#!/usr/bin/env python3
# NOTE: This API server is now always started by PLua as an embedded server.
# Do NOT run this file directly. Use `python plua.py` or your main entrypoint instead.

"""
PLua API Server
A FastAPI-based REST API frontend for the PLua interpreter.
Provides endpoints for executing Lua code, managing scripts, and accessing extensions.
"""
import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Response,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field

import extensions
from plua.interpreter import PLuaInterpreter
import json

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize the event loop manager
loop_manager = extensions.network_extensions.loop_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API tags for better organization
tags_metadata = [
    {"name": "Core", "description": "Core PLua functionality"},
    {"name": "Device methods", "description": "Device and QuickApp methods"},
    {"name": "GlobalVariables methods", "description": "Managing global variables"},
    {"name": "Rooms methods", "description": "Managing rooms"},
    {"name": "Section methods", "description": "Managing sections"},
    {"name": "CustomEvents methods", "description": "Managing custom events"},
    {"name": "RefreshStates methods", "description": "Getting events"},
    {"name": "Plugins methods", "description": "Plugin methods"},
    {"name": "QuickApp methods", "description": "Managing QuickApps"},
    {"name": "Weather methods", "description": "Weather status"},
    {"name": "iosDevices methods", "description": "iOS devices info"},
    {"name": "Home methods", "description": "Home info"},
    {"name": "DebugMessages methods", "description": "Debug messages info"},
    {"name": "Settings methods", "description": "Settings info"},
    {"name": "Partition methods", "description": "Partitions management"},
    {"name": "Alarm devices methods", "description": "Alarm device management"},
    {"name": "NotificationCenter methods", "description": "Notification management"},
    {"name": "Profiles methods", "description": "Profiles management"},
    {"name": "Icons methods", "description": "Icons management"},
    {"name": "Users methods", "description": "Users management"},
    {"name": "Energy devices methods", "description": "Energy management"},
    {"name": "Panels location methods", "description": "Location management"},
    {"name": "Panels notifications methods", "description": "Notifications management"},
    {"name": "Panels family methods", "description": "Family management"},
    {"name": "Panels sprinklers methods", "description": "Sprinklers management"},
    {"name": "Panels humidity methods", "description": "Humidity management"},
    {
        "name": "Panels favoriteColors methods",
        "description": "Favorite colors management",
    },
    {"name": "Diagnostics methods", "description": "Diagnostics info"},
]

