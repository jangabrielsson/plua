"""
FastAPI REST API server for plua2
Provides HTTP endpoints to interact with the Lua runtime
"""

import asyncio
import uuid
import socket
import psutil
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from .runtime import LuaAsyncRuntime
from .fibaro_api_endpoints import create_fibaro_api_routes, set_interpreter


@dataclass
class ExecutionRequest:
    """Request to execute Lua code"""
    request_id: str
    lua_code: str
    timeout: float = 30.0


@dataclass
class ExecutionResponse:
    """Response from Lua execution"""
    request_id: str
    success: bool
    result: Any = None
    output: str = ""
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class LuaExecuteRequest(BaseModel):
    """Pydantic model for POST /plua/execute"""
    code: str
    timeout: float = 30.0


class LuaExecuteResponse(BaseModel):
    """Pydantic model for execution response"""
    success: bool
    result: Any = None
    output: str = ""
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    request_id: str


class PlUA2APIServer:
    """
    FastAPI server that communicates with plua2 runtime via message queues
    """

    def __init__(self, runtime: LuaAsyncRuntime, host: str = "0.0.0.0", port: int = 8888):
        self.runtime = runtime
        self.host = host
        self.port = port

        # Tracking variables for status
        self.start_time = time.time()
        self.executed_scripts_count = 0
        self.fibaro_endpoints_loaded = False

        # Store pending execution requests
        self.pending_requests: Dict[str, asyncio.Future] = {}

        # WebSocket connections for real-time UI updates
        self.websocket_connections: set[WebSocket] = set()

        # Clean up the port if it's in use
        if not is_port_free(port, host):
            print(f"Port {port} is in use, attempting cleanup...")
            if not cleanup_port(port, host):
                raise RuntimeError(f"Failed to free port {port}. Please manually stop any processes using this port.")

        # FastAPI app
        self.app = FastAPI(
            title="plua2 REST API",
            description="REST API for executing Lua code in plua2 runtime",
            version="1.0.0"
        )

        # Add CORS middleware for browser access
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure as needed for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
            max_age=3600,
        )

        # Mount static files directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        static_dir = os.path.join(project_root, "static")
        if os.path.exists(static_dir):
            self.app.mount("/static", StaticFiles(directory=static_dir), name="static")

        self._setup_routes()

    def _call_fibaro_api_hook(self, method: str, path: str, data: Any = None):
        """Call the Fibaro API hook if available"""
        try:
            # Get the Fibaro API hook from Lua runtime
            lua = self.runtime.interpreter.get_lua_runtime()
            if not lua:
                return None

            fibaro_hook = self.runtime.interpreter.PY.fibaro_api_hook
            if not fibaro_hook:
                return None

            # Call the Lua handler function
            response_data, status_code = fibaro_hook(method, path, data)
            return response_data, status_code

        except Exception as e:
            print(f"Error calling Fibaro API hook: {e}")
            return None

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/")
        async def root():
            return {
                "message": "plua2 REST API Server",
                "version": "1.0.0",
                "web_interface": "/web",
                "api_docs": "/docs",
                "endpoints": {
                    "web": "GET /web - Web REPL interface",
                    "execute": "POST /plua/execute - Execute Lua code",
                    "status": "GET /plua/status - Get runtime status",
                    "info": "GET /plua/info - Get API information"
                }
            }

        @self.app.get("/web", response_class=HTMLResponse)
        async def web_repl():
            """Serve the Main Web Interface with tabs"""
            # Find the HTML file relative to this script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to src/plua2 -> src -> project root
            project_root = os.path.dirname(os.path.dirname(current_dir))
            html_path = os.path.join(project_root, "static", "plua2_main_page.html")

            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                return HTMLResponse(content=html_content)
            except FileNotFoundError:
                # Fallback to dev directory
                html_path = os.path.join(project_root, "dev", "plua2_web_repl.html")
                try:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    return HTMLResponse(content=html_content)
                except FileNotFoundError:
                    raise HTTPException(status_code=404, detail="Web interface not found")

        @self.app.get("/plua/info")
        async def info():
            """Get API and runtime information"""
            try:
                state = self.runtime.interpreter.get_runtime_state()
                return {
                    "api_version": "1.0.0",
                    "runtime_active": True,
                    "lua_version": "5.4",
                    "runtime_state": state,
                    "features": ["timers", "networking", "json", "callbacks"]
                }
            except Exception as e:
                return {
                    "api_version": "1.0.0",
                    "runtime_active": False,
                    "error": str(e)
                }

        @self.app.get("/plua/status")
        async def status():
            """Get current runtime status"""
            try:
                state = self.runtime.interpreter.get_runtime_state()
                return {
                    "status": "running",
                    "active_timers": state["active_timers"],
                    "pending_callbacks": state["pending_callbacks"],
                    "total_tasks": state["total_tasks"],
                    "api_requests_pending": len(self.pending_requests)
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get status: {e}")

        @self.app.get("/plua/state")
        async def state():
            """Get detailed runtime state information"""
            try:
                state = self.runtime.interpreter.get_runtime_state()
                return {
                    "task_info": state.get("task_info", {}),
                    "active_timers": state.get("active_timers", 0),
                    "pending_callbacks": state.get("pending_callbacks", 0),
                    "total_tasks": state.get("total_tasks", 0),
                    "api_requests_pending": len(self.pending_requests),
                    "runtime_info": {
                        "lua_version": "5.4",
                        "features": ["timers", "networking", "json", "callbacks"],
                        "initialized": True
                    }
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get state: {e}")

        @self.app.post("/plua/execute", response_model=LuaExecuteResponse)
        async def execute_lua(request: LuaExecuteRequest):
            """Execute Lua code and return result"""
            request_id = str(uuid.uuid4())

            try:
                # Execute Lua code directly in the same event loop
                response = await self._execute_lua_code_async(request.code, request_id, request.timeout)

                # If execution failed due to syntax error, return 400
                if not response.success and response.error and ("syntax error" in response.error.lower() or "invalid" in response.error.lower()):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Lua syntax error: {response.error}"
                    )

                return LuaExecuteResponse(
                    success=response.success,
                    result=response.result,
                    output=response.output,
                    error=response.error,
                    execution_time_ms=response.execution_time_ms,
                    request_id=response.request_id
                )

            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=408,
                    detail=f"Lua execution timed out after {request.timeout} seconds"
                )
            except HTTPException:
                # Re-raise HTTP exceptions (like our 400 above)
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Execution failed: {e}")

        # Fibaro API delegation endpoint
        async def fibaro_api_handler(method: str, path: str, request_data: dict = None):
            """
            Handle Fibaro API requests by delegating to Lua fibaro_api_hook

            Args:
                method: HTTP method (GET, POST, PUT, DELETE, etc.)
                path: API path (e.g., "/devices/123")
                request_data: Request data (JSON body, query params, etc.)

            Returns:
                Tuple of (response_data, status_code)
            """
            if not self.runtime.interpreter.PY.fibaro_api_hook:
                raise HTTPException(status_code=501, detail="Fibaro API not implemented")

            try:
                # Call the Lua fibaro_api_hook function
                response_data, status_code = self.runtime.interpreter.PY.fibaro_api_hook(method, path, request_data or {})
                return response_data, status_code
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Fibaro API error: {e}")

        # Store the handler for use in Fibaro endpoints
        self._fibaro_api_handler = fibaro_api_handler

        # WebSocket endpoint for real-time UI updates
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time UI updates"""
            await websocket.accept()
            self.websocket_connections.add(websocket)
            print(f"[WEBSOCKET DEBUG] Client connected. Total connections: {len(self.websocket_connections)}")

            try:
                while True:
                    # Keep connection alive by receiving messages
                    await websocket.receive_text()
            except WebSocketDisconnect:
                print("[WEBSOCKET DEBUG] Client disconnected")
            except Exception as e:
                print(f"[WEBSOCKET DEBUG] WebSocket error: {e}")
            finally:
                self.websocket_connections.discard(websocket)
                print(f"[WEBSOCKET DEBUG] Client removed. Total connections: {len(self.websocket_connections)}")

    async def broadcast_ui_update(self, qa_id: int):
        """
        Broadcast UI update to all connected WebSocket clients

        Args:
            qa_id: QuickApp ID that was updated
        """
        print(f"[BROADCAST DEBUG] Starting broadcast for QA {qa_id}")
        print(f"[BROADCAST DEBUG] WebSocket connections: {len(self.websocket_connections)}")

        if not self.websocket_connections:
            print("[BROADCAST DEBUG] No WebSocket connections, broadcast aborted")
            return

        # Get the updated QuickApp data
        try:
            print(f"[BROADCAST DEBUG] Getting QuickApp data for {qa_id}")
            result = self.runtime.interpreter.lua.eval(f"_PY.get_quickapp({qa_id})")
            if result:
                # Convert to JSON string if it's a table
                if hasattr(result, 'items') or hasattr(result, '__iter__'):
                    qa_data = self.runtime.interpreter.lua.eval(f'json.encode(_PY.get_quickapp({qa_id}))')
                else:
                    qa_data = result

                message = {
                    "type": "ui_update",
                    "qa_id": qa_id,
                    "data": qa_data
                }

                print(f"[BROADCAST DEBUG] Sending message to {len(self.websocket_connections)} clients")
                print(f"[BROADCAST DEBUG] Message: {str(message)[:200]}...")

                # Send to all connected clients
                disconnected = set()
                sent_count = 0
                for websocket in self.websocket_connections:
                    try:
                        import json
                        await websocket.send_text(json.dumps(message))
                        sent_count += 1
                        print(f"[BROADCAST DEBUG] Sent to client {sent_count}")
                    except Exception as e:
                        print(f"[BROADCAST DEBUG] Failed to send to client: {e}")
                        # Connection is broken, mark for removal
                        disconnected.add(websocket)

                # Clean up disconnected clients
                self.websocket_connections -= disconnected
                print(f"[BROADCAST DEBUG] Successfully sent to {sent_count} clients, removed {len(disconnected)} disconnected")

            else:
                print(f"[BROADCAST DEBUG] No QuickApp data found for {qa_id}")

        except Exception as e:
            print(f"[BROADCAST DEBUG] Error broadcasting UI update for QA {qa_id}: {e}")
            import traceback
            traceback.print_exc()

    async def broadcast_view_update(self, qa_id: int, component_name: str, property_name: str, value):
        """
        Broadcast granular view update to all connected WebSocket clients
        
        Args:
            qa_id: QuickApp ID
            component_name: UI component that was updated (e.g., "lbl1", "button1") 
            property_name: Property that changed (e.g., "text", "value")
            value: The new value for the property
        """
        if not self.websocket_connections:
            return

        try:
            message = {
                "type": "view_update",
                "qa_id": qa_id,
                "element_id": component_name,
                "property": property_name,
                "value": value
            }

            # Send to all connected clients
            import json
            disconnected = set()
            for websocket in self.websocket_connections:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    disconnected.add(websocket)

            # Clean up disconnected clients
            self.websocket_connections -= disconnected

        except Exception as e:
            print(f"Error broadcasting view update for QA {qa_id}: {e}")

    def register_fibaro_endpoints(self):
        """
        Register Fibaro API endpoints that delegate to Lua fibaro_api_hook
        Always registers endpoints - the hook implementation determines functionality
        """
        # Set the interpreter for the auto-generated endpoints
        set_interpreter(self.runtime.interpreter)

        # Create all auto-generated Fibaro API routes
        create_fibaro_api_routes(self.app)

        # Mark that Fibaro endpoints are loaded
        self.fibaro_endpoints_loaded = True

    def check_and_register_fibaro_api(self):
        """
        Always register Fibaro API endpoints - no conditional checking needed
        The hook implementation will determine if Fibaro functionality is available
        """
        if not self.fibaro_endpoints_loaded:
            self.register_fibaro_endpoints()

    async def _execute_lua_code_async(self, lua_code: str, request_id: str, timeout: float = 30.0) -> ExecutionResponse:
        """Execute Lua code directly in the main event loop and capture output/result"""
        start_time = datetime.now()

        try:
            # Get the Lua runtime from interpreter
            lua = self.runtime.interpreter.get_lua_runtime()
            if not lua:
                raise RuntimeError("Lua runtime not available")

            # Execute user code with proper error handling and output capture
            result = None
            success = True
            error_msg = None
            output = ""

            # Clear output buffer before execution
            self.runtime.interpreter.clear_output_buffer()

            # Set web mode to prevent ANSI conversion
            self.runtime.interpreter.set_web_mode(True)

            try:
                # Execute with timeout but in the main event loop
                async def execute_lua():
                    """Execute Lua code in the main event loop"""
                    try:
                        # Try to execute as an expression first (for simple values)
                        try:
                            result = lua.execute(f"return ({lua_code})")
                        except Exception:  # noqa: E722
                            # If that fails, execute as statements
                            result = lua.execute(lua_code)

                        return result
                    except Exception as e:
                        raise e

                # Execute with timeout in the main event loop
                result = await asyncio.wait_for(execute_lua(), timeout=timeout)

                # Get captured output from buffer
                output = self.runtime.interpreter.get_output_buffer()

            except asyncio.TimeoutError:
                success = False
                error_msg = f"Execution timed out after {timeout} seconds"
                # Try to get any output that was captured before timeout
                output = self.runtime.interpreter.get_output_buffer()
            except Exception as e:
                success = False
                error_msg = str(e)
                # Try to get any output that was captured before error
                output = self.runtime.interpreter.get_output_buffer()
            finally:
                # Reset web mode
                self.runtime.interpreter.set_web_mode(False)

            # Calculate execution time
            end_time = datetime.now()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            return ExecutionResponse(
                request_id=request_id,
                success=success,
                result=result,
                output=output,
                error=error_msg,
                execution_time_ms=execution_time_ms
            )

        except Exception as e:
            end_time = datetime.now()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            return ExecutionResponse(
                request_id=request_id,
                success=False,
                error=f"API execution error: {e}",
                execution_time_ms=execution_time_ms
            )

    async def start_server(self):
        """Start the FastAPI server"""
        # Check and register Fibaro endpoints if available
        self.check_and_register_fibaro_api()

        # Configure uvicorn with proper shutdown handling
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="warning",  # Suppress INFO logs
            # Disable lifespan events to prevent cancellation errors
            lifespan="off"
        )

        server = uvicorn.Server(config)

        try:
            await server.serve()
        except asyncio.CancelledError:
            # Graceful shutdown - the server will handle this cleanly
            # No need for additional cleanup since lifespan is disabled
            raise

    def stop(self):
        """Stop the server and cleanup"""
        # Cleanup any pending requests
        for future in self.pending_requests.values():
            if not future.done():
                future.cancel()


def cleanup_port(port: int, host: str = "0.0.0.0") -> bool:
    """
    Platform-independent function to forcefully close processes using a specific port

    Args:
        port: Port number to clean up
        host: Host address (default: 0.0.0.0 for all interfaces)

    Returns:
        bool: True if cleanup was successful, False otherwise
    """
    try:
        # First, try to check if the port is actually in use
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host if host != "0.0.0.0" else "127.0.0.1", port))
        sock.close()

        if result != 0:
            # Port is not in use
            return True

        print(f"Port {port} is in use, attempting to free it...")

        # Find processes using the port
        killed_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Get connections for this process
                connections = proc.connections()
                if connections:
                    for conn in connections:
                        if (hasattr(conn, 'laddr') and conn.laddr.port == port and conn.status == psutil.CONN_LISTEN):
                            pid = proc.info['pid']
                            name = proc.info['name']

                            print(f"Found process using port {port}: {name} (PID: {pid})")

                            # Try to terminate gracefully first
                            try:
                                process = psutil.Process(pid)
                                process.terminate()

                                # Wait a bit for graceful termination
                                time.sleep(0.5)

                                if process.is_running():
                                    # Force kill if still running
                                    print(f"Force killing process {pid}")
                                    process.kill()

                                killed_processes.append(f"{name} (PID: {pid})")

                            except psutil.AccessDenied:
                                print(f"Access denied when trying to kill process {pid}")
                                return False
                            except psutil.NoSuchProcess:
                                # Process already gone
                                pass
                            except Exception as e:
                                print(f"Error killing process {pid}: {e}")
                                return False

            except (psutil.AccessDenied, psutil.NoSuchProcess):
                # Skip processes we can't access
                continue
            except Exception:  # noqa: E722
                # Skip any other errors with individual processes
                continue

        if killed_processes:
            print(f"Killed processes: {', '.join(killed_processes)}")
            # Give the OS time to clean up
            time.sleep(1)

        # Verify the port is now free
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host if host != "0.0.0.0" else "127.0.0.1", port))
        sock.close()

        if result == 0:
            print(f"Warning: Port {port} is still in use after cleanup attempt")
            return False
        else:
            print(f"Port {port} is now free")
            return True

    except Exception as e:
        print(f"Error during port cleanup: {e}")
        return False


def is_port_free(port: int, host: str = "0.0.0.0") -> bool:
    """
    Check if a port is free

    Args:
        port: Port number to check
        host: Host address to check

    Returns:
        bool: True if port is free, False if in use
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host if host != "0.0.0.0" else "127.0.0.1", port))
        sock.close()
        return result != 0
    except Exception:  # noqa: E722
        return False


async def run_api_server(runtime: LuaAsyncRuntime, host: str = "0.0.0.0", port: int = 8888):
    """Convenience function to run the API server"""
    server = PlUA2APIServer(runtime, host, port)
    await server.start_server()


def cleanup_port_cli(port: int, host: str = "0.0.0.0"):
    """
    Command-line interface for port cleanup
    """
    print(f"Cleaning up port {port} on {host}...")

    if is_port_free(port, host):
        print(f"Port {port} is already free")
        return True

    success = cleanup_port(port, host)
    if success:
        print(f"Successfully cleaned up port {port}")
    else:
        print(f"Failed to clean up port {port}")

    return success
