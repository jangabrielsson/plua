"""
Embedded API Server for PLua (single-process, always started by PLua)
Do NOT run this file directly.
"""

import os
import sys
import threading
import time
from datetime import datetime
from typing import Optional, Any, List

# Add the project root to the path so we can import api_server
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel, Field
    import uvicorn
    import httpx
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install with: pip install fastapi uvicorn httpx")
    raise


class EmbeddedAPIServer:
    """Embedded FastAPI server that runs within the PLua interpreter process"""
    
    def __init__(self, interpreter, host="127.0.0.1", port=8000):
        self.interpreter = interpreter
        self.host = host
        self.port = port
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
    
    def create_app(self):
        """Create the FastAPI application"""
        app = FastAPI(
            title="PLua API Server",
            description="API server for PLua interpreter",
            version="1.0.0"
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
        
        # API endpoints
        @app.get("/", response_class=HTMLResponse)
        async def root():
            """Web interface"""
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>PLua Web Interface</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .header { background: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                    .code-input { width: 100%; height: 200px; font-family: monospace; }
                    .output { background: #f8f8f8; padding: 10px; border-radius: 5px; white-space: pre-wrap; }
                    .button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
                    .button:hover { background: #005a87; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>PLua Web Interface</h1>
                        <p>Execute Lua code in the embedded PLua interpreter</p>
                    </div>
                    
                    <div>
                        <textarea id="code" class="code-input" placeholder="Enter Lua code here...">print("Hello from PLua!")</textarea>
                        <br><br>
                        <button onclick="executeCode()" class="button">Execute</button>
                        <button onclick="clearOutput()" class="button">Clear Output</button>
                        <br><br>
                        <div id="output" class="output"></div>
                    </div>
                </div>
                
                <script>
                    async function executeCode() {
                        const code = document.getElementById('code').value;
                        const output = document.getElementById('output');
                        
                        output.textContent = 'Executing...';
                        
                        try {
                            const response = await fetch('/api/execute', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ code: code })
                            });
                            
                            const result = await response.json();
                            
                            if (result.success) {
                                output.innerHTML = result.result || 'Code executed successfully';
                            } else {
                                output.innerHTML = 'Error: ' + result.error;
                            }
                        } catch (error) {
                            output.innerHTML = 'Error: ' + error.message;
                        }
                    }
                    
                    function clearOutput() {
                        document.getElementById('output').textContent = '';
                    }
                </script>
            </body>
            </html>
            """
        
        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "plua_mode": True,
                "server_ready": True,
                "interpreter_available": True
            }
        
        @app.post("/api/execute", response_model=ExecuteResponse)
        async def execute_lua_code(request: ExecuteRequest):
            """Execute Lua code"""
            start_time = time.time()
            
            try:
                # Set a reasonable timeout for execution
                timeout = request.timeout or 30
                
                # Execute the code using the interpreter with timeout handling
                import asyncio
                import concurrent.futures
                
                # Run the execution in a thread pool to handle timeouts
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = loop.run_in_executor(
                        executor, 
                        self.interpreter.execute_lua_code, 
                        request.code
                    )
                    
                    try:
                        result = await asyncio.wait_for(future, timeout=timeout)
                    except asyncio.TimeoutError:
                        return ExecuteResponse(
                            success=False,
                            error=f"Execution timed out after {timeout} seconds",
                            session_id=request.session_id,
                            execution_time=time.time() - start_time
                        )
                
                execution_time = time.time() - start_time
                
                return ExecuteResponse(
                    success=result["success"],
                    result=result.get("result"),
                    error=result.get("error"),
                    session_id=request.session_id,
                    execution_time=execution_time
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                return ExecuteResponse(
                    success=False,
                    error=str(e),
                    session_id=request.session_id,
                    execution_time=execution_time
                )
        
        @app.get("/api/status")
        async def get_status():
            """Get interpreter status"""
            return {
                "status": "running",
                "interpreter_available": True,
                "timestamp": datetime.now().isoformat()
            }
        
        @app.post("/api/restart")
        async def restart_interpreter():
            """Restart the interpreter (reinitialize Lua environment)"""
            try:
                # Reinitialize the Lua environment
                self.interpreter.setup_lua_environment()
                return {"status": "restarted", "message": "Interpreter restarted successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to restart: {str(e)}")
        
        # Fibaro API endpoints
        @app.get("/api/devices")
        async def get_devices(request: Request):
            """Get devices (Fibaro API simulation)"""
            try:
                # Extract query parameters
                query_params = dict(request.query_params)
                
                # Use the interpreter's Lua runtime to call PY.fibaroapi
                lua_runtime = self.interpreter.get_lua_runtime()
                if hasattr(lua_runtime.globals(), '_PY') and hasattr(lua_runtime.globals()['_PY'], 'fibaroapi'):
                    # Call the generic fibaroapi function
                    result = lua_runtime.globals()['_PY']['fibaroapi']("GET", "/api/devices", None, query_params)
                    # Convert Lua table to Python dict/list
                    from plua.interpreter import lua_to_python
                    result = lua_to_python(result)
                    
                    # Check if this is a redirect response
                    if isinstance(result, dict) and result.get('_redirect'):
                        # Handle redirect to external HC3 server
                        external_result, status_code = await self._handle_redirect(
                            result, "GET", "/api/devices", None, query_params, dict(request.headers)
                        )
                        return external_result
                    
                    return result
                else:
                    # Return mock data if fibaroapi not available
                    return [
                        {"id": 1, "name": "Device 1", "type": "device"},
                        {"id": 2, "name": "Device 2", "type": "device"}
                    ]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/devices/{id}")
        async def get_device(id: int, request: Request):
            """Get specific device"""
            try:
                # Extract query parameters
                query_params = dict(request.query_params)
                
                # Use the interpreter's Lua runtime to call PY.fibaroapi
                lua_runtime = self.interpreter.get_lua_runtime()
                if hasattr(lua_runtime.globals(), '_PY') and hasattr(lua_runtime.globals()['_PY'], 'fibaroapi'):
                    # Call the generic fibaroapi function
                    result = lua_runtime.globals()['_PY']['fibaroapi']("GET", f"/api/devices/{id}", None, query_params)
                    # Convert Lua table to Python dict/list
                    from plua.interpreter import lua_to_python
                    result = lua_to_python(result)
                    
                    # Check if this is a redirect response
                    if isinstance(result, dict) and result.get('_redirect'):
                        # Handle redirect to external HC3 server
                        external_result, status_code = await self._handle_redirect(
                            result, "GET", f"/api/devices/{id}", None, query_params, dict(request.headers)
                        )
                        return external_result
                    
                    return result
                else:
                    return {"id": id, "name": f"Device {id}", "type": "device"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/globalVariables")
        async def get_global_variables(request: Request):
            """Get global variables"""
            try:
                # Extract query parameters
                query_params = dict(request.query_params)
                
                # Use the interpreter's Lua runtime to call PY.fibaroapi
                lua_runtime = self.interpreter.get_lua_runtime()
                if hasattr(lua_runtime.globals(), '_PY') and hasattr(lua_runtime.globals()['_PY'], 'fibaroapi'):
                    # Call the generic fibaroapi function
                    result = lua_runtime.globals()['_PY']['fibaroapi']("GET", "/api/globalVariables", None, query_params)
                    # Convert Lua table to Python dict/list
                    from plua.interpreter import lua_to_python
                    result = lua_to_python(result)
                    
                    # Check if this is a redirect response
                    if isinstance(result, dict) and result.get('_redirect'):
                        # Handle redirect to external HC3 server
                        external_result, status_code = await self._handle_redirect(
                            result, "GET", "/api/globalVariables", None, query_params, dict(request.headers)
                        )
                        return external_result
                    
                    return result
                else:
                    return {"var1": "value1", "var2": "value2"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/globalVariables/{name}")
        async def get_global_variable(name: str, request: Request):
            """Get specific global variable"""
            try:
                # Extract query parameters
                query_params = dict(request.query_params)
                
                # Use the interpreter's Lua runtime to call PY.fibaroapi
                lua_runtime = self.interpreter.get_lua_runtime()
                if hasattr(lua_runtime.globals(), '_PY') and hasattr(lua_runtime.globals()['_PY'], 'fibaroapi'):
                    # Call the generic fibaroapi function
                    result = lua_runtime.globals()['_PY']['fibaroapi']("GET", f"/api/globalVariables/{name}", None, query_params)
                    # Convert Lua table to Python dict/list
                    from plua.interpreter import lua_to_python
                    result = lua_to_python(result)
                    
                    # Check if this is a redirect response
                    if isinstance(result, dict) and result.get('_redirect'):
                        # Handle redirect to external HC3 server
                        external_result, status_code = await self._handle_redirect(
                            result, "GET", f"/api/globalVariables/{name}", None, query_params, dict(request.headers)
                        )
                        return external_result
                    
                    return {"name": name, "value": result}
                else:
                    return {"name": name, "value": f"mock_value_for_{name}"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Add more Fibaro API endpoints as needed...
        
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
                config = uvicorn.Config(
                    self.app,
                    host=self.host,
                    port=self.port,
                    log_level="info",
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
                print("Warning: Embedded API server may not have started properly")
            else:
                print(f"Embedded API server started on http://{self.host}:{self.port}")
            
        except Exception as e:
            print(f"Failed to start embedded API server: {e}")
            self.running = False
    
    def stop(self):
        """Stop the API server"""
        if self.server and self.running:
            self.server.should_exit = True
            self.running = False
            print("Embedded API server stopped")
    
    def is_running(self):
        """Check if the server is running"""
        return self.running 