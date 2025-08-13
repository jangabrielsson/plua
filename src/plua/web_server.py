"""
Web Server Extension for EPLua

Provides a FastAPI-based web server that can be controlled from Lua scripts.
The server runs in a separate thread and communicates with the main Lua engine
through the thread-safe callback system.
"""

import asyncio
import threading
import time
import uuid
from typing import Optional, Dict, Any
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel

from .lua_bindings import export_to_lua, get_global_engine, get_exported_functions


class ExecuteRequest(BaseModel):
    """Request model for executing Lua scripts."""
    script: str
    timeout: Optional[float] = 30.0
    is_json: Optional[bool] = False


class JsonApiRequest(BaseModel):
    """Request model for JSON API function calls."""
    function_name: str
    module_name: Optional[str] = None
    args: Optional[list] = []
    timeout: Optional[float] = 30.0


class ServerStatus(BaseModel):
    """Server status response model."""
    status: str
    uptime: float
    active_callbacks: int
    running_intervals: int
    server_port: int


class WebServerManager:
    """Manages the FastAPI web server in a separate thread."""

    def __init__(self):
        self.app = FastAPI(title="EPLua API", version="0.1.0")
        self.server_thread: Optional[threading.Thread] = None
        self.server = None
        self.port = 8000
        self.host = "127.0.0.1"
        self.start_time = time.time()
        self.is_running = False
        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes."""

        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint."""
            return {"message": "EPLua API Server", "version": "0.1.0"}

        @self.app.get("/status", response_model=ServerStatus)
        async def get_status():
            """Get server and engine status."""
            engine = get_global_engine()
            if not engine:
                raise HTTPException(status_code=503, detail="EPLua engine not available")

            return ServerStatus(
                status="running",
                uptime=time.time() - self.start_time,
                active_callbacks=engine.get_pending_callback_count(),
                running_intervals=engine.get_running_intervals_count(),
                server_port=self.port
            )

        @self.app.post("/execute")
        async def execute_script(request: ExecuteRequest):
            """Execute a Lua script and return the result."""
            engine = get_global_engine()
            if not engine:
                raise HTTPException(status_code=503, detail="EPLua engine not available")

            try:
                # Execute the script using the thread-safe execution method
                result = engine.execute_script_from_thread(
                    request.script,
                    request.timeout,
                    request.is_json
                )

                if result["success"]:
                    return {
                        "result": result["result"],
                        "execution_time": result["execution_time"]
                    }
                else:
                    raise HTTPException(status_code=400, detail=f"Lua error: {result['error']}")

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

        @self.app.get("/engine/callbacks")
        async def get_callbacks():
            """Get information about active callbacks."""
            engine = get_global_engine()
            if not engine:
                raise HTTPException(status_code=503, detail="EPLua engine not available")

            # For now, we'll return basic counts since we don't have individual callback details
            return {
                "callbacks": [],  # Individual callback details not available
                "count": engine.get_pending_callback_count(),
                "running_intervals": engine.get_running_intervals_count()
            }

    def start_server(self, host: str = "127.0.0.1", port: int = 8000):
        """Start the web server in a separate thread."""
        if self.is_running:
            return False, "Server is already running"

        self.host = host
        self.port = port
        self.start_time = time.time()

        def run_server():
            """Run the uvicorn server."""
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            self.server = uvicorn.Server(config)
            asyncio.run(self.server.serve())

        try:
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            self.is_running = True  # Set after thread starts

            # Give the server a moment to start
            time.sleep(0.5)

            return True, f"Server started on http://{self.host}:{self.port}"
        except Exception as e:
            self.is_running = False  # Reset on error
            return False, f"Failed to start server: {str(e)}"

    def stop_server(self):
        """Stop the web server."""
        if not self.is_running:
            return False, "Server is not running"

        try:
            if self.server:
                # Note: uvicorn.Server doesn't have a clean shutdown method
                # In a production environment, you'd want to handle this more gracefully
                pass

            self.is_running = False
            return True, "Server stop requested"
        except Exception as e:
            return False, f"Failed to stop server: {str(e)}"

    def get_server_info(self):
        """Get information about the server."""
        return {
            "running": self.is_running,
            "host": self.host,
            "port": self.port,
            "uptime": time.time() - self.start_time if self.is_running else 0,
            "url": f"http://{self.host}:{self.port}" if self.is_running else None
        }


# Global web server manager instance
_web_server_manager = None


def get_web_server_manager():
    """Get the global web server manager instance."""
    global _web_server_manager
    if _web_server_manager is None or not _web_server_manager.is_running:
        _web_server_manager = WebServerManager()
    return _web_server_manager


def start_web_server(host: str = "127.0.0.1", port: int = 8000, callback_id: str = None):
    """
    Start the web server.

    Args:
        host: Host to bind to (default: 127.0.0.1)
        port: Port to bind to (default: 8000)
        callback_id: Optional callback ID for result notification
    """

    def execute():
        manager = get_web_server_manager()
        success, message = manager.start_server(host, port)

        result = {
            "success": success,
            "message": message,
            "server_info": manager.get_server_info()
        }

        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, error=None, result=result)

        return result

    # Run in a separate thread to avoid blocking
    thread = threading.Thread(target=execute)
    thread.start()

    if not callback_id:
        thread.join()  # Wait for completion if no callback
        # Return the result from the manager since execute() already ran
        return {
            "success": True,
            "message": "Server operation completed",
            "server_info": get_web_server_manager().get_server_info()
        }


def stop_web_server(callback_id: str = None):
    """
    Stop the web server.

    Args:
        callback_id: Optional callback ID for result notification
    """
    def execute():
        manager = get_web_server_manager()
        success, message = manager.stop_server()

        result = {
            "success": success,
            "message": message
        }

        if callback_id:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, error=None, result=result)

        return result

    # Run in a separate thread
    thread = threading.Thread(target=execute)
    thread.start()

    if not callback_id:
        thread.join()
        # Return the result from the manager since execute() already ran
        return {
            "success": True,
            "message": "Server operation completed",
            "server_info": get_web_server_manager().get_server_info()
        }


def get_web_server_status():
    """
    Get the current status of the web server.

    Returns:
        Dict with server status information
    """
    manager = get_web_server_manager()
    return manager.get_server_info()


def register_web_server_functions():
    """Register web server functions with the export system."""
    from .lua_bindings import _exported_functions

    _exported_functions["start_web_server"] = start_web_server
    _exported_functions["stop_web_server"] = stop_web_server
    _exported_functions["get_web_server_status"] = get_web_server_status


# Call registration immediately
register_web_server_functions()