# Create FastAPI app
app = FastAPI(
    title="PLua API Server",
    description="Fibaro HC3 compatible API for PLua",
    version="1.0.0",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={
        "docExpansion": "none",
        "operationsSorter": "alpha",
        "tagsSorter": "alpha",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global interpreter instance
interpreter: Optional[PLuaInterpreter] = None
active_sessions: Dict[str, Dict[str, Any]] = {}


# Pydantic models for API requests/responses
class ExecuteRequest(BaseModel):
    code: str = Field(..., description="Lua code to execute")
    session_id: Optional[str] = Field(
        None, description="Session ID for stateful execution"
    )
    timeout: Optional[int] = Field(30, description="Execution timeout in seconds")
    libraries: Optional[List[str]] = Field(
        [], description="Libraries to load before execution"
    )


class ExecuteResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    session_id: Optional[str] = None
    execution_time: Optional[float] = None


class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    last_activity: datetime
    variables: Dict[str, Any]
    active_timers: int
    active_network_operations: int


class ExtensionInfo(BaseModel):
    name: str
    description: str
    category: str
    parameters: Optional[List[str]] = None


class FileInfo(BaseModel):
    name: str
    path: str
    size: int
    modified: datetime
    is_directory: bool


class ActionParams(BaseModel):
    args: list


class PLuaRegistration(BaseModel):
    instance_id: str
    port: int = 8000
    host: str = "127.0.0.1"


# Initialize the interpreter
def init_interpreter():
    """Initialize the global interpreter instance"""
    global interpreter

    if interpreter is None:
        interpreter = PLuaInterpreter(
            debug=True, start_api_server=False
        )  # Don't start nested API server
        logger.info("PLua interpreter initialized in standalone mode")


# API endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize the interpreter on startup"""
    init_interpreter()


@app.get("/", response_class=HTMLResponse, tags=["Core"])
async def root():
    """Serve a modern HTML interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PLua API Server</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 { margin: 0; font-size: 2.5em; }
            .header p { margin: 10px 0 0 0; opacity: 0.9; }
            .content { padding: 30px; }
            .section {
                margin: 30px 0;
                padding: 25px;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                background: #fafbfc;
            }
            .section h2 {
                margin: 0 0 20px 0;
                color: #24292e;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .code-input {
                width: 100%;
                height: 200px;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 14px;
                padding: 15px;
                border: 1px solid #d1d5da;
                border-radius: 6px;
                resize: vertical;
                background: #f6f8fa;
            }
            .button {
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 500;
                transition: background 0.2s;
            }
            .button:hover { background: #5a6fd8; }
            .button:disabled { background: #ccc; cursor: not-allowed; }
            .output {
                background: #f6f8fa;
                padding: 20px;
                border-radius: 6px;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                white-space: pre-wrap;
                border: 1px solid #e1e5e9;
                min-height: 100px;
                max-height: 400px;
                overflow-y: auto;
            }
            .status {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }
            .status.success { background: #d4edda; color: #155724; }
            .status.error { background: #f8d7da; color: #721c24; }
            .status.info { background: #d1ecf1; color: #0c5460; }
            .tabs {
                display: flex;
                border-bottom: 1px solid #e1e5e9;
                margin-bottom: 20px;
            }
            .tab {
                padding: 10px 20px;
                cursor: pointer;
                border-bottom: 2px solid transparent;
                transition: all 0.2s;
            }
            .tab.active {
                border-bottom-color: #667eea;
                color: #667eea;
                font-weight: 500;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .api-links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .api-link {
                padding: 15px;
                border: 1px solid #e1e5e9;
                border-radius: 6px;
                text-decoration: none;
                color: #24292e;
                transition: all 0.2s;
            }
            .api-link:hover {
                border-color: #667eea;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>PLua API Server</h1>
                <p>Execute Lua code with Python extensions via REST API</p>
            </div>

            <div class="content">
                <div class="tabs">
                    <div class="tab active" onclick="showTab('execute')">Execute Code</div>
                    <div class="tab" onclick="showTab('api')">API Documentation</div>
                    <div class="tab" onclick="showTab('status')">Server Status</div>
                </div>

                <div id="execute" class="tab-content active">
                    <div class="section">
                        <h2>Execute Lua Code</h2>
                        <textarea id="code" class="code-input" placeholder="Enter Lua code here...">print("Hello from PLua!")
print("Current time:", _PY.get_time())
print("Python version:", _PY.get_python_version())</textarea>
                        <br><br>
                        <button onclick="executeCode()" class="button" id="executeBtn">Execute</button>
                        <button onclick="clearOutput()" class="button" style="background: #6c757d; margin-left: 10px;">Clear</button>
                        <button onclick="restartInterpreter()" class="button" style="background: #dc3545; margin-left: 10px;">Restart Interpreter</button>
                        <div id="output" class="output">Ready to execute Lua code...</div>
                    </div>
                </div>

                <div id="api" class="tab-content">
                    <div class="section">
                        <h2>API Documentation</h2>
                        <p>Access the full API documentation and interactive testing interface:</p>
                        <div class="api-links">
                            <a href="/docs" target="_blank" class="api-link">
                                <strong>Swagger UI</strong><br>
                                Interactive API documentation with testing interface
                            </a>
                            <a href="/redoc" target="_blank" class="api-link">
                                <strong>ReDoc</strong><br>
                                Beautiful, responsive API documentation
                            </a>
                        </div>
                    </div>
                </div>

                <div id="status" class="tab-content">
                    <div class="section">
                        <h2>Server Status</h2>
                        <div id="statusContent">Loading...</div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function showTab(tabName) {
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });

                // Show selected tab
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');

                // Load status if needed
                if (tabName === 'status') {
                    loadStatus();
                }
            }

            async function executeCode() {
                const code = document.getElementById('code').value;
                const output = document.getElementById('output');
                const executeBtn = document.getElementById('executeBtn');

                output.textContent = 'Executing...';
                executeBtn.disabled = true;

                try {
                    const response = await fetch('/api/execute', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ code: code })
                    });

                    const result = await response.json();

                    if (result.success) {
                        const timeStr = result.execution_time?.toFixed(3) || '0.000';
                        output.innerHTML = `<span class="status success">Success (${timeStr}s)</span><br><br>Result:<br>${result.result}`;
                    } else {
                        const timeStr = result.execution_time?.toFixed(3) || '0.000';
                        output.innerHTML = `<span class="status error">Error (${timeStr}s)</span><br><br>${result.error}`;
                    }
                } catch (error) {
                    output.innerHTML = `<span class="status error">Request Failed</span><br><br>${error.message}`;
                } finally {
                    executeBtn.disabled = false;
                }
            }

            function clearOutput() {
                document.getElementById('output').textContent = 'Ready to execute Lua code...';
            }

            async function restartInterpreter() {
                const output = document.getElementById('output');
                const restartBtn = event.target;

                output.textContent = 'Restarting interpreter...';
                restartBtn.disabled = true;

                try {
                    const response = await fetch('/api/restart', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });

                    const result = await response.json();

                    if (result.success) {
                        output.innerHTML = `<span class="status success">Interpreter Restarted</span><br><br>${result.message}<br>Timestamp: ${result.timestamp}`;
                    } else {
                        output.innerHTML = `<span class="status error">Restart Failed</span><br><br>${result.error}`;
                    }
                } catch (error) {
                    output.innerHTML = `<span class="status error">Request Failed</span><br><br>${error.message}`;
                } finally {
                    restartBtn.disabled = false;
                }
            }

            async function loadStatus() {
                const statusContent = document.getElementById('statusContent');

                try {
                    const response = await fetch('/api/status');
                    const status = await response.json();

                    const interpreterStatus = status.interpreter_initialized ? 'success' : 'error';
                    const interpreterText = status.interpreter_initialized ? 'Initialized' : 'Not Initialized';

                    statusContent.innerHTML = `
                        <p><strong>Server Time:</strong> ${status.server_time}</p>
                        <p><strong>Interpreter:</strong> <span class="status ${interpreterStatus}">${interpreterText}</span></p>
                        <p><strong>Active Sessions:</strong> ${status.active_sessions}</p>
                        <p><strong>Active Timers:</strong> ${status.active_timers}</p>
                        <p><strong>Network Operations:</strong> ${status.active_network_operations}</p>
                        <p><strong>Python Version:</strong> ${status.python_version}</p>
                        <p><strong>Lua Version:</strong> ${status.lua_version}</p>
                    `;
                } catch (error) {
                    statusContent.innerHTML = `<span class="status error">Failed to load status: ${error.message}</span>`;
                }
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/execute", tags=["Core"], response_model=ExecuteResponse)
async def execute_lua_code(request: ExecuteRequest):
    """Execute Lua code"""
    global interpreter

    start_time = time.time()

    # Initialize interpreter if needed
    if interpreter is None:
        init_interpreter()

    # Clear any previous output
    if interpreter:
        interpreter.clear_output_buffer()

    # Execute the code
    result = await interpreter.async_execute_code(request.code)

    # Get captured output
    captured_output = interpreter.get_captured_output()

    execution_time = time.time() - start_time

    return ExecuteResponse(
        success=True,
        result=captured_output if captured_output else result,
        session_id=request.session_id,
        execution_time=execution_time,
    )


@app.get("/api/sessions", response_model=List[SessionInfo], tags=["Core"])
async def list_sessions():
    """List all active sessions"""
    global active_sessions

    sessions = []
    for session_id, session_data in active_sessions.items():
        sessions.append(
            SessionInfo(
                session_id=session_id,
                created_at=session_data["created_at"],
                last_activity=session_data["last_activity"],
                variables=session_data["variables"],
                active_timers=session_data["active_timers"],
                active_network_operations=session_data["active_network_operations"],
            )
        )

    return sessions


@app.delete("/api/sessions/{session_id}", tags=["Core"])
async def delete_session(session_id: str):
    """Delete a session"""
    global active_sessions

    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"success": True, "message": f"Session {session_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/api/extensions", response_model=List[ExtensionInfo], tags=["Core"])
async def list_extensions():
    """List all available extensions"""
    from extensions.registry import registry

    extensions = []
    metadata = registry.get_extension_metadata()

    for name, ext_data in metadata.items():
        extensions.append(
            ExtensionInfo(
                name=name,
                description=ext_data["description"],
                category=ext_data["category"],
            )
        )

    return extensions


@app.get("/api/extensions/{category}", response_model=List[ExtensionInfo], tags=["Core"])
async def list_extensions_by_category(category: str):
    """List extensions by category"""
    from extensions.registry import registry

    extensions = []
    metadata = registry.get_extension_metadata()

    for name, ext_data in metadata.items():
        if ext_data["category"] == category:
            extensions.append(
                ExtensionInfo(
                    name=name,
                    description=ext_data["description"],
                    category=ext_data["category"],
                )
            )

    return extensions


@app.get("/api/files", response_model=List[FileInfo], tags=["Core"])
async def list_files(directory: str = "."):
    """List files in a directory"""
    try:
        path = Path(directory).resolve()
        if not path.exists():
            raise HTTPException(status_code=404, detail="Directory not found")

        files = []
        for item in path.iterdir():
            try:
                stat = item.stat()
                files.append(
                    FileInfo(
                        name=item.name,
                        path=str(item),
                        size=stat.st_size,
                        modified=datetime.fromtimestamp(stat.st_mtime),
                        is_directory=item.is_dir(),
                    )
                )
            except (OSError, PermissionError):
                continue

        return sorted(files, key=lambda x: (x.is_directory, x.name))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/{file_path:path}", tags=["Core"])
async def read_file(file_path: str):
    """Read a file's contents"""
    try:
        path = Path(file_path).resolve()
        if not path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        if path.is_dir():
            raise HTTPException(status_code=400, detail="Path is a directory")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "path": str(path),
            "content": content,
            "size": len(content),
            "modified": datetime.fromtimestamp(path.stat().st_mtime),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/files/{file_path:path}", tags=["Core"])
async def write_file(file_path: str, content: str):
    """Write content to a file"""
    try:
        path = Path(file_path).resolve()

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return {"success": True, "path": str(path), "size": len(content)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status", tags=["Core"])
async def get_status():
    """Get server status and interpreter information"""
    global interpreter

    if interpreter is None:
        init_interpreter()

    # Get active timers and network operations through extensions
    active_timers = 0
    active_network_operations = 0

    try:
        from extensions.core import timer_manager

        active_timers = timer_manager.has_active_timers()
    except Exception:
        pass

    try:
        from extensions.network_extensions import has_active_network_operations

        active_network_operations = has_active_network_operations()
    except Exception:
        pass

    return {
        "server_time": datetime.now().isoformat(),
        "interpreter_initialized": interpreter is not None,
        "active_sessions": len(active_sessions),
        "active_timers": active_timers,
        "active_network_operations": active_network_operations,
        "python_version": sys.version,
        "lua_version": "Lua 5.4",
    }


# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message["type"] == "execute":
                # Execute Lua code
                try:
                    result = await interpreter.async_execute_code(message["code"])
                    await websocket.send_text(
                        json.dumps(
                            {"type": "result", "success": True, "result": result}
                        )
                    )
                except Exception as e:
                    await websocket.send_text(
                        json.dumps(
                            {"type": "result", "success": False, "error": str(e)}
                        )
                    )

            elif message["type"] == "status":
                # Send current status
                active_timers = 0
                active_network_operations = 0

                try:
                    from extensions.core import timer_manager

                    active_timers = timer_manager.has_active_timers()
                except Exception:
                    pass

                try:
                    from extensions.network_extensions import (
                        has_active_network_operations,
                    )

                    active_network_operations = has_active_network_operations()
                except Exception:
                    pass

                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "status",
                            "active_timers": active_timers,
                            "active_network_operations": active_network_operations,
                        }
                    )
                )

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")


