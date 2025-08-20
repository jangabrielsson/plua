"""
FastAPI Server Process for PLua
Runs FastAPI in a separate process and communicates with the main Lua engine via IPC
This eliminates asyncio event loop conflicts and provides a stable web server
"""

import asyncio
import json
import logging
import platform
import queue
import time
import uuid
from typing import Dict, Any, Optional, Union

# Platform-specific imports
if platform.system() == "Windows":
    # On Windows, use threading queues since we use threading instead of multiprocessing
    QueueType = queue.Queue
else:
    # On Unix/Linux, use multiprocessing queues
    import multiprocessing
    QueueType = multiprocessing.Queue

# Set multiprocessing start method for Windows to avoid spawn issues
if platform.system() == "Windows":
    try:
        # Import multiprocessing only if needed for configuration
        import multiprocessing
        # Try to use fork method if available, otherwise stick with spawn
        import sys
        if hasattr(sys, 'set_int_max_str_digits'):  # Python 3.11+
            # Use a more aggressive approach - disable multiprocessing entirely on Windows
            # and fall back to threading for better exit handling
            multiprocessing.set_start_method('spawn', force=True)
        else:
            multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass  # Method already set

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

logger = logging.getLogger(__name__)


class LuaExecuteRequest(BaseModel):
    """Pydantic model for POST /plua/execute"""
    code: str
    timeout: float = 30.0


class LuaExecuteResponse(BaseModel):
    """Pydantic model for execute response"""
    success: bool
    result: Any = None
    output: str = ""
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class IPCMessage(BaseModel):
    """Message format for IPC communication"""
    id: str
    type: str  # "execute", "fibaro_api", "response"
    data: Dict[str, Any]
    timestamp: float


