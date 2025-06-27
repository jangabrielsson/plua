"""
Embedded API Server for PLua (single-process, always started by PLua)
Do NOT run this file directly.
"""

import os
import sys
import threading
import time
from datetime import datetime
from typing import Optional, Any, List, Dict

# Add the project root to the path so we can import api_server
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from fastapi import FastAPI, HTTPException, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel, Field
    import uvicorn
    import httpx
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install with: pip install fastapi uvicorn httpx")
    raise

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
    {"name": "Panels favoriteColors methods", "description": "Favorite colors management"},
    {"name": "Diagnostics methods", "description": "Diagnostics info"},
    {"name": "Proxy methods", "description": "Proxy operations"},
]


class EmbeddedAPIServer:
    """Embedded FastAPI server that runs within the PLua interpreter process"""

    def __init__(self, interpreter, host="127.0.0.1", port=8000, debug=False):
        self.interpreter = interpreter
        self.host = host
        self.port = port
        self.debug = debug
        self.app = None
        self.server = None
        self.server_thread = None
        self.running = False

        if FastAPI is None:
            raise ImportError("FastAPI is not available")

    async def _handle_redirect(self, redirect_data, method, path, data, query_params, headers):
        """Handle redirect to external HC3 server"""
        try:
            hostname = redirect_data.get('hostname')
            port = redirect_data.get('port', 80)

            # Handle case where hostname contains full URL
            if hostname.startswith('http://') or hostname.startswith('https://'):
                # Extract just the hostname part
                from urllib.parse import urlparse
                parsed = urlparse(hostname)
                hostname = parsed.netloc
                # Use the scheme from the URL if provided
                scheme = parsed.scheme
            else:
                # Use default scheme based on port
                scheme = "https" if port == 443 else "http"

            # Construct the external URL
            url = f"{scheme}://{hostname}:{port}{path}"

            print(f"DEBUG: Redirecting to external server: {url}")

            # Prepare headers for the external request
            external_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            # Add any additional headers from the original request
            if headers:
                external_headers.update(headers)

            # Make the request to the external HC3 server
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(url, params=query_params, headers=external_headers)
                elif method == "POST":
                    response = await client.post(url, json=data, params=query_params, headers=external_headers)
                elif method == "PUT":
                    response = await client.put(url, json=data, params=query_params, headers=external_headers)
                elif method == "DELETE":
                    response = await client.delete(url, params=query_params, headers=external_headers)
                else:
                    raise HTTPException(status_code=400, detail=f"Unsupported method: {method}")

                print(f"DEBUG: External server response status: {response.status_code}")

                # Return the response from the external server
                return response.json(), response.status_code

        except httpx.RequestError as e:
            print(f"DEBUG: Request error during redirect: {e}")
            raise HTTPException(status_code=502, detail=f"Failed to connect to external HC3 server: {str(e)}")
        except Exception as e:
            print(f"DEBUG: Error during redirect: {e}")
            raise HTTPException(status_code=500, detail=f"Error proxying to external server: {str(e)}")

    def _unpack_result(self, result):
        """Helper to unpack Lua {data, status} result for FastAPI endpoints."""
        if result is None:
            return None, 200
        if isinstance(result, (list, tuple)) and len(result) == 2 and isinstance(result[1], int):
            return result[0], result[1]
        return result, 200

    def create_app(self):
        """Create the FastAPI application"""
        app = FastAPI(
            title="PLua Embedded API Server",
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

        # Store reference to interpreter
        app.state.interpreter = self.interpreter

        # Define models
        class ExecuteRequest(BaseModel):
            code: str = Field(..., description="Lua code to execute")
            session_id: Optional[str] = Field(None, description="Session ID for stateful execution")
            timeout: Optional[int] = Field(30, description="Execution timeout in seconds")
            libraries: Optional[List[str]] = Field(None, description="Libraries to load")

        class ExecuteResponse(BaseModel):
            success: bool
            result: Optional[Any] = None
            error: Optional[str] = None
            session_id: Optional[str] = None
            execution_time: Optional[float] = None

        # Additional models for HC3 endpoints
        class ActionParams(BaseModel):
            args: list

        class RoomSpec(BaseModel):
            id: Optional[int] = None
            name: Optional[str] = None
            sectionID: Optional[int] = None
            category: Optional[str] = None
            icon: Optional[str] = None
            visible: Optional[bool] = True

        class SectionSpec(BaseModel):
            name: Optional[str] = None
            id: Optional[int] = None

        class CustomEventSpec(BaseModel):
            name: str
            userdescription: Optional[str] = ""

        class RefreshStatesQuery(BaseModel):
            last: int = 0
            lang: str = "en"
            rand: float = 0.09580020181569104
            logs: bool = False

        class UpdatePropertyParams(BaseModel):
            deviceId: int
            propertyName: str
            value: Any

        class UpdateViewParams(BaseModel):
            deviceId: int
            componentName: str
            propertyName: str
            newValue: Any

        class RestartParams(BaseModel):
            deviceId: int

        class ChildParams(BaseModel):
            parentId: Optional[int] = None
            name: str
            type: str
            initialProperties: Optional[Dict[str, Any]] = None
            initialInterfaces: Optional[List[str]] = None

        class EventParams(BaseModel):
            type: str
            source: Optional[int] = None
            data: Any

        class InternalStorageParams(BaseModel):
            name: str
            value: Any
            isHidden: bool = False

        class DebugMessageSpec(BaseModel):
            message: str
            messageType: str = "info"
            tag: str

        class DebugMsgQuery(BaseModel):
            filter: List[str] = []
            limit: int = 100
            offset: int = 0

        class QAFileSpec(BaseModel):
            name: str
            content: str
            type: Optional[str] = "lua"

        class QAImportSpec(BaseModel):
            name: str
            files: List[QAFileSpec]
            initialInterfaces: Optional[Any] = None

        class QAImportParams(BaseModel):
            file: str
            roomId: Optional[int] = None

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

        class DefaultSensorParams(BaseModel):
            light: Optional[int] = None
            temperature: Optional[int] = None
            humidity: Optional[int] = None

        class HomeParams(BaseModel):
            defaultSensors: DefaultSensorParams
            firstRunAfterUpdate: bool

        class ProxyParams(BaseModel):
            url: str

        # API endpoints
        @app.get("/", response_class=HTMLResponse, tags=["Core"])
        async def root():
            """Web interface"""
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>PLua Web Interface</title>
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
                        <h1>PLua Web Interface</h1>
                        <p>Execute Lua code with Python extensions via web interface</p>
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
                                const outputText = result.result || 'No output';
                                output.innerHTML = `<span class="status success">Success (${timeStr}s)</span><br><br>Output:<br>${outputText}`;
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

                    async function loadStatus() {
                        const statusContent = document.getElementById('statusContent');

                        try {
                            const response = await fetch('/api/status');
                            const status = await response.json();

                            const interpreterStatus = status.interpreter_initialized ? 'success' : 'error';
                            const interpreterText = status.interpreter_initialized ? 'Initialized' : 'Not Initialized';

                            statusContent.innerHTML = `
                                <p><strong>Server Time:</strong> ${status.server_time || 'Unknown'}</p>
                                <p><strong>Interpreter:</strong> <span class="status ${interpreterStatus}">${interpreterText}</span></p>
                                <p><strong>Active Sessions:</strong> ${status.active_sessions || 0}</p>
                                <p><strong>Active Timers:</strong> ${status.active_timers || 0}</p>
                                <p><strong>Network Operations:</strong> ${status.active_network_operations || 0}</p>
                                <p><strong>Python Version:</strong> ${status.python_version || 'Unknown'}</p>
                                <p><strong>Lua Version:</strong> ${status.lua_version || 'Unknown'}</p>
                                <p><strong>PLua Version:</strong> ${status.plua_version || 'Unknown'}</p>
                            `;
                        } catch (error) {
                            statusContent.innerHTML = `<span class="status error">Failed to load status: ${error.message}</span>`;
                        }
                    }
                </script>
            </body>
            </html>
            """

        @app.get("/health", tags=["Core"])
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}

        @app.post("/api/execute", response_model=ExecuteResponse, tags=["Core"])
        async def execute_lua_code(request: ExecuteRequest):
            """Execute Lua code"""
            start_time = time.time()

            # Clear any previous output
            self.interpreter.clear_output_buffer()

            # Execute the code
            result = await self.interpreter.async_execute_code(request.code)

            # Get captured output
            captured_output = self.interpreter.get_captured_output()

            execution_time = time.time() - start_time

            return ExecuteResponse(
                success=True,
                result=captured_output if captured_output else result,
                session_id=request.session_id,
                execution_time=execution_time,
            )

        @app.get("/api/status", tags=["Core"])
        async def get_status():
            """Get server status and interpreter information"""
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

            # Get PLua version from the interpreter
            plua_version = "Unknown"
            try:
                lua_globals = self.interpreter.get_lua_runtime().globals()
                if hasattr(lua_globals, '_PLUA_VERSION'):
                    plua_version = lua_globals._PLUA_VERSION
                else:
                    # Fallback: try to get it directly from the version module
                    from plua.version import __version__
                    plua_version = __version__
            except Exception:
                # Final fallback
                plua_version = "1.0.0"

            return {
                "server_time": datetime.now().isoformat(),
                "interpreter_initialized": self.interpreter is not None,
                "active_sessions": 0,
                "active_timers": active_timers,
                "active_network_operations": active_network_operations,
                "python_version": sys.version,
                "lua_version": "Lua 5.4",
                "plua_version": plua_version,
            }

        @app.post("/api/restart", tags=["Core"])
        async def restart_interpreter():
            """Restart the PLua interpreter to reset the environment"""
            try:
                # Clear any existing interpreter
                self.interpreter.clear_output_buffer()

                return {
                    "success": True,
                    "message": "Interpreter restarted successfully",
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        # Fibaro API endpoints
        @app.get("/api/devices", tags=["Device methods"])
        async def get_devices(request: Request, response: Response):
            """Get all devices"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/devices')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    if not data:
                        return []
                    if isinstance(data, dict):
                        return list(data.values())
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/devices/{id}", tags=["Device methods"])
        async def get_device(id: int, request: Request, response: Response):
            """Get a specific device"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/devices/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/globalVariables", tags=["GlobalVariables methods"])
        async def get_global_variables(request: Request, response: Response):
            """Get all global variables"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/globalVariables')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    if not data:
                        return []
                    if isinstance(data, dict):
                        return list(data.values())
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/globalVariables/{name}", tags=["GlobalVariables methods"])
        async def get_global_variable(name: str, request: Request, response: Response):
            """Get a specific global variable"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/globalVariables/{name}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Device action endpoints
        @app.post("/api/devices/{id}/action/{name}", tags=["Device methods"])
        async def call_quickapp_method(id: int, name: str, args: ActionParams, response: Response):
            """Call a QuickApp method"""
            t = time.time()
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/devices/{id}/action/{name}', {args.args})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return {
                        "endTimestampMillis": time.time(),
                        "message": "Accepted",
                        "startTimestampMillis": t,
                    }
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/callAction", tags=["Device methods"])
        async def callAction_quickapp_method(request: Request, response: Response):
            """Call QuickApp action via query parameters"""
            qps = request.query_params._dict
            # Remove deviceID and name from query params
            del qps["deviceID"]
            del qps["name"]
            args = [a for a in qps.values()]
            t = time.time()
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/callAction', {args}, {qps})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return {
                        "endTimestampMillis": time.time(),
                        "message": "Accepted",
                        "startTimestampMillis": t,
                    }
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/devices/hierarchy", tags=["Device methods"])
        async def get_Device_Hierarchy():
            """Get device hierarchy"""
            # Return dummy hierarchy data
            return {"devices": [{"id": 1, "name": "Device1", "children": []}]}

        @app.delete("/api/devices/{id}", tags=["Device methods"])
        async def delete_Device(id: int, response: Response):
            """Delete a device"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('DELETE', '/api/devices/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Rooms endpoints
        @app.get("/api/rooms", tags=["Rooms methods"])
        async def get_Rooms(response: Response):
            """Get all rooms"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/rooms')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    if not data:
                        return []
                    if isinstance(data, dict):
                        return list(data.values())
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/rooms/{id}", tags=["Rooms methods"])
        async def get_Room(id: int, response: Response):
            """Get a specific room"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/rooms/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/rooms", tags=["Rooms methods"])
        async def create_Room(room: RoomSpec, response: Response):
            """Create a new room"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/rooms', {room.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.put("/api/rooms/{id}", tags=["Rooms methods"])
        async def modify_Room(id: int, room: RoomSpec, response: Response):
            """Modify a room"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('PUT', '/api/rooms/{id}', {room.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.delete("/api/rooms/{id}", tags=["Rooms methods"])
        async def delete_Room(id: int, response: Response):
            """Delete a room"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('DELETE', '/api/rooms/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Sections endpoints
        @app.get("/api/sections", tags=["Section methods"])
        async def get_Sections(response: Response):
            """Get all sections"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/sections')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    if not data:
                        return []
                    if isinstance(data, dict):
                        return list(data.values())
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/sections/{id}", tags=["Section methods"])
        async def get_Section(id: int, response: Response):
            """Get a specific section"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/sections/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/sections", tags=["Section methods"])
        async def create_Section(section: SectionSpec, response: Response):
            """Create a new section"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/sections', {section.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.put("/api/sections/{id}", tags=["Section methods"])
        async def modify_Section(id: int, section: SectionSpec, response: Response):
            """Modify a section"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('PUT', '/api/sections/{id}', {section.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.delete("/api/sections/{id}", tags=["Section methods"])
        async def delete_Section(id: int, response: Response):
            """Delete a section"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('DELETE', '/api/sections/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Custom Events endpoints
        @app.get("/api/customEvents", tags=["CustomEvents methods"])
        async def get_CustomEvents(response: Response):
            """Get all custom events"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/customEvents')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    if not data:
                        return []
                    if isinstance(data, dict):
                        return list(data.values())
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/customEvents/{name}", tags=["CustomEvents methods"])
        async def get_CustomEvent(name: str, response: Response):
            """Get a specific custom event"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/customEvents/{name}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/customEvents", tags=["CustomEvents methods"])
        async def create_CustomEvent(customEvent: CustomEventSpec, response: Response):
            """Create a new custom event"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/customEvents', {customEvent.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.put("/api/customEvents/{name}", tags=["CustomEvents methods"])
        async def modify_CustomEvent(name: str, customEvent: CustomEventSpec, response: Response):
            """Modify a custom event"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('PUT', '/api/customEvents/{name}', {customEvent.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.delete("/api/customEvents/{name}", tags=["CustomEvents methods"])
        async def delete_CustomEvent(name: str, response: Response):
            """Delete a custom event"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('DELETE', '/api/customEvents/{name}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/customEvents/{name}/emit", tags=["CustomEvents methods"])
        async def emit_CustomEvent(name: str, response: Response):
            """Emit a custom event"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/customEvents/{name}/emit')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # RefreshStates endpoints
        @app.get("/api/refreshStates", tags=["RefreshStates methods"])
        async def get_refreshStates_events(query: RefreshStatesQuery, response: Response):
            """Get refresh states events"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/refreshStates', None, {query.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # iosDevices endpoints
        @app.get("/api/iosDevices", tags=["iosDevices methods"])
        async def get_iosDevices(response: Response):
            """Get iOS devices"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/iosDevices')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Home endpoints
        @app.get("/api/home", tags=["Home methods"])
        async def get_Home(response: Response):
            """Get home information"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/home')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # DebugMessages endpoints
        @app.post("/api/debugMessages", tags=["DebugMessages methods"])
        async def add_debug_message(args: DebugMessageSpec, response: Response):
            """Add debug message"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/debugMessages', {args.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/debugMessages", tags=["DebugMessages methods"])
        async def get_debug_messages(response: Response):
            """Get debug messages"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/debugMessages')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Weather endpoints
        @app.get("/api/weather", tags=["Weather methods"])
        async def get_Weather(response: Response):
            """Get weather information"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/weather')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.put("/api/weather", tags=["Weather methods"])
        async def modify_Weather(args: WeatherSpec, response: Response):
            """Modify weather information"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('PUT', '/api/weather', {args.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Plugins endpoints
        @app.get("/api/plugins/callUIEvent", tags=["Plugins methods"])
        async def call_ui_event(request: Request, response: Response):
            """Call UI event via query parameters"""
            qps = request.query_params._dict
            # Remove deviceID and name from query params
            del qps["deviceID"]
            del qps["name"]
            args = [a for a in qps.values()]
            t = time.time()
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/plugins/callUIEvent', {args}, {qps})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return {
                        "endTimestampMillis": time.time(),
                        "message": "Accepted",
                        "startTimestampMillis": t,
                    }
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/plugins/updateProperty", tags=["Plugins methods"])
        async def update_qa_property(args: UpdatePropertyParams, response: Response):
            """Update QuickApp property"""
            t = time.time()
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/plugins/updateProperty', {args.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return {
                        "endTimestampMillis": time.time(),
                        "message": "Accepted",
                        "startTimestampMillis": t,
                    }
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/plugins/updateView", tags=["Plugins methods"])
        async def update_qa_view(args: UpdateViewParams, response: Response):
            """Update QuickApp view"""
            t = time.time()
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/plugins/updateView', {args.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return {
                        "endTimestampMillis": time.time(),
                        "message": "Accepted",
                        "startTimestampMillis": t,
                    }
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/plugins/restart", tags=["Plugins methods"])
        async def restart_qa(args: RestartParams, response: Response):
            """Restart QuickApp"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/plugins/restart', {args.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/plugins/createChildDevice", tags=["Plugins methods"])
        async def create_Child_Device(args: ChildParams, response: Response):
            """Create child device"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/plugins/createChildDevice', {args.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.delete("/api/plugins/removeChildDevice/{id}", tags=["Plugins methods"])
        async def delete_Child_Device(id: int, response: Response):
            """Remove child device"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('DELETE', '/api/plugins/removeChildDevice/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/plugins/publishEvent", tags=["Plugins methods"])
        async def publish_event(args: EventParams, response: Response):
            """Publish event"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/plugins/publishEvent', {args.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/plugins/{id}/variables", tags=["Plugins methods"])
        async def get_plugin_variables(id: int, response: Response):
            """Get plugin variables"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/plugins/{id}/variables')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/plugins/{id}/variables/{name}", tags=["Plugins methods"])
        async def get_plugin_variable(id: int, name: str, response: Response):
            """Get specific plugin variable"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/plugins/{id}/variables/{name}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/plugins/{id}/variables", tags=["Plugins methods"])
        async def create_plugin_variable(id: int, args: InternalStorageParams, response: Response):
            """Create plugin variable"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/plugins/{id}/variables', {args.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.put("/api/plugins/{id}/variables/{name}", tags=["Plugins methods"])
        async def update_plugin_variable(id: int, name: str, args: InternalStorageParams, response: Response):
            """Update plugin variable"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('PUT', '/api/plugins/{id}/variables/{name}', {args.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.delete("/api/plugins/{id}/variables/{name}", tags=["Plugins methods"])
        async def delete_plugin_variable(id: int, name: str, response: Response):
            """Delete plugin variable"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('DELETE', '/api/plugins/{id}/variables/{name}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.delete("/api/plugins/{id}/variables", tags=["Plugins methods"])
        async def delete_all_plugin_variables(id: int, response: Response):
            """Delete all plugin variables"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('DELETE', '/api/plugins/{id}/variables')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # QuickApp endpoints
        @app.get("/api/quickApp/{id}/files", tags=["QuickApp methods"])
        async def get_QuickApp_Files(id: int, response: Response):
            """Get QuickApp files"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/quickApp/{id}/files')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/quickApp/{id}/files", tags=["QuickApp methods"])
        async def create_QuickApp_Files(id: int, file: QAFileSpec, response: Response):
            """Create QuickApp file"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/quickApp/{id}/files', {file.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/quickApp/{id}/files/{name}", tags=["QuickApp methods"])
        async def get_QuickApp_File(id: int, name: str, response: Response):
            """Get specific QuickApp file"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/quickApp/{id}/files/{name}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.put("/api/quickApp/{id}/files/{name}", tags=["QuickApp methods"])
        async def modify_QuickApp_File(id: int, name: str, file: QAFileSpec, response: Response):
            """Modify QuickApp file"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('PUT', '/api/quickApp/{id}/files/{name}', {file.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.put("/api/quickApp/{id}/files", tags=["QuickApp methods"])
        async def modify_QuickApp_Files(id: int, args: List[QAFileSpec], response: Response):
            """Modify multiple QuickApp files"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('PUT', '/api/quickApp/{id}/files', {[f.model_dump() for f in args]})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/quickApp/export/{id}", tags=["QuickApp methods"])
        async def export_QuickApp_FQA(id: int, response: Response):
            """Export QuickApp"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/quickApp/export/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/quickApp/", tags=["QuickApp methods"])
        async def import_QuickApp(file: QAImportSpec, response: Response):
            """Import QuickApp"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('POST', '/api/quickApp', {file.model_dump()})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.delete("/api/quickApp/{id}/files/{name}", tags=["QuickApp methods"])
        async def delete_QuickApp_File(id: int, name: str, response: Response):
            """Delete QuickApp file"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('DELETE', '/api/quickApp/{id}/files/{name}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Settings endpoints
        @app.get("/api/settings/{name}", tags=["Settings methods"])
        async def get_Settings(name: str, response: Response):
            """Get setting"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/settings/{name}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Partitions endpoints
        @app.get("/api/alarms/v1/partitions", tags=["Partition methods"])
        async def get_Partitions(response: Response):
            """Get partitions"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/alarms/v1/partitions')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/alarms/v1/partitions/{id}", tags=["Partition methods"])
        async def get_Partition(id: int, response: Response):
            """Get specific partition"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/alarms/v1/partitions/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Alarm devices endpoints
        @app.get("/api/alarms/v1/devices", tags=["Alarm devices methods"])
        async def get_alarm_devices(response: Response):
            """Get alarm devices"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/alarms/v1/devices')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # NotificationCenter endpoints
        @app.get("/api/notificationCenter", tags=["NotificationCenter methods"])
        async def get_NotificationCenter(response: Response):
            """Get notification center"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/notificationCenter')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Profiles endpoints
        @app.get("/api/profiles/{id}", tags=["Profiles methods"])
        async def get_Profile(id: int, response: Response):
            """Get specific profile"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/profiles/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/profiles", tags=["Profiles methods"])
        async def get_Profiles(response: Response):
            """Get all profiles"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/profiles')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Icons endpoints
        @app.get("/api/icons", tags=["Icons methods"])
        async def get_Icons(response: Response):
            """Get icons"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/icons')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Users endpoints
        @app.get("/api/users", tags=["Users methods"])
        async def get_Users(response: Response):
            """Get users"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/users')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Energy devices endpoints
        @app.get("/api/energy/devices", tags=["Energy devices methods"])
        async def get_Energy_Devices(response: Response):
            """Get energy devices"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/energy/devices')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Panels endpoints
        @app.get("/api/panels/location", tags=["Panels location methods"])
        async def get_Panels_Location(response: Response):
            """Get panels location"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/panels/location')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/panels/climate/{id}", tags=["Panels climate methods"])
        async def get_Panels_Climate_by_id(id: int, response: Response):
            """Get specific climate panel"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/panels/climate/{id}')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/panels/climate", tags=["Panels climate methods"])
        async def get_Panels_Climate(response: Response):
            """Get climate panels"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/panels/climate')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/panels/notifications", tags=["Panels notifications methods"])
        async def get_Panels_Notifications(response: Response):
            """Get notifications panels"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/panels/notifications')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/panels/family", tags=["Panels family methods"])
        async def get_Panels_Family(response: Response):
            """Get family panels"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/panels/family')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/panels/sprinklers", tags=["Panels sprinklers methods"])
        async def get_Panels_Sprinklers(response: Response):
            """Get sprinklers panels"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/panels/sprinklers')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/panels/humidity", tags=["Panels humidity methods"])
        async def get_Panels_Humidity(response: Response):
            """Get humidity panels"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/panels/humidity')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/panels/favoriteColors", tags=["Panels favoriteColors methods"])
        async def get_Favorite_Colors(response: Response):
            """Get favorite colors"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/panels/favoriteColors')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/panels/favoriteColors/v2", tags=["Panels favoriteColors methods"])
        async def get_Favorite_ColorsV2(response: Response):
            """Get favorite colors v2"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/panels/favoriteColors/v2')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Diagnostics endpoints
        @app.get("/api/diagnostics", tags=["Diagnostics methods"])
        async def get_Diagnostics(response: Response):
            """Get diagnostics"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    "return _PY.fibaroapi('GET', '/api/diagnostics')"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Proxy endpoints
        @app.get("/api/proxy", tags=["Proxy methods"])
        async def call_via_proxy(query: ProxyParams, response: Response):
            """Call via proxy"""
            try:
                result = self.interpreter.execute_lua_code_remote(
                    f"return _PY.fibaroapi('GET', '/api/proxy', None, {{'url': '{query.url}'}})"
                )
                if result.get("success"):
                    lua_result = result.get("result", [])
                    data, status = self._unpack_result(lua_result)
                    response.status_code = status
                    return data
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        self.app = app
        return app

    def start(self):
        """Start the API server in a background thread"""
        if self.running:
            return

        try:
            # Create the app
            self.create_app()

            # Start server in background thread
            def run_server():
                # Set log level based on debug flag
                log_level = "info" if self.debug else "error"

                config = uvicorn.Config(
                    self.app,
                    host=self.host,
                    port=self.port,
                    log_level=log_level,
                    access_log=False,
                    timeout_keep_alive=30,
                    timeout_graceful_shutdown=10
                )
                self.server = uvicorn.Server(config)
                self.server.run()

            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()

            # Wait a moment for server to start, but with timeout
            import time
            start_time = time.time()
            while not self.running and time.time() - start_time < 10:
                time.sleep(0.1)
                # Check if server is responding
                try:
                    import requests
                    response = requests.get(f"http://{self.host}:{self.port}/health", timeout=1)
                    if response.status_code == 200:
                        self.running = True
                        break
                except (requests.RequestException, ImportError):
                    pass

            if not self.running:
                if self.debug:
                    print("Warning: Embedded API server may not have started properly")
            else:
                if self.debug:
                    print(f"Embedded API server started on http://{self.host}:{self.port}")

        except Exception as e:
            if self.debug:
                print(f"Failed to start embedded API server: {e}")
            self.running = False

    def stop(self):
        """Stop the API server"""
        if self.server and self.running:
            self.server.should_exit = True
            self.running = False
            if self.debug:
                print("Embedded API server stopped")

    def is_running(self):
        """Check if the server is running"""
        return self.running