# Health check endpoint
@app.get("/health", tags=["Core"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="PLua API Server",
        version="1.0.0",
        description="REST API for executing Lua code with Python extensions",
        routes=app.routes,
    )

    openapi_schema["info"] = {
        "title": "PLua API Server",
        "version": "1.0.0",
        "description": "A comprehensive REST API for executing Lua code with Python extensions, managing sessions, and accessing file system operations.",
        "contact": {
            "name": "PLua API Support",
            "url": "https://github.com/your-repo/plua",
        },
        "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Device endpoints
class DeviceQueryParams(BaseModel):
    id: Optional[int] = None
    parentId: Optional[int] = None
    name: Optional[str] = None
    baseType: Optional[str] = None
    interface: Optional[str] = None
    type: Optional[str] = None


@app.get("/api/devices", tags=["Device methods"])
async def get_devices(response: Response):
    """Get all devices"""
    result, code = call_fibaro_api("GET", "/api/devices")
    response.status_code = code
    if not result:
        return []
    if isinstance(result, dict):
        return list(result.values())
    return result


@app.get("/api/devices/{id}", tags=["Device methods"])
async def get_Device(id: int, response: Response):
    """Get a specific device"""
    result, code = call_fibaro_api("GET", f"/api/devices/{id}")
    response.status_code = code
    return result if code < 300 else None


# GlobalVariables endpoints
@app.get("/api/globalVariables", tags=["GlobalVariables methods"])
async def get_Global_Variables(response: Response):
    """Get all global variables"""
    result, code = call_fibaro_api("GET", "/api/globalVariables")
    response.status_code = code
    if not result:
        return []
    if isinstance(result, dict):
        return list(result.values())
    return result


@app.get("/api/globalVariables/{name}", tags=["GlobalVariables methods"])
async def get_Global_Variable(name: str, response: Response):
    """Get a specific global variable"""
    result, code = call_fibaro_api("GET", f"/api/globalVariables/{name}")
    response.status_code = code
    return result if code < 300 else None


# Device action endpoints
@app.post("/api/devices/{id}/action/{name}", tags=["Device methods"])
async def call_quickapp_method(id: int, name: str, args: ActionParams):
    """Call a QuickApp method"""
    t = time.time()
    result, code = call_fibaro_api("POST", f"/api/devices/{id}/action/{name}", args.args)
    return {
        "endTimestampMillis": time.time(),
        "message": "Accepted",
        "startTimestampMillis": t,
    }


@app.get("/api/callAction", tags=["Device methods"])
async def callAction_quickapp_method(response: Response, request: Request):
    """Call QuickApp action via query parameters"""
    qps = request.query_params._dict
    # Remove deviceID and name from query params
    del qps["deviceID"]
    del qps["name"]
    args = [a for a in qps.values()]
    t = time.time()
    result, code = call_fibaro_api("POST", "/api/callAction", args, qps)
    return {
        "endTimestampMillis": time.time(),
        "message": "Accepted",
        "startTimestampMillis": t,
    }


@app.get("/api/devices/hierarchy", tags=["Device methods"])
async def get_Device_Hierarchy():
    """Get device hierarchy"""
    # Return dummy hierarchy data
    return {"devices": [{"id": 1, "name": "Device1", "children": []}]}


@app.delete("/api/devices/{id}", tags=["Device methods"])
async def delete_Device(id: int, response: Response):
    """Delete a device"""
    result, code = call_fibaro_api("DELETE", f"/api/devices/{id}")
    response.status_code = code
    return result if code < 300 else None


# Rooms endpoints
class RoomSpec(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    sectionID: Optional[int] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    visible: Optional[bool] = True


@app.get("/api/rooms", tags=["Rooms methods"])
async def get_Rooms(response: Response):
    """Get all rooms"""
    result, code = call_fibaro_api("GET", "/api/rooms")
    response.status_code = code
    if not result:
        return []
    if isinstance(result, dict):
        return list(result.values())
    return result


@app.get("/api/rooms/{id}", tags=["Rooms methods"])
async def get_Room(id: int, response: Response):
    """Get a specific room"""
    result, code = call_fibaro_api("GET", f"/api/rooms/{id}")
    response.status_code = code
    return result if code < 300 else None


@app.post("/api/rooms", tags=["Rooms methods"])
async def create_Room(room: RoomSpec, response: Response):
    """Create a new room"""
    result, code = call_fibaro_api("POST", "/api/rooms", room.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.put("/api/rooms/{id}", tags=["Rooms methods"])
async def modify_Room(id: int, room: RoomSpec, response: Response):
    """Modify a room"""
    result, code = call_fibaro_api("PUT", f"/api/rooms/{id}", room.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.delete("/api/rooms/{id}", tags=["Rooms methods"])
async def delete_Room(id: int, response: Response):
    """Delete a room"""
    result, code = call_fibaro_api("DELETE", f"/api/rooms/{id}")
    response.status_code = code
    return result if code < 300 else None


# Sections endpoints
class SectionSpec(BaseModel):
    name: Optional[str] = None
    id: Optional[int] = None


@app.get("/api/sections", tags=["Section methods"])
async def get_Sections(response: Response):
    """Get all sections"""
    result, code = call_fibaro_api("GET", "/api/sections")
    response.status_code = code
    if not result:
        return []
    if isinstance(result, dict):
        return list(result.values())
    return result


@app.get("/api/sections/{id}", tags=["Section methods"])
async def get_Section(id: int, response: Response):
    """Get a specific section"""
    result, code = call_fibaro_api("GET", f"/api/sections/{id}")
    response.status_code = code
    return result if code < 300 else None


@app.post("/api/sections", tags=["Section methods"])
async def create_Section(section: SectionSpec, response: Response):
    """Create a new section"""
    result, code = call_fibaro_api("POST", "/api/sections", section.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.put("/api/sections/{id}", tags=["Section methods"])
async def modify_Section(id: int, section: SectionSpec, response: Response):
    """Modify a section"""
    result, code = call_fibaro_api("PUT", f"/api/sections/{id}", section.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.delete("/api/sections/{id}", tags=["Section methods"])
async def delete_Section(id: int, response: Response):
    """Delete a section"""
    result, code = call_fibaro_api("DELETE", f"/api/sections/{id}")
    response.status_code = code
    return result if code < 300 else None


# Custom Events endpoints
class CustomEventSpec(BaseModel):
    name: str
    userdescription: Optional[str] = ""


@app.get("/api/customEvents", tags=["CustomEvents methods"])
async def get_CustomEvents(response: Response):
    """Get all custom events"""
    result, code = call_fibaro_api("GET", "/api/customEvents")
    response.status_code = code
    if not result:
        return []
    if isinstance(result, dict):
        return list(result.values())
    return result


@app.get("/api/customEvents/{name}", tags=["CustomEvents methods"])
async def get_CustomEvent(name: str, response: Response):
    """Get a specific custom event"""
    result, code = call_fibaro_api("GET", f"/api/customEvents/{name}")
    response.status_code = code
    return result if code < 300 else None


@app.post("/api/customEvents", tags=["CustomEvents methods"])
async def create_CustomEvent(customEvent: CustomEventSpec, response: Response):
    """Create a new custom event"""
    result, code = call_fibaro_api("POST", "/api/customEvents", customEvent.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.put("/api/customEvents/{name}", tags=["CustomEvents methods"])
async def modify_CustomEvent(
    name: str, customEvent: CustomEventSpec, response: Response
):
    """Modify a custom event"""
    result, code = call_fibaro_api("PUT", f"/api/customEvents/{name}", customEvent.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.delete("/api/customEvents/{name}", tags=["CustomEvents methods"])
async def delete_CustomEvent(name: str, response: Response):
    """Delete a custom event"""
    result, code = call_fibaro_api("DELETE", f"/api/customEvents/{name}")
    response.status_code = code
    return result if code < 300 else None


@app.post("/api/customEvents/{name}/emit", tags=["CustomEvents methods"])
async def emit_CustomEvent(name: str, response: Response):
    """Emit a custom event"""
    result, code = call_fibaro_api("POST", f"/api/customEvents/{name}/emit")
    response.status_code = code
    return {} if code < 300 else None


# RefreshStates endpoints
class RefreshStatesQuery(BaseModel):
    last: int = 0
    lang: str = "en"
    rand: float = 0.09580020181569104
    logs: bool = False


@app.get("/api/refreshStates", tags=["RefreshStates methods"])
async def get_refreshStates_events(
    response: Response, query: RefreshStatesQuery = Depends()
):
    """Get refresh states events"""
    result, code = call_fibaro_api("GET", "/api/refreshStates", None, query.model_dump())
    response.status_code = 200
    return result


# Plugins endpoints
@app.get("/api/plugins/callUIEvent", tags=["Plugins methods"])
async def call_ui_event(response: Response, request: Request):
    """Call UI event via query parameters"""
    qps = request.query_params._dict
    # Remove deviceID and name from query params
    del qps["deviceID"]
    del qps["name"]
    args = [a for a in qps.values()]
    t = time.time()
    result, code = call_fibaro_api("POST", "/api/plugins/callUIEvent", args, qps)
    return {
        "endTimestampMillis": time.time(),
        "message": "Accepted",
        "startTimestampMillis": t,
    }


class UpdatePropertyParams(BaseModel):
    deviceId: int
    propertyName: str
    value: Any


@app.post("/api/plugins/updateProperty", tags=["Plugins methods"])
async def update_qa_property(args: UpdatePropertyParams):
    """Update QuickApp property"""
    t = time.time()
    result, code = call_fibaro_api("POST", "/api/plugins/updateProperty", args.model_dump())
    return {
        "endTimestampMillis": time.time(),
        "message": "Accepted",
        "startTimestampMillis": t,
    }


class UpdateViewParams(BaseModel):
    deviceId: int
    componentName: str
    propertyName: str
    newValue: Any


@app.post("/api/plugins/updateView", tags=["Plugins methods"])
async def update_qa_view(args: UpdateViewParams):
    """Update QuickApp view"""
    t = time.time()
    result, code = call_fibaro_api("POST", "/api/plugins/updateView", args.model_dump())
    return {
        "endTimestampMillis": time.time(),
        "message": "Accepted",
        "startTimestampMillis": t,
    }


class RestartParams(BaseModel):
    deviceId: int


@app.post("/api/plugins/restart", tags=["Plugins methods"])
async def restart_qa(args: RestartParams, response: Response):
    """Restart QuickApp"""
    result, code = call_fibaro_api("POST", "/api/plugins/restart", args.model_dump())
    response.status_code = code
    return {} if code < 300 else None


class ChildParams(BaseModel):
    parentId: Optional[int] = None
    name: str
    type: str
    initialProperties: Optional[Dict[str, Any]] = None
    initialInterfaces: Optional[List[str]] = None


@app.post("/api/plugins/createChildDevice", tags=["Plugins methods"])
async def create_Child_Device(args: ChildParams, response: Response):
    """Create child device"""
    result, code = call_fibaro_api("POST", "/api/plugins/createChildDevice", args.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.delete("/api/plugins/removeChildDevice/{id}", tags=["Plugins methods"])
async def delete_Child_Device(id: int, response: Response):
    """Remove child device"""
    result, code = call_fibaro_api("DELETE", f"/api/plugins/removeChildDevice/{id}")
    response.status_code = code
    return result if code < 300 else None


class EventParams(BaseModel):
    type: str
    source: Optional[int] = None
    data: Any


@app.post("/api/plugins/publishEvent", tags=["Plugins methods"])
async def publish_event(args: EventParams, response: Response):
    """Publish event"""
    result, code = call_fibaro_api("POST", "/api/plugins/publishEvent", args.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.get("/api/plugins/{id}/variables", tags=["Plugins methods"])
async def get_plugin_variables(id: int, response: Response):
    """Get plugin variables"""
    result, code = call_fibaro_api("GET", f"/api/plugins/{id}/variables")
    response.status_code = code
    return result if code < 300 else None


@app.get("/api/plugins/{id}/variables/{name}", tags=["Plugins methods"])
async def get_plugin_variable(id: int, name: str, response: Response):
    """Get specific plugin variable"""
    result, code = call_fibaro_api("GET", f"/api/plugins/{id}/variables/{name}")
    response.status_code = code
    return result if code < 300 else None


class InternalStorageParams(BaseModel):
    name: str
    value: Any
    isHidden: bool = False


@app.post("/api/plugins/{id}/variables", tags=["Plugins methods"])
async def create_plugin_variable(
    id: int, args: InternalStorageParams, response: Response
):
    """Create plugin variable"""
    result, code = call_fibaro_api("POST", f"/api/plugins/{id}/variables", args.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.put("/api/plugins/{id}/variables/{name}", tags=["Plugins methods"])
async def update_plugin_variable(
    id: int, name: str, args: InternalStorageParams, response: Response
):
    """Update plugin variable"""
    result, code = call_fibaro_api("PUT", f"/api/plugins/{id}/variables/{name}", args.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.delete("/api/plugins/{id}/variables/{name}", tags=["Plugins methods"])
async def delete_plugin_variable(id: int, name: str, response: Response):
    """Delete plugin variable"""
    result, code = call_fibaro_api("DELETE", f"/api/plugins/{id}/variables/{name}")
    response.status_code = code
    return result if code < 300 else None


@app.delete("/api/plugins/{id}/variables", tags=["Plugins methods"])
async def delete_all_plugin_variables(id: int, response: Response):
    """Delete all plugin variables"""
    result, code = call_fibaro_api("DELETE", f"/api/plugins/{id}/variables")
    response.status_code = code
    return result if code < 300 else None


# DebugMessages endpoints
class DebugMessageSpec(BaseModel):
    message: str
    messageType: str = "info"
    tag: str


@app.post("/api/debugMessages", tags=["DebugMessages methods"])
async def add_debug_message(args: DebugMessageSpec, response: Response):
    """Add debug message"""
    result, code = call_fibaro_api("POST", "/api/debugMessages", args.model_dump())
    response.status_code = code
    return result if code < 300 else None


class DebugMsgQuery(BaseModel):
    filter: List[str] = []
    limit: int = 100
    offset: int = 0


@app.get("/api/debugMessages", tags=["DebugMessages methods"])
async def get_debug_messages(response: Response, request: Request):
    """Get debug messages"""
    # Return dummy debug messages
    messages = [
        {"message": "Test message 1", "type": "info", "timestamp": time.time()},
        {"message": "Test message 2", "type": "warning", "timestamp": time.time()},
    ]
    return messages


# QuickApp endpoints
@app.get("/api/quickApp/{id}/files", tags=["QuickApp methods"])
async def get_QuickApp_Files(id: int, response: Response):
    """Get QuickApp files"""
    result, code = call_fibaro_api("GET", f"/api/quickApp/{id}/files")
    response.status_code = code
    return result if code < 300 else None


class QAFileSpec(BaseModel):
    name: str
    content: str
    type: Optional[str] = "lua"


@app.post("/api/quickApp/{id}/files", tags=["QuickApp methods"])
async def create_QuickApp_Files(id: int, file: QAFileSpec, response: Response):
    """Create QuickApp file"""
    result, code = call_fibaro_api("POST", f"/api/quickApp/{id}/files", file.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.get("/api/quickApp/{id}/files/{name}", tags=["QuickApp methods"])
async def get_QuickApp_File(id: int, name: str, response: Response):
    """Get specific QuickApp file"""
    result, code = call_fibaro_api("GET", f"/api/quickApp/{id}/files/{name}")
    response.status_code = code
    return result if code < 300 else None


@app.put("/api/quickApp/{id}/files/{name}", tags=["QuickApp methods"])
async def modify_QuickApp_File(
    id: int, name: str, file: QAFileSpec, response: Response
):
    """Modify QuickApp file"""
    result, code = call_fibaro_api("PUT", f"/api/quickApp/{id}/files/{name}", file.model_dump())
    response.status_code = code
    return result if code < 300 else None


@app.put("/api/quickApp/{id}/files", tags=["QuickApp methods"])
async def modify_QuickApp_Files(id: int, args: List[QAFileSpec], response: Response):
    """Modify multiple QuickApp files"""
    result, code = call_fibaro_api("PUT", f"/api/quickApp/{id}/files", [f.model_dump() for f in args])
    response.status_code = code
    return result if code < 300 else None


@app.get("/api/quickApp/export/{id}", tags=["QuickApp methods"])
async def export_QuickApp_FQA(id: int, response: Response):
    """Export QuickApp"""
    result, code = call_fibaro_api("GET", f"/api/quickApp/export/{id}")
    response.status_code = code
    return result if code < 300 else None


class QAImportSpec(BaseModel):
    name: str
    files: List[QAFileSpec]
    initialInterfaces: Optional[Any] = None


@app.post("/api/quickApp/", tags=["QuickApp methods"])
async def import_QuickApp(file: QAImportSpec, response: Response):
    """Import QuickApp"""
    result, code = call_fibaro_api("POST", "/api/quickApp", file.model_dump())
    response.status_code = code
    return result if code < 300 else None


class QAImportParams(BaseModel):
    file: str
    roomId: Optional[int] = None


@app.post("/api/quickApp/import", tags=["QuickApp methods"])
async def import_QuickApp_file(file: QAImportParams, response: Response):
    """Import QuickApp from file"""
    t = time.time()
    result, code = call_fibaro_api("POST", "/api/quickApp/import", file.model_dump())
    return {
        "endTimestampMillis": time.time(),
        "message": "Accepted",
        "startTimestampMillis": t,
    }


@app.delete("/api/quickApp/{id}/files/{name}", tags=["QuickApp methods"])
async def delete_QuickApp_File(id: int, name: str, response: Response):
    """Delete QuickApp file"""
    result, code = call_fibaro_api("DELETE", f"/api/quickApp/{id}/files/{name}")
    response.status_code = code
    return result if code < 300 else None


# Weather endpoints
@app.get("/api/weather", tags=["Weather methods"])
async def get_Weather(response: Response):
    """Get weather information"""
    result, code = call_fibaro_api("GET", "/api/weather")
    response.status_code = code
    return result if code < 300 else None


class WeatherSpec(BaseModel):
    ConditionCode: Optional[float] = None
    ConditionText: Optional[str] = None
    Temperature: Optional[float] = None
    FeelsLike: Optional[float] = None
    Humidity: Optional[float] = None
    Pressure: Optional[float] = None
    WindSpeed: Optional[float] = None
    WindDirection: Optional[str] = None
    WindUnit: Optional[str] = None


@app.put("/api/weather", tags=["Weather methods"])
async def modify_Weather(args: WeatherSpec, response: Response):
    """Modify weather information"""
    result, code = call_fibaro_api("PUT", "/api/weather", args.model_dump())
    response.status_code = code
    return result if code < 300 else None


# iOS Devices endpoints
@app.get("/api/iosDevices", tags=["iosDevices methods"])
async def get_iosDevices(response: Response):
    """Get iOS devices"""
    result, code = call_fibaro_api("GET", "/api/iosDevices")
    response.status_code = code
    return result if code < 300 else None


# Home endpoints
@app.get("/api/home", tags=["Home methods"])
async def get_Home(response: Response):
    """Get home information"""
    result, code = call_fibaro_api("GET", "/api/home")
    response.status_code = code
    return result if code < 300 else None


class DefaultSensorParams(BaseModel):
    light: Optional[int] = None
    temperature: Optional[int] = None
    humidity: Optional[int] = None


class HomeParams(BaseModel):
    defaultSensors: DefaultSensorParams
    firstRunAfterUpdate: bool


@app.put("/api/home", tags=["Home methods"])
async def modify_Home(args: HomeParams, response: Response):
    """Modify home information"""
    result, code = call_fibaro_api("PUT", "/api/home", args.model_dump())
    response.status_code = code
    return result if code < 300 else None


# Settings endpoints
@app.get("/api/settings/{name}", tags=["Settings methods"])
async def get_Settings(name: str, response: Response):
    """Get setting"""
    result, code = call_fibaro_api("GET", f"/api/settings/{name}")
    response.status_code = code
    return result if code < 300 else None


# Alarms endpoints
@app.get("/api/alarms/v1/partitions", tags=["Partition methods"])
async def get_Partitions(response: Response):
    """Get partitions"""
    result, code = call_fibaro_api("GET", "/api/alarms/v1/partitions")
    response.status_code = code
    return result


@app.get("/api/alarms/v1/partitions/{id}", tags=["Partition methods"])
async def get_Partition(id: int, response: Response):
    """Get specific partition"""
    result, code = call_fibaro_api("GET", f"/api/alarms/v1/partitions/{id}")
    response.status_code = code
    return result if code < 300 else None


@app.post("/alarms/v1/partitions/actions/arm", tags=["Partition methods"])
async def post_PartitionArm(id: int, response: Response):
    """Arm specific partition"""
    result, code = call_fibaro_api("POST", f"/alarms/v1/partitions/{id}/actions/arm")
    response.status_code = code
    return result if code < 300 else None


@app.delete("/alarms/v1/partitions/{id}/actions/arm", tags=["Partition methods"])
async def delete_PartitionArm(id: int, response: Response):
    """Disarm specific partition"""
    result, code = call_fibaro_api("DELETE", f"/alarms/v1/partitions/{id}/actions/arm")
    response.status_code = code
    return result if code < 300 else None


@app.get("/api/alarms/v1/devices/", tags=["Alarm devices methods"])
async def get_alarm_devices(response: Response):
    """Get alarm devices"""
    result, code = call_fibaro_api("GET", "/api/alarms/v1/devices")
    response.status_code = code
    return result


# NotificationCenter endpoints
@app.get("/api/notificationCenter", tags=["NotificationCenter methods"])
async def get_NotificationCenter(response: Response):
    """Get notification center"""
    result, code = call_fibaro_api("GET", "/api/notificationCenter")
    response.status_code = code
    return result


# Profiles endpoints
@app.get("/api/profiles/{id}", tags=["Profiles methods"])
async def get_Profile(id: int, response: Response):
    """Get specific profile"""
    result, code = call_fibaro_api("GET", f"/api/profiles/{id}")
    response.status_code = code
    return result.get("profiles")[id] if code < 300 else None


@app.get("/api/profiles", tags=["Profiles methods"])
async def get_Profiles(response: Response):
    """Get all profiles"""
    result, code = call_fibaro_api("GET", "/api/profiles")
    response.status_code = code
    return result if code < 300 else None


# Icons endpoints
@app.get("/api/icons", tags=["Icons methods"])
async def get_Icons(response: Response):
    """Get icons"""
    result, code = call_fibaro_api("GET", "/api/icons")
    response.status_code = code
    return result


# Users endpoints
@app.get("/api/users", tags=["Users methods"])
async def get_Users(response: Response):
    """Get users"""
    result, code = call_fibaro_api("GET", "/api/users")
    response.status_code = code
    return result


# Energy endpoints
@app.get("/api/energy/devices", tags=["Energy devices methods"])
async def get_Energy_Devices(response: Response):
    """Get energy devices"""
    result, code = call_fibaro_api("GET", "/api/energy/devices")
    response.status_code = code
    return result


# Panels endpoints
@app.get("/api/panels/location", tags=["Panels location methods"])
async def get_Panels_Location(response: Response):
    """Get panels location"""
    result, code = call_fibaro_api("GET", "/api/panels/location")
    response.status_code = code
    return result


@app.get("/api/panels/climate/{id}", tags=["Panels climate methods"])
async def get_Panels_Climate_by_id(id: int, response: Response):
    """Get specific climate panel"""
    result, code = call_fibaro_api("GET", f"/api/panels/climate/{id}")
    response.status_code = code
    return result if code < 300 else None


@app.get("/api/panels/climate", tags=["Panels climate methods"])
async def get_Panels_Climate(response: Response):
    """Get climate panels"""
    result, code = call_fibaro_api("GET", "/api/panels/climate")
    response.status_code = code
    return result


@app.get("/api/panels/notifications", tags=["Panels notifications methods"])
async def get_Panels_Notifications(response: Response):
    """Get notifications panels"""
    result, code = call_fibaro_api("GET", "/api/panels/notifications")
    response.status_code = code
    return result


@app.get("/api/panels/family", tags=["Panels family methods"])
async def get_Panels_Family(response: Response):
    """Get family panels"""
    result, code = call_fibaro_api("GET", "/api/panels/family")
    response.status_code = code
    return result


@app.get("/api/panels/sprinklers", tags=["Panels sprinklers methods"])
async def get_Panels_Sprinklers(response: Response):
    """Get sprinklers panels"""
    result, code = call_fibaro_api("GET", "/api/panels/sprinklers")
    response.status_code = code
    return result


@app.get("/api/panels/humidity", tags=["Panels humidity methods"])
async def get_Panels_Humidity(response: Response):
    """Get humidity panels"""
    result, code = call_fibaro_api("GET", "/api/panels/humidity")
    response.status_code = code
    return result


@app.get("/api/panels/favoriteColors", tags=["Panels favoriteColors methods"])
async def get_Favorite_Colors(response: Response):
    """Get favorite colors"""
    result, code = call_fibaro_api("GET", "/api/panels/favoriteColors")
    response.status_code = code
    return result


@app.get("/api/panels/favoriteColors/v2", tags=["Panels favoriteColors methods"])
async def get_Favorite_ColorsV2(response: Response):
    """Get favorite colors v2"""
    result, code = call_fibaro_api("GET", "/api/panels/favoriteColors/v2")
    response.status_code = code
    return result


# Diagnostics endpoints
@app.get("/api/diagnostics", tags=["Diagnostics methods"])
async def get_Diagnostics(response: Response):
    """Get diagnostics"""
    result, code = call_fibaro_api("GET", "/api/diagnostics")
    response.status_code = code
    return result if code < 300 else None


# Proxy endpoints
class ProxyParams(BaseModel):
    url: str


@app.get("/api/proxy", tags=["Proxy methods"])
async def call_via_proxy(response: Response, query: ProxyParams = Depends()):
    """Call via proxy"""
    result, code = call_fibaro_api("GET", "/api/proxy", None, {"url": query.url})
    response.status_code = code
    return result if code < 300 else None


@app.post("/api/restart", tags=["Core"])
async def restart_interpreter():
    """Restart the PLua interpreter to reset the environment"""
    global interpreter

    try:
        # Clear any existing interpreter
        if interpreter:
            # Clear the output buffer
            interpreter.clear_output_buffer()

        # Set interpreter to None to force a fresh initialization
        interpreter = None

        # Reinitialize the interpreter
        init_interpreter()

        return {
            "success": True,
            "message": "Interpreter restarted successfully",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to restart interpreter: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# Helper function to call _PY.fibaroapi if available
def call_fibaro_api(method, path, data=None, query_parameters=None):
    """Call _PY.fibaroapi if available, otherwise return 500 error"""
    global interpreter, active_plua_instance

    # In PLua mode, use the registered instance if available
    if active_plua_instance:
        try:
            # Call the registered PLua instance
            import requests
            response = requests.post(
                f"http://{active_plua_instance['host']}:{active_plua_instance['port']}/api/plua/execute",
                json={
                    "code": f"return _PY.fibaroapi('{method}', '{path}', {repr(data)}, {repr(query_parameters)})",
                    "timeout": 30
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # The result should be a tuple [data, status_code]
                    lua_result = result.get("result", [])
                    if isinstance(lua_result, list) and len(lua_result) >= 2:
                        return lua_result[0], lua_result[1]
                    else:
                        return lua_result, 200
                else:
                    raise HTTPException(status_code=500, detail=f"PLua execution error: {result.get('error', 'Unknown error')}")
            else:
                raise HTTPException(status_code=500, detail=f"Failed to call PLua instance: {response.status_code}")
        except Exception as e:
            logger.error(f"Error calling PLua instance: {e}")
            raise HTTPException(status_code=500, detail=f"PLua instance error: {str(e)}")

    # In standalone mode, use the local interpreter
    if interpreter is None:
        raise HTTPException(status_code=500, detail="Fibaro API not loaded - interpreter not initialized")

    try:
        # Check if _PY.fibaroapi is available
        lua_globals = interpreter.get_lua_runtime().globals()
        if not hasattr(lua_globals, '_PY') or not hasattr(lua_globals['_PY'], 'fibaroapi'):
            raise HTTPException(status_code=500, detail="Fibaro API not loaded - use --fibaro flag")

        # Call the fibaroapi function
        fibaroapi = lua_globals['_PY']['fibaroapi']
        result, status_code = fibaroapi(method, path, data, query_parameters)

        return result, status_code
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calling fibaroapi: {e}")
        raise HTTPException(status_code=500, detail=f"Fibaro API error: {str(e)}")


def set_plua_interpreter_instance(interpreter_instance):
    """Set the active PLua interpreter instance"""
    global active_plua_instance
    active_plua_instance = interpreter_instance


if __name__ == "__main__":
    print("ERROR: Do not run api_server.py directly. Start PLua instead.")
    exit(1)
