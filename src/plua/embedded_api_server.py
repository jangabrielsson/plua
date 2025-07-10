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
import json
from fastapi import WebSocket, WebSocketDisconnect

# Add the project root to the path so we can import api_server
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from fastapi import FastAPI, HTTPException, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
    import uvicorn
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install with: pip install fastapi uvicorn")
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
        self.quickapps_ws_clients = set()

        if FastAPI is None:
            raise ImportError("FastAPI is not available")

    async def broadcast_ui_update(self, device_id):
        message = json.dumps({"type": "ui_update", "deviceID": device_id})
        for ws in list(self.quickapps_ws_clients):
            try:
                await ws.send_text(message)
            except Exception:
                self.quickapps_ws_clients.discard(ws)

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

        # Mount static files
        app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

        # Register websocket endpoint
        quickapps_ws_clients = self.quickapps_ws_clients

        @app.websocket("/ws/quickapps")
        async def quickapps_ws(websocket: WebSocket):
            await websocket.accept()
            quickapps_ws_clients.add(websocket)
            try:
                while True:
                    await websocket.receive_text()  # Keep the connection alive
            except WebSocketDisconnect:
                quickapps_ws_clients.remove(websocket)

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

        class CallUIEventParams(BaseModel):
            deviceID: int
            elementName: str
            eventType: str
            # value: Optional[Any] = None
            values: Optional[List[Any]] = None

        # API endpoints
        @app.get("/", response_class=HTMLResponse, tags=["Core"])
        async def root():
            """Web interface"""
            try:
                with open(os.path.join(os.path.dirname(__file__), "static", "index.html"), "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                return """
                <html>
                <head><title>PLua Web Interface</title></head>
                <body>
                    <h1>PLua Web Interface</h1>
                    <p>Static files not found. Please ensure the static directory exists with index.html, styles.css, and script.js files.</p>
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
            # Build the full path with query parameters
            path = "/api/devices"
            qps = request.query_params._dict
            if qps:
                query_parts = []
                for k, v in qps.items():
                    query_parts.append(f"{k}={v}")
                path += "?" + "&".join(query_parts)
            
            try:
                result = self.interpreter.execute_lua_code(
                    f"return _PY.fibaroapi('GET', '{path}')"
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
                result = self.interpreter.execute_lua_code(
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

        @app.get("/api/devices/{id}/properties/{name}", tags=["Device methods"])
        async def get_device_property(id: int, name: str, response: Response):
            """Get a specific property of a device"""
            try:
                result = self.interpreter.execute_lua_code(
                    f"return _PY.fibaroapi('GET', '/api/devices/{id}/properties/{name}')"
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                # print(f"Calling {id}/{name} with {args}")
                import json
                json_args = json.dumps(args.args)
                result = self.interpreter.execute_lua_code(
                    f"return _PY.fibaroapi('POST', '/api/devices/{id}/action/{name}', json.decode([==[{json_args}]==]))"
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

        @app.get("/api/devices/{id}/action/{name}", tags=["Device methods"])
        async def get_device_action_info(id: int, name: str, response: Response):
            """Get device action information"""
            try:
                result = self.interpreter.execute_lua_code(
                    f"return _PY.fibaroapi('GET', '/api/devices/{id}/action/{name}')"
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

        @app.get("/api/callAction", tags=["Device methods"])
        async def callAction_quickapp_method(request: Request, response: Response):
            """Call QuickApp action via query parameters"""
            qps = request.query_params._dict
            # Build the full path with query parameters
            path = "/api/callAction"
            if qps:
                query_parts = []
                for k, v in qps.items():
                    query_parts.append(f"{k}={v}")
                path += "?" + "&".join(query_parts)
            
            t = time.time()
            try:
                result = self.interpreter.execute_lua_code(
                    f"return _PY.fibaroapi('POST', '{path}')"
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
            # Build the full path with query parameters
            path = "/api/refreshStates"
            query_dict = query.model_dump()
            if query_dict:
                query_parts = []
                for k, v in query_dict.items():
                    query_parts.append(f"{k}={v}")
                path += "?" + "&".join(query_parts)
            
            try:
                result = self.interpreter.execute_lua_code(
                    f"return _PY.fibaroapi('GET', '{path}')"
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
        @app.post("/api/plugins/callUIEvent", tags=["Plugins methods"])
        async def call_ui_event(request: Request, response: Response):
            """Call UI event via POST body"""
            t = time.time()
            try:
                # Parse the request body
                body = await request.body()
                args = CallUIEventParams.model_validate_json(body)
                
                # Use message passing to communicate with main Lua thread
                message_id = self.interpreter.send_api_message("fibaroapi", {
                    "method": "POST",
                    "path": "/api/plugins/callUIEvent",
                    "data": args.model_dump()
                })
                
                # Wait for response from main thread
                result = self.interpreter.get_api_response(message_id, timeout=30)
                
                if result.get("success"):
                    return {
                        "endTimestampMillis": time.time(),
                        "message": "Accepted",
                        "startTimestampMillis": t,
                        "result": result.get("result"),
                    }
                else:
                    response.status_code = 400
                    return {
                        "endTimestampMillis": time.time(),
                        "message": "Not accepted",
                        "startTimestampMillis": t,
                        "error": result.get("error", "Unknown error")
                    }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/plugins/updateProperty", tags=["Plugins methods"])
        async def update_qa_property(args: UpdatePropertyParams, response: Response):
            """Update QuickApp property"""
            t = time.time()
            try:
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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

        @app.get("/api/quickapps", tags=["QuickApp methods"])
        async def get_all_quickapps():
            """Get all emulated QuickApps"""
            try:
                result = self.interpreter.execute_lua_code(
                    "return _PY.getAllQAInfo()"
                )
                if result.get("success"):
                    qa_info_str = result.get("result", "")
                    if qa_info_str and qa_info_str.strip():
                        import json
                        devices = json.loads(qa_info_str)
                        return devices  # Return as-is, do not wrap in {"device": d}
                    return []
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/quickapps/{id}", tags=["QuickApp methods"])
        async def get_quickapp_by_id(id: int):
            """Get specific QuickApp by ID"""
            try:
                result = self.interpreter.execute_lua_code(
                    f"return _PY.getQAInfo({id})"
                )
                if result.get("success"):
                    qa_data_str = result.get("result", "")
                    if qa_data_str and qa_data_str.strip():
                        import json
                        device = json.loads(qa_data_str)
                        return {"device": device}
                    else:
                        raise HTTPException(status_code=404, detail="QuickApp not found")
                else:
                    raise HTTPException(status_code=500, detail=f"Lua execution error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/quickApp/{id}/files", tags=["QuickApp methods"])
        async def create_QuickApp_Files(id: int, file: QAFileSpec, response: Response):
            """Create QuickApp file"""
            try:
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
                result = self.interpreter.execute_lua_code(
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
            # Build the full path with query parameters
            path = f"/api/proxy?url={query.url}"
            
            try:
                result = self.interpreter.execute_lua_code(
                    f"return _PY.fibaroapi('GET', '{path}')"
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