def create_fastapi_app(request_queue: Union[queue.Queue, 'multiprocessing.Queue'], response_queue: Union[queue.Queue, 'multiprocessing.Queue'], broadcast_queue: Union[queue.Queue, 'multiprocessing.Queue'], config: Dict[str, Any]) -> FastAPI:
    """Create the FastAPI application with IPC communication"""
    
    app = FastAPI(
        title="PLua API Server", 
        description="REST API for PLua Lua Runtime with Web UI support (Multi-Process)",
        version="2.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files for QuickApp UI
    import os
    import sys
    
    # Find static directory - handle both development and Nuitka builds
    static_dir = None
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "static"),  # Development mode
        os.path.join(os.path.dirname(sys.executable), "static"),  # Nuitka build
        os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "static"),  # Alternative Nuitka path
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            static_dir = path
            break
    
    if static_dir and os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info(f"📁 Static files mounted from: {static_dir}")
    else:
        logger.warning(f"⚠️ Static directory not found. Tried: {possible_paths}")
    
    # Server statistics
    start_time = time.time()
    request_count = 0
    
    # Helper function to send IPC request and wait for response
    async def send_ipc_request(message_type: str, data: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
        """Send an IPC request and wait for response"""
        nonlocal request_count
        request_count += 1
        
        message_id = str(uuid.uuid4())
        message = IPCMessage(
            id=message_id,
            type=message_type,
            data=data,
            timestamp=time.time()
        )
        
        try:
            # Send request to main process
            request_queue.put(message.dict(), timeout=1.0)
            
            # Wait for response
            start_wait = time.time()
            while time.time() - start_wait < timeout:
                try:
                    response_data = response_queue.get(timeout=0.1)
                    if response_data.get("id") == message_id:
                        return response_data.get("data", {})
                except queue.Empty:
                    continue
                    
            return {"success": False, "error": f"IPC timeout after {timeout} seconds"}
            
        except Exception as e:
            return {"success": False, "error": f"IPC error: {str(e)}"}
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        uptime = time.time() - start_time
        return {
            "status": "healthy",
            "uptime_seconds": uptime,
            "requests_served": request_count,
            "mode": "multi-process",
            "lua_engine": "connected via IPC",
            "fibaro_api": "available (hook-based)"
        }
        
    # Main page
    @app.get("/", response_class=HTMLResponse)
    async def root():
        uptime = time.time() - start_time
        status_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PLua API Server (Multi-Process)</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .status {{ background: #e8f5e8; padding: 20px; border-radius: 5px; }}
                .info {{ margin: 10px 0; }}
                .multiprocess {{ background: #f0f8ff; border-left: 4px solid #0066cc; padding: 10px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>🚀 PLua API Server</h1>
            <div class="multiprocess">
                <strong>🔄 Multi-Process Architecture</strong><br>
                This FastAPI server runs in a separate process from the Lua engine,
                providing maximum stability and avoiding event loop conflicts.
            </div>
            <div class="status">
                <div class="info"><strong>Status:</strong> Running</div>
                <div class="info"><strong>Uptime:</strong> {uptime:.1f} seconds</div>
                <div class="info"><strong>Requests Served:</strong> {request_count}</div>
                <div class="info"><strong>Architecture:</strong> Multi-Process</div>
                <div class="info"><strong>Lua Engine:</strong> ✅ Connected via IPC</div>
                <div class="info"><strong>Fibaro API:</strong> ✅ Available (hook-based)</div>
            </div>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/health">GET /health</a> - Health check</li>
                <li>POST /plua/execute - Execute Lua code</li>
                <li>GET/POST/PUT/DELETE /api/* - Fibaro API endpoints (if enabled)</li>
                <li><a href="/docs">GET /docs</a> - API Documentation</li>
            </ul>
        </body>
        </html>
        """
        return status_html
        
    # Lua execution endpoint
    @app.post("/plua/execute", response_model=LuaExecuteResponse)
    async def execute_lua(request: LuaExecuteRequest):
        """Execute Lua code via IPC"""
        start_time = time.time()
        
        # Send execution request via IPC
        result = await send_ipc_request(
            "execute",
            {
                "code": request.code,
                "timeout": request.timeout
            },
            timeout=request.timeout + 5.0  # Add buffer for IPC overhead
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        return LuaExecuteResponse(
            success=result.get("success", False),
            result=result.get("result"),
            output=result.get("output", ""),
            error=result.get("error"),
            execution_time_ms=execution_time
        )
    
    # Fibaro API endpoints - always available, hook determines response
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def fibaro_api(request: Request, path: str):
        """Handle Fibaro API requests via IPC - always call the hook"""
        method = request.method
        body_data = None
        
        if method in ["POST", "PUT"] and await request.body():
            try:
                body_data = await request.json()
            except Exception:
                body_data = None
                
        # Always send fibaro request via IPC - hook will handle it
        result = await send_ipc_request(
            "fibaro_api",
            {
                "method": method,
                "path": f"/api/{path}",
                "data": body_data
            },
            timeout=30.0
        )
        
        # Handle hook response
        if result.get("success", False):
            hook_result = result.get("data")
            status_code = result.get("status_code", 200)
            
            # If hook returned a non-200 status code, return error
            if status_code != 200:
                error_msg = hook_result if isinstance(hook_result, str) else f"Fibaro API unavailable"
                raise HTTPException(status_code=status_code, detail=error_msg)
                
            return hook_result
        else:
            # IPC failed
            status_code = result.get("status_code", 500)
            error_msg = result.get("error", "Fibaro API hook error")
            raise HTTPException(status_code=status_code, detail=error_msg)
    
        # QuickApp endpoints for UI structure and device data
    @app.get("/plua/quickApp/{qa_id}/info")
    async def get_quickapp_info(qa_id: int):
        """Get QuickApp UI structure and device data"""
        logger.info(f"📱 QuickApp info requested for ID: {qa_id}")
        
        # Get QuickApp data from Lua engine via IPC
        result = await send_ipc_request(
            "quickapp_info",
            {"qa_id": qa_id},
            timeout=10.0
        )
        
        if result.get("success", False):
            return result.get("data")
        else:
            error_msg = result.get("error", f"QuickApp {qa_id} not found")
            raise HTTPException(status_code=404, detail=error_msg)
    
    @app.get("/plua/quickApp/info")
    async def get_all_quickapps_info():
        """Get all QuickApps UI structures and device data"""
        logger.info("📱 All QuickApps info requested")
        
        # Get all QuickApps data from Lua engine via IPC
        result = await send_ipc_request(
            "all_quickapps_info",
            {},
            timeout=10.0
        )
        
        if result.get("success", False):
            return result.get("data", [])
        else:
            error_msg = result.get("error", "Failed to get QuickApps info")
            raise HTTPException(status_code=500, detail=error_msg)
    
    # WebSocket management - define connections set and message buffer at function level
    websocket_connections = set()
    pending_broadcasts = []  # Buffer for messages when no connections are available
    
    async def broadcast_to_websockets(qa_id: int, element_id: str, property_name: str, value):
        """Broadcast a view update to all connected WebSocket clients"""
        # Access websocket_connections from app.state to avoid scope issues
        connections = getattr(app.state, 'websocket_connections', set())
        
        message = {
            "type": "view_update",
            "qa_id": qa_id,
            "element_id": element_id,
            "property_name": property_name,
            "value": value
        }
        
        if not connections:
            # Buffer the message for later delivery
            pending_broadcasts.append(message)
            logger.debug(f"Buffered WebSocket message (total: {len(pending_broadcasts)})")
            return
        
        # Send message to all connected clients
        disconnected = set()
        for websocket in connections.copy():  # Use copy to avoid modification during iteration
            try:
                # Check if WebSocket is still connected before sending
                if websocket.client_state.name != "CONNECTED":
                    disconnected.add(websocket)
                    continue
                await websocket.send_json(message)
            except Exception as e:
                logger.debug(f"Failed to send to WebSocket client: {e}")  # Reduced to debug level
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        connections -= disconnected
        # Update app.state if needed
        if hasattr(app.state, 'websocket_connections'):
            app.state.websocket_connections -= disconnected
    
    async def flush_pending_broadcasts():
        """Send all pending broadcasts to newly connected WebSocket clients"""
        if not pending_broadcasts:
            return
            
        connections = getattr(app.state, 'websocket_connections', set())
        if not connections:
            return
            
        logger.info(f"Flushing {len(pending_broadcasts)} pending broadcasts")
        
        # Send all buffered messages
        for message in pending_broadcasts:
            disconnected = set()
            for websocket in connections.copy():  # Use copy to avoid modification during iteration
                try:
                    # Check if WebSocket is still connected before sending
                    if websocket.client_state.name != "CONNECTED":
                        disconnected.add(websocket)
                        continue
                    await websocket.send_json(message)
                except Exception as e:
                    logger.debug(f"Failed to send buffered message: {e}")  # Reduced to debug level
                    disconnected.add(websocket)
            
            # Clean up disconnected clients
            connections -= disconnected
            # Update app.state if needed
            if hasattr(app.state, 'websocket_connections'):
                app.state.websocket_connections -= disconnected
        
        # Clear the buffer after successful delivery
        pending_broadcasts.clear()
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time UI updates"""
        try:
            await websocket.accept()
            websocket_connections.add(websocket)
            # Also add to app.state for consistency
            if not hasattr(app.state, 'websocket_connections'):
                app.state.websocket_connections = set()
            app.state.websocket_connections.add(websocket)
            
            logger.info(f"WebSocket connection accepted. Total connections: {len(websocket_connections)}")
            
            # Small delay to ensure connection is fully established
            await asyncio.sleep(0.1)
            
            # Flush any pending broadcasts to the new connection
            if pending_broadcasts:
                await flush_pending_broadcasts()
            
            try:
                while True:
                    # Keep connection alive by receiving messages
                    await websocket.receive_text()
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected normally")
            except Exception as e:
                logger.debug(f"WebSocket error during communication: {e}")
        except Exception as e:
            logger.debug(f"WebSocket connection error: {e}")
        finally:
            # Clean up the connection
            websocket_connections.discard(websocket)
            if hasattr(app.state, 'websocket_connections'):
                app.state.websocket_connections.discard(websocket)
            logger.info(f"WebSocket connection removed. Total connections: {len(websocket_connections)}")
    
    # Store the broadcast function and connections in app state for access from background task
    app.state.websocket_connections = websocket_connections
    app.state.broadcast_to_websockets = broadcast_to_websockets
    app.state.pending_broadcasts = pending_broadcasts
    
    # Shutdown event to signal background tasks to stop
    shutdown_event = asyncio.Event()
    
    # Background task to process WebSocket broadcasts from the request queue
    @app.on_event("startup")
    async def startup_event():
        """Initialize background tasks"""
        logger.info("🚀 FastAPI startup event called!")
        
        async def process_websocket_broadcasts():
            """Process broadcast requests from the broadcast queue"""
            logger.info("📥 Broadcast processor starting...")
            
            while not shutdown_event.is_set():
                try:
                    # Check for broadcast requests in the broadcast queue (non-blocking)
                    try:
                        message = broadcast_queue.get_nowait()
                        
                        if isinstance(message, dict) and message.get("type") == "websocket_broadcast":
                            # Handle broadcast request directly
                            data = message.get("data", {})
                            qa_id = data.get("qa_id")
                            element_id = data.get("element_id")
                            property_name = data.get("property_name")
                            value = data.get("value")
                            
                            # Use the broadcast function from app state
                            if hasattr(app.state, 'broadcast_to_websockets'):
                                await app.state.broadcast_to_websockets(qa_id, element_id, property_name, value)
                            else:
                                logger.warning("broadcast_to_websockets function not found in app.state")
                            
                    except queue.Empty:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error processing broadcast request: {e}")
                
                # Small delay to avoid busy waiting, but check shutdown frequently
                try:
                    await asyncio.wait_for(shutdown_event.wait(), timeout=0.01)
                    break  # Shutdown signal received
                except asyncio.TimeoutError:
                    pass  # Continue processing
            
            logger.info("📥 Broadcast processor stopping...")
        
        # Start the broadcast processor
        logger.info("🔄 Starting broadcast processor task...")
        asyncio.create_task(process_websocket_broadcasts())
        logger.info("🔄 Queue broadcast processor started")
    
    @app.on_event("shutdown")
    async def shutdown_event_handler():
        """Signal background tasks to shutdown"""
        shutdown_event.set()

    
    return app


def run_fastapi_server(request_queue: Union[queue.Queue, 'multiprocessing.Queue'], response_queue: Union[queue.Queue, 'multiprocessing.Queue'], broadcast_queue: Union[queue.Queue, 'multiprocessing.Queue'], config: Dict[str, Any]):
    """Run the FastAPI server in a separate process"""
    import sys
    import os
    
    # On Windows, suppress stderr to avoid multiprocessing spawn errors
    if platform.system() == "Windows":
        try:
            # Redirect stderr to null to suppress spawn errors
            sys.stderr = open(os.devnull, 'w')
        except Exception:
            pass
    
    # Set up logging for the server process
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("fastapi_process")
    logger.info(f"Starting FastAPI server process on {config['host']}:{config['port']}")
    
    try:
        # Create the FastAPI app
        app = create_fastapi_app(request_queue, response_queue, broadcast_queue, config)
        
        # Determine uvicorn log level based on PLua config
        plua_log_level = config.get("loglevel", "INFO").upper()
        if plua_log_level in ["CRITICAL", "ERROR"]:
            uvicorn_log_level = "error"
        elif plua_log_level == "WARNING":
            uvicorn_log_level = "warning"  
        elif plua_log_level == "INFO":
            uvicorn_log_level = "error"  # Hide uvicorn startup messages unless explicitly requested
        else:  # DEBUG
            uvicorn_log_level = "info"
        
        # Run with uvicorn
        uvicorn.run(
            app,
            host=config.get("host", "localhost"),
            port=config.get("port", 8080),
            log_level=uvicorn_log_level,
            access_log=False
        )
        
    except Exception as e:
        logger.error(f"FastAPI server process error: {e}")
    finally:
        logger.info("FastAPI server process stopped")


class FastAPIProcessManager:
    """Manages the FastAPI server process and IPC communication"""
    
    def __init__(self, host: str = "localhost", port: int = 8080, config: Dict[str, Any] = None):
        self.host = host
        self.port = port
        self.config = config or {}
        self.config.update({"host": host, "port": port})
        
        # IPC queues
        self.request_queue = QueueType()
        self.response_queue = QueueType()
        self.broadcast_queue = QueueType()  # Separate queue for WebSocket broadcasts
        
        # Process management
        self.server_process: Optional[multiprocessing.Process] = None
        self.running = False
        
        # Callbacks
        self.lua_executor: Optional[callable] = None
        self.fibaro_callback: Optional[callable] = None
        self.quickapp_callback: Optional[callable] = None
        
    def set_lua_executor(self, executor: callable):
        """Set the Lua code executor function"""
        self.lua_executor = executor
        logger.info("Lua executor set for FastAPI process")
        
    def set_fibaro_callback(self, callback: callable):
        """Set the Fibaro API callback function"""
        self.fibaro_callback = callback
        logger.info("Fibaro API callback set for FastAPI process")
        
    def set_quickapp_callback(self, callback: callable):
        """Set the QuickApp data callback function"""
        self.quickapp_callback = callback
        logger.info("QuickApp callback set for FastAPI process")
        
    def _convert_lua_objects(self, obj):
        """Convert LuaTable objects to Python objects to avoid pickle errors"""
        if hasattr(obj, '__class__') and 'LuaTable' in str(obj.__class__):
            # Import here to avoid circular imports
            try:
                from .lua_bindings import lua_to_python_table
                return lua_to_python_table(obj)
            except ImportError:
                # Fallback: convert manually if import fails
                result = {}
                try:
                    for key, value in obj.items():
                        python_key = self._convert_lua_objects(key)
                        python_value = self._convert_lua_objects(value)
                        result[python_key] = python_value
                    return result
                except Exception:
                    # If all else fails, return string representation
                    return str(obj)
        elif isinstance(obj, (list, tuple)):
            return [self._convert_lua_objects(item) for item in obj]
        elif isinstance(obj, dict):
            return {self._convert_lua_objects(k): self._convert_lua_objects(v) for k, v in obj.items()}
        else:
            return obj
        
    def start(self):
        """Start the FastAPI server process"""
        if self.running:
            logger.warning("FastAPI process already running")
            return
            
        logger.info(f"Starting FastAPI server process on {self.host}:{self.port}")
        
        # Start the server process with Windows-specific handling
        if platform.system() == "Windows":
            # On Windows, use threading instead of multiprocessing to avoid spawn issues
            import threading
            import asyncio
            
            def run_in_thread():
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Create the FastAPI app
                    app = create_fastapi_app(self.request_queue, self.response_queue, self.broadcast_queue, self.config)
                    
                    # Determine uvicorn log level based on PLua config
                    plua_log_level = self.config.get("loglevel", "INFO").upper()
                    if plua_log_level in ["CRITICAL", "ERROR"]:
                        uvicorn_log_level = "error"
                    elif plua_log_level == "WARNING":
                        uvicorn_log_level = "warning"  
                    elif plua_log_level == "INFO":
                        uvicorn_log_level = "error"  # Hide uvicorn startup messages unless explicitly requested
                    else:  # DEBUG
                        uvicorn_log_level = "info"
                    
                    # Run with uvicorn
                    import uvicorn
                    uvicorn.run(
                        app,
                        host=self.host,
                        port=self.port,
                        log_level=uvicorn_log_level,
                        access_log=False
                    )
                except Exception as e:
                    logger.error(f"FastAPI thread error: {e}")
                finally:
                    loop.close()
            
            # Start FastAPI in a daemon thread on Windows
            self.server_thread = threading.Thread(target=run_in_thread, daemon=True)
            self.server_thread.start()
            self.server_process = None  # No process on Windows, using thread
            logger.info("FastAPI started in thread mode on Windows")
        else:
            # Unix/Linux - use multiprocessing as before
            self.server_process = multiprocessing.Process(
                target=run_fastapi_server,
                args=(self.request_queue, self.response_queue, self.broadcast_queue, self.config),
                daemon=True
            )
            self.server_process.start()
            logger.info(f"FastAPI process started with PID {self.server_process.pid}")
        
        self.running = True
        
        # Start IPC message handler in a thread
        import threading
        self.ipc_thread = threading.Thread(target=self._handle_ipc_messages, daemon=True)
        self.ipc_thread.start()
        
        logger.info("FastAPI server started successfully")
        
    def stop(self):
        """Stop the FastAPI server process/thread"""
        if not self.running:
            return
            
        logger.info("Stopping FastAPI server...")
        self.running = False
        
        if platform.system() == "Windows":
            # On Windows, we're using threading - daemon threads will die with main process
            if hasattr(self, 'server_thread') and self.server_thread.is_alive():
                logger.info("FastAPI thread will terminate with main process")
        else:
            # Unix/Linux - stop the process
            if self.server_process and self.server_process.is_alive():
                self.server_process.terminate()
                self.server_process.join(timeout=5)
                
                if self.server_process.is_alive():
                    logger.warning("Force killing FastAPI process")
                    self.server_process.kill()
                
        logger.info("FastAPI server process stopped")
        
    def _handle_ipc_messages(self):
        """Handle IPC messages from the FastAPI process"""
        logger.info("IPC message handler started")
        
        while self.running:
            try:
                # Get message from FastAPI process
                message_data = self.request_queue.get(timeout=1.0)
                message = IPCMessage(**message_data)
                
                # Process the message
                response_data = None
                
                if message.type == "execute" and self.lua_executor:
                    # Execute Lua code
                    data = message.data
                    try:
                        result = self.lua_executor(data["code"], data.get("timeout", 30.0))
                        response_data = {"success": True, **result}
                    except Exception as e:
                        response_data = {"success": False, "error": str(e)}
                        
                elif message.type == "fibaro_api":
                    # Always handle Fibaro API call - hook will determine response
                    data = message.data
                    try:
                        if self.fibaro_callback:
                            # Call the hook function
                            hook_result, status_code = self.fibaro_callback(
                                data["method"], 
                                data["path"], 
                                json.dumps(data["data"]) if data["data"] else None
                            )
                            
                            # Handle the hook response - pass through status code
                            if status_code == 200:
                                response_data = {
                                    "success": True, 
                                    "data": hook_result,
                                    "status_code": 200
                                }
                            else:
                                # Non-200 status code - this will trigger HTTPException in FastAPI
                                response_data = {
                                    "success": True,  # IPC succeeded 
                                    "data": hook_result,
                                    "status_code": status_code
                                }
                        else:
                            # No callback set - this shouldn't happen but handle gracefully
                            response_data = {
                                "success": False, 
                                "error": "Fibaro callback not set", 
                                "status_code": 503
                            }
                    except Exception as e:
                        response_data = {"success": False, "error": str(e), "status_code": 500}
                        
                elif message.type == "quickapp_info":
                    # Get specific QuickApp info
                    data = message.data
                    qa_id = data.get("qa_id")
                    logger.info(f"🔧 IPC QuickApp info request: QA {qa_id}")
                    try:
                        if self.quickapp_callback:
                            logger.info(f"🔧 Calling quickapp_callback for QA {qa_id}")
                            qa_info = self.quickapp_callback("get_quickapp", qa_id)
                            if qa_info:
                                # Convert any LuaTable objects to Python objects before IPC
                                qa_info = self._convert_lua_objects(qa_info)
                                logger.info(f"🔧 QuickApp info found: {qa_info}")
                                response_data = {"success": True, "data": qa_info}
                            else:
                                logger.warning(f"🔧 QuickApp {qa_id} not found")
                                response_data = {"success": False, "error": f"QuickApp {qa_id} not found"}
                        else:
                            logger.error("🔧 QuickApp callback not set!")
                            response_data = {"success": False, "error": "QuickApp callback not set"}
                    except Exception as e:
                        logger.error(f"🔧 QuickApp callback error: {e}")
                        response_data = {"success": False, "error": str(e)}
                        
                elif message.type == "all_quickapps_info":
                    # Get all QuickApps info
                    logger.info("🔧 IPC All QuickApps info request")
                    try:
                        if self.quickapp_callback:
                            logger.info("🔧 Calling quickapp_callback for all QAs")
                            all_qas = self.quickapp_callback("get_all_quickapps")
                            # Convert any LuaTable objects to Python objects before IPC
                            all_qas = self._convert_lua_objects(all_qas)
                            logger.info(f"🔧 All QuickApps found: {all_qas}")
                            response_data = {"success": True, "data": all_qas}
                        else:
                            logger.error("🔧 QuickApp callback not set!")
                            response_data = {"success": False, "error": "QuickApp callback not set"}
                    except Exception as e:
                        logger.error(f"🔧 QuickApp callback error: {e}")
                        response_data = {"success": False, "error": str(e)}
                        
                else:
                    response_data = {"success": False, "error": "Unknown message type or no handler"}
                
                # Send response back
                response = {
                    "id": message.id,
                    "type": "response",
                    "data": response_data,
                    "timestamp": time.time()
                }
                
                self.response_queue.put(response, timeout=1.0)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"IPC message handling error: {e}")
                
        logger.info("IPC message handler stopped")
        
    def broadcast_view_update(self, qa_id: int, element_id: str, property_name: str, value: Any) -> bool:
        """Send a WebSocket broadcast request via IPC"""
        try:
            if not self.is_running():
                logger.warning("FastAPI process not running")
                return False
                
            # Convert LuaTable objects before sending via IPC
            converted_value = self._convert_lua_objects(value)
                
            # Queue the WebSocket broadcast request
            broadcast_data = {
                "id": str(uuid.uuid4()),
                "type": "websocket_broadcast",
                "data": {
                    "qa_id": qa_id,
                    "element_id": element_id,
                    "property_name": property_name,
                    "value": converted_value
                },
                "timestamp": time.time()
            }
            
            self.broadcast_queue.put(broadcast_data)
            return True
            
        except Exception as e:
            logger.error(f"Error queuing WebSocket broadcast: {e}")
            return False
        
    def is_running(self) -> bool:
        """Check if the FastAPI process/thread is running"""
        if platform.system() == "Windows":
            # On Windows, check thread instead of process
            return self.running and hasattr(self, 'server_thread') and self.server_thread.is_alive()
        else:
            # Unix/Linux - check process
            return self.running and self.server_process and self.server_process.is_alive()


# Global process manager instance
_process_manager: Optional[FastAPIProcessManager] = None


def get_process_manager() -> Optional[FastAPIProcessManager]:
    """Get the global process manager instance"""
    return _process_manager


def start_fastapi_process(host: str = "localhost", port: int = 8080, config: Dict[str, Any] = None) -> FastAPIProcessManager:
    """Start the global FastAPI server process"""
    global _process_manager
    
    if _process_manager and _process_manager.is_running():
        logger.warning("FastAPI process already running")
        return _process_manager
        
    _process_manager = FastAPIProcessManager(host, port, config)
    _process_manager.start()
    return _process_manager


def stop_fastapi_process():
    """Stop the global FastAPI server process"""
    global _process_manager
    
    if _process_manager:
        _process_manager.stop()
        _process_manager = None
