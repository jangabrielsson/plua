"""
Python functions library for Lua integration
Decorators and utilities for exporting Python functions to Lua's _PY table
"""

import os
import json
from typing import Any, Callable, Dict, List, Tuple, Union
from functools import wraps


class LuaExporter:
    """
    Manages Python functions that are exported to Lua's _PY table
    """
    
    def __init__(self):
        self.exported_functions: Dict[str, Callable] = {}
        self.function_metadata: Dict[str, Dict[str, str]] = {}  # Store function metadata
    
    def export(self, name: str = None, description: str = None, category: str = "general", inject_runtime: bool = False):
        """
        Decorator to export a Python function to Lua's _PY table
        
        Args:
            name: Optional name for the function in Lua (defaults to function name)
            description: Description of what the function does
            category: Category for organizing functions (e.g., "html", "file", "network")
            inject_runtime: Whether to inject lua_runtime as first parameter
        
        Usage:
            @lua_exporter.export()
            def my_function():
                return "hello"
                
            @lua_exporter.export("customName", description="Does something cool", category="utility")
            def another_function():
                return {"key": "value"}
                
            @lua_exporter.export(inject_runtime=True)
            def runtime_function(lua_runtime):
                return lua_runtime.table()
        """
        def decorator(func: Callable) -> Callable:
            # Use provided name or function name
            lua_name = name if name is not None else func.__name__
            
            # Store metadata
            self.function_metadata[lua_name] = {
                "description": description or func.__doc__ or "No description available",
                "category": category,
                "inject_runtime": inject_runtime
            }
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Inject lua_runtime if requested
                if inject_runtime and hasattr(wrapper, '_lua_runtime'):
                    args = (wrapper._lua_runtime,) + args
                
                # Call the original function
                result = func(*args, **kwargs)
                
                # Convert Python types to Lua-compatible types
                # We'll set the lua_runtime when we register the function
                return self._convert_to_lua(result, getattr(wrapper, '_lua_runtime', None))
            
            # Store the wrapped function
            self.exported_functions[lua_name] = wrapper
            return func  # Return original function unchanged
            
        return decorator
    
    def _convert_to_lua(self, value: Any, lua_runtime=None) -> Any:
        """
        Convert Python values to Lua-compatible types
        
        Args:
            value: Python value to convert
            lua_runtime: Optional Lua runtime for creating Lua tables
            
        Returns:
            Lua-compatible value
        """
        if value is None:
            return None
        elif isinstance(value, (bool, int, float, str)):
            # Basic types are compatible
            return value
        elif isinstance(value, dict):
            # Convert dict to Lua table if runtime available, otherwise keep as dict
            if lua_runtime:
                lua_table = lua_runtime.table()
                for k, v in value.items():
                    lua_table[k] = self._convert_to_lua(v, lua_runtime)
                return lua_table
            else:
                return {k: self._convert_to_lua(v, lua_runtime) for k, v in value.items()}
        elif isinstance(value, tuple):
            # Preserve tuples for lupa's unpack_returned_tuples feature
            return tuple(self._convert_to_lua(item, lua_runtime) for item in value)
        elif isinstance(value, list):
            # Convert list to Lua table if runtime available
            if lua_runtime:
                lua_table = lua_runtime.table()
                for i, item in enumerate(value, 1):  # Lua tables are 1-indexed
                    lua_table[i] = self._convert_to_lua(item, lua_runtime)
                return lua_table
            else:
                return [self._convert_to_lua(item, lua_runtime) for item in value]
        else:
            # For other types, convert to string representation
            return str(value)
    
    def get_exported_functions(self) -> Dict[str, Callable]:
        """
        Get all exported functions
        
        Returns:
            Dictionary of function names to wrapped functions
        """
        return self.exported_functions.copy()
    
    def get_function_metadata(self) -> Dict[str, Dict[str, str]]:
        """
        Get metadata for all exported functions
        
        Returns:
            Dictionary of function names to metadata
        """
        return self.function_metadata.copy()
    
    def list_functions_by_category(self) -> Dict[str, List[str]]:
        """
        Get functions grouped by category
        
        Returns:
            Dictionary of category names to lists of function names
        """
        categories = {}
        for func_name, metadata in self.function_metadata.items():
            category = metadata["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(func_name)
        return categories


# Global exporter instance
lua_exporter = LuaExporter()


# Exported Python functions for Lua
@lua_exporter.export(description="Get the current working directory", category="file")
def getcwd() -> str:
    """
    Get the current working directory
    
    Returns:
        Current working directory path
    """
    return os.getcwd()


@lua_exporter.export(description="Get an environment variable value", category="system")
def getenv(name: str, default: str = None) -> str:
    """
    Get an environment variable
    
    Args:
        name: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value or default
    """
    return os.getenv(name, default)


@lua_exporter.export(description="List directory contents", category="file")
def listdir(path: str = ".") -> List[str]:
    """
    List directory contents
    
    Args:
        path: Directory path to list (defaults to current directory)
        
    Returns:
        List of filenames in the directory
    """
    try:
        return os.listdir(path)
    except OSError as e:
        # Return error info that Lua can handle
        return {"error": str(e)}


@lua_exporter.export(description="Get detailed information about a file or directory path", category="file")
def path_info(path: str) -> Dict[str, Any]:
    """
    Get information about a path
    
    Args:
        path: Path to examine
        
    Returns:
        Dictionary with path information
    """
    try:
        stat = os.stat(path)
        return {
            "exists": True,
            "is_file": os.path.isfile(path),
            "is_dir": os.path.isdir(path),
            "size": stat.st_size,
            "basename": os.path.basename(path),
            "dirname": os.path.dirname(path),
            "abspath": os.path.abspath(path)
        }
    except OSError:
        return {
            "exists": False,
            "is_file": False,
            "is_dir": False,
            "size": 0,
            "basename": os.path.basename(path),
            "dirname": os.path.dirname(path),
            "abspath": os.path.abspath(path)
        }


@lua_exporter.export(description="Example function demonstrating multiple return values", category="example")
def multiple_values_example() -> Tuple[str, int, Dict[str, str]]:
    """
    Example function that returns multiple values to Lua
    
    Returns:
        Tuple of multiple values (Lua will unpack these)
    """
    return "hello", 42, {"status": "ok", "message": "multiple values work"}


@lua_exporter.export(description="Encode a Lua table to JSON string", category="json")
def json_encode(lua_table) -> str:
    """
    Encode a Lua table to JSON string
    
    Args:
        lua_table: Lua table or Python dict/list to encode
        
    Returns:
        JSON string representation
    """
    try:
        # Convert Lua table to Python object first
        python_obj = _lua_to_python(lua_table)
        return json.dumps(python_obj, ensure_ascii=False, separators=(',', ':'))
    except Exception as e:
        # Return JSON error object instead of raising
        return json.dumps({"error": f"JSON encoding failed: {str(e)}"})


@lua_exporter.export(description="Decode JSON string to Lua table", category="json")
def json_decode(json_string: str):
    """
    Decode JSON string to Lua table
    
    Args:
        json_string: JSON string to decode
        
    Returns:
        Lua table representation of the JSON data
    """
    try:
        # Parse JSON string to Python object
        python_obj = json.loads(json_string)
        # Return the Python object and let the exporter convert it to Lua
        return python_obj
    except json.JSONDecodeError as e:
        # Return error object that will be converted to Lua table
        return {"error": f"JSON parsing failed: {str(e)}", "valid": False}
    except Exception as e:
        # Handle other errors
        return {"error": f"JSON decoding failed: {str(e)}", "valid": False}


def _lua_to_python(lua_value):
    """
    Convert Lua values to Python objects for JSON serialization
    
    Args:
        lua_value: Lua value (table, string, number, etc.)
        
    Returns:
        Python object (dict, list, str, int, float, bool, None)
    """
    # Handle None/nil
    if lua_value is None:
        return None
    
    # Handle basic types
    if isinstance(lua_value, (str, int, float, bool)):
        return lua_value
    
    # Check if it's a Lua table (has table interface)
    if hasattr(lua_value, 'keys') and hasattr(lua_value, 'values'):
        # It's a Lua table - determine if it's array-like or object-like
        try:
            # Get all keys
            keys = list(lua_value.keys())
            
            # Check if it's an array (consecutive integers starting from 1)
            if keys and all(isinstance(k, int) for k in keys):
                # Sort keys to check for consecutiveness
                sorted_keys = sorted(keys)
                if sorted_keys[0] == 1 and sorted_keys == list(range(1, len(sorted_keys) + 1)):
                    # It's an array-like table
                    return [_lua_to_python(lua_value[i]) for i in sorted_keys]
            
            # It's an object-like table
            result = {}
            for key in keys:
                # Convert key to string if needed
                str_key = str(key) if not isinstance(key, str) else key
                result[str_key] = _lua_to_python(lua_value[key])
            return result
            
        except Exception:
            # Fallback: treat as object
            result = {}
            try:
                for key, value in lua_value.items():
                    str_key = str(key) if not isinstance(key, str) else key
                    result[str_key] = _lua_to_python(value)
                return result
            except Exception:
                # Last resort: convert to string
                return str(lua_value)
    
    # For other types, convert to string
    return str(lua_value)


@lua_exporter.export(description="Get environment variable with .env file support", category="system")
def getenv_with_dotenv(name: str, default: str = None) -> str:
    """
    Get an environment variable, checking .env file first
    
    Args:
        name: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value from .env file, system env, or default
    """
    import os
    
    # First try to read from .env file in current working directory
    env_file_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_file_path):
        try:
            with open(env_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        if key == name:
                            return value
        except (IOError, OSError):
            # If we can't read the .env file, fall back to system env
            pass
    
    # Fall back to system environment variable
    return os.getenv(name, default)


@lua_exporter.export(description="Get environment variable with .env file support (alias for getenv_with_dotenv)", category="system")
def getenv_dotenv(name: str, default: str = None) -> str:
    """
    Alias for getenv_with_dotenv - Get an environment variable, checking .env file first
    
    Args:
        name: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value from .env file, system env, or default
    """
    return getenv_with_dotenv(name, default)


@lua_exporter.export(description="Get system configuration and environment information", category="system")
def get_config() -> Dict[str, Any]:
    """
    Get system configuration and environment information
    
    Returns:
        Dictionary with system configuration information
    """
    import os
    import platform
    import sys
    
    config = {
        # Directories
        "homedir": os.path.expanduser("~"),
        "cwd": os.getcwd(),
        "tempdir": os.path.join(os.path.expanduser("~"), "tmp") if platform.system() != "Windows" else os.environ.get("TEMP", "C:\\temp"),
        
        # Path separators
        "fileseparator": os.sep,
        "pathseparator": os.pathsep,
        
        # Platform information
        "platform": platform.system().lower(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        
        # Environment flags
        "debug": getenv_dotenv("DEBUG", "false").lower() in ("true", "1", "yes", "on"),
        "production": getenv_dotenv("PRODUCTION", "false").lower() in ("true", "1", "yes", "on"),
        
        # User information
        "username": os.getenv("USER") or os.getenv("USERNAME") or "unknown",
        
        # Common environment variables
        "path": os.getenv("PATH", ""),
        "lang": os.getenv("LANG", "en_US.UTF-8"),
        
        # Plua2 specific
        "plua2_version": "0.1.0",
        "lua_version": "5.4"
    }
    
    return config


@lua_exporter.export(description="Make a synchronous HTTP call from Lua", category="network")
def http_call_sync(method, url, data=None, headers=None):
    """Make a synchronous HTTP call from Lua"""
    import requests
    
    try:
        method = method.upper()
        
        # Default headers
        if headers is None:
            headers = {}
        
        # Make the HTTP request
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            return {"success": False, "error": f"Unsupported HTTP method: {method}"}
        
        # Return response data
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.text,
            "headers": dict(response.headers)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@lua_exporter.export(description="Make internal HTTP call to our own FastAPI server", category="network")
def http_call_internal(method, path, data=None, headers=None):
    """Make internal HTTP call to our own FastAPI server by calling function directly"""
    
    # Get the interpreter via the runtime reference (same pattern as network module)
    from . import network
    runtime = network._current_runtime
    if not runtime:
        return {"success": False, "error": "Runtime not available"}
    
    interpreter = runtime.interpreter
    if not interpreter:
        return {"success": False, "error": "Interpreter not available"}
    
    try:
        # Extract the endpoint and parameters from the path
        if path.startswith("/api/"):
            # Parse query parameters from the path if present
            import urllib.parse
            import re
            parsed_url = urllib.parse.urlparse(path)
            clean_path = parsed_url.path
            query_params = urllib.parse.parse_qs(parsed_url.query) if parsed_url.query else {}
            
            # Extract path parameters by matching against common FastAPI patterns
            path_params = {}
            template_path = clean_path  # Default to original path if no template matches
            
            # Common Fibaro API path patterns with their templates
            patterns = [
                (r'^/api/devices/(\d+)$', '/api/devices/{deviceID}', ['deviceID']),
                (r'^/api/devices/(\d+)/action/(.+)$', '/api/devices/{deviceID}/action/{actionName}', ['deviceID', 'actionName']),
                (r'^/api/devices/(\d+)/properties/(.+)$', '/api/devices/{deviceID}/properties/{propertyName}', ['deviceID', 'propertyName']),
                (r'^/api/rooms/(\d+)$', '/api/rooms/{roomID}', ['roomID']),
                (r'^/api/scenes/(\d+)$', '/api/scenes/{sceneID}', ['sceneID']),
                (r'^/api/users/(\d+)$', '/api/users/{userID}', ['userID']),
                (r'^/api/sections/(\d+)$', '/api/sections/{sectionID}', ['sectionID']),
                (r'^/api/profiles/(\d+)$', '/api/profiles/{profileId}', ['profileId']),
                (r'^/api/quickApp/(\d+)/files/(.+)$', '/api/quickApp/{deviceId}/files/{fileName}', ['deviceId', 'fileName']),
                (r'^/api/quickApp/(\d+)/files$', '/api/quickApp/{deviceId}/files', ['deviceId']),
                (r'^/api/RGBPrograms/(\d+)$', '/api/RGBPrograms/{programID}', ['programID']),
                (r'^/api/notificationCenter/(\d+)$', '/api/notificationCenter/{notificationId}', ['notificationId']),
                (r'^/api/energy/(\d+)/(\d+)/([^/]+)/([^/]+)/([^/]+)/(\d+)$', '/api/energy/{timestampFrom}/{timestampTo}/{dataSet}/{type}/{unit}/{id}', ['timestampFrom', 'timestampTo', 'dataSet', 'type', 'unit', 'id']),
                (r'^/api/temperature/(\d+)/(\d+)/([^/]+)/([^/]+)/temperature/(\d+)$', '/api/temperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/temperature/{id}', ['timestampFrom', 'timestampTo', 'dataSet', 'type', 'id']),
                (r'^/api/smokeTemperature/(\d+)/(\d+)/([^/]+)/([^/]+)/smoke/(\d+)$', '/api/smokeTemperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/smoke/{id}', ['timestampFrom', 'timestampTo', 'dataSet', 'type', 'id']),
                (r'^/api/thermostatTemperature/(\d+)/(\d+)/([^/]+)/([^/]+)/thermostat/(\d+)$', '/api/thermostatTemperature/{timestampFrom}/{timestampTo}/{dataSet}/{type}/thermostat/{id}', ['timestampFrom', 'timestampTo', 'dataSet', 'type', 'id']),
                (r'^/api/deviceNotifications/v1/(\d+)$', '/api/deviceNotifications/v1/{deviceID}', ['deviceID']),
                (r'^/api/panels/favoriteColors/v2/(\d+)$', '/api/panels/favoriteColors/v2/{favoriteColorID}', ['favoriteColorID']),
                (r'^/api/devices/action/(\d+)/(\d+)$', '/api/devices/action/{timestamp}/{id}', ['timestamp', 'id']),
                (r'^/api/slave/([^/]+)/api/devices/(\d+)$', '/api/slave/{uuid}/api/devices/{deviceID}', ['uuid', 'deviceID']),
                (r'^/api/slave/([^/]+)/api/devices/(\d+)/action/(.+)$', '/api/slave/{uuid}/api/devices/{deviceID}/action/{actionName}', ['uuid', 'deviceID', 'actionName']),
                (r'^/api/energy/installationCost/(\d+)$', '/api/energy/installationCost/{id}', ['id']),
                (r'^/api/energy/consumption/room/(\d+)/detail$', '/api/energy/consumption/room/{roomId}/detail', ['roomId']),
                (r'^/api/energy/consumption/device/(\d+)/detail$', '/api/energy/consumption/device/{deviceId}/detail', ['deviceId']),
                (r'^/api/linkedDevices/v1/devices/(\d+)$', '/api/linkedDevices/v1/devices/{deviceID}', ['deviceID']),
                (r'^/api/additionalInterfaces/([^/]+)$', '/api/additionalInterfaces/{interfaceName}', ['interfaceName']),
                (r'^/api/fti/v2/changeStep/([^/]+)$', '/api/fti/v2/changeStep/{step}', ['step']),
                (r'^/api/devices/groupAction/([^/]+)$', '/api/devices/groupAction/{actionName}', ['actionName']),
                (r'^/api/quickApp/export/(\d+)$', '/api/quickApp/export/{deviceId}', ['deviceId']),
                (r'^/api/service/slaves/([^/]+)$', '/api/service/slaves/{id}', ['id']),
                (r'^/api/service/slaves/([^/]+)/password$', '/api/service/slaves/{id}/password', ['id']),
                (r'^/api/service/slaves/([^/]+)/ip$', '/api/service/slaves/{serialOrId}/ip', ['serialOrId']),
                (r'^/api/service/discovery/resolve/([^/]+)/([^/]+)$', '/api/service/discovery/resolve/{type}/{value}', ['type', 'value']),
                (r'^/api/service/resolve/([^/]+)/([^/]+)$', '/api/service/resolve/{type}/{value}', ['type', 'value']),
            ]
            
            for pattern, template, param_names in patterns:
                match = re.match(pattern, clean_path)
                if match:
                    template_path = template
                    for i, param_name in enumerate(param_names):
                        if i < len(match.groups()):
                            path_params[param_name] = match.group(i + 1)
                    break
            
            # Convert data to JSON string if it exists
            data_json = "nil"
            if data is not None:
                import json
                data_json = json.dumps(data)
                data_json = f'"{data_json}"'  # Wrap in quotes for Lua string
            
            # Convert query params to Lua table format
            query_lua = "nil"
            if query_params:
                query_items = []
                for key, values in query_params.items():
                    # Take first value if multiple values for same key
                    value = values[0] if values else ""
                    query_items.append(f'["{key}"] = "{value}"')
                query_lua = "{" + ", ".join(query_items) + "}"
            
            # Convert path params to Lua table format
            path_lua = "nil"
            if path_params:
                path_items = []
                for key, value in path_params.items():
                    path_items.append(f'["{key}"] = "{value}"')
                path_lua = "{" + ", ".join(path_items) + "}"
            
            # Execute Lua script to call the fibaro_api_hook function
            lua_script = f"""
if _PY.fibaro_api_hook then
    local result, status = _PY.fibaro_api_hook("{method}", "{template_path}", {path_lua}, {query_lua}, {data_json})
    _PY.temp_internal_call_result = {{
        success = true,
        status_code = status or 200,
        data = result,
        headers = {{["Content-Type"] = "application/json"}}
    }}
else
    _PY.temp_internal_call_result = {{
        success = false,
        error = "fibaro_api_hook not available"
    }}
end
"""
            
            # Execute the script
            interpreter.execute_script(lua_script, "internal_http_call")
            
            # Get the result from Lua globals
            result = interpreter.lua.globals()._PY.temp_internal_call_result
            
            # Clean up
            interpreter.lua.globals()._PY.temp_internal_call_result = None
            
            # Convert the Lua table to Python dict
            if result:
                python_result = _lua_to_python(result)
                return python_result
            else:
                return {"success": False, "error": "No result from fibaro_api_hook"}
                
        else:
            return {"success": False, "error": f"Unknown internal path: {path}"}
            
    except Exception as e:
        return {"success": False, "error": f"Internal call failed: {str(e)}"}


def set_global_fastapi_app(app):
    """Set the global FastAPI app reference for internal calls"""
    # Get the interpreter via the runtime reference  
    from . import network
    runtime = network._current_runtime
    if runtime and runtime.interpreter:
        runtime.interpreter.set_fastapi_app(app)


def get_fastapi_app():
    """Get the FastAPI app reference"""
    from . import network
    runtime = network._current_runtime
    if runtime and runtime.interpreter:
        return runtime.interpreter._fastapi_app
    return None


@lua_exporter.export(description="Base64 encode a string", category="utility")
def base64_encode(data):
    """Encode data as base64"""
    import base64
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.b64encode(data).decode('utf-8')


@lua_exporter.export(description="Base64 decode a string", category="utility")
def base64_decode(data):
    """Decode base64 data"""
    import base64
    return base64.b64decode(data).decode('utf-8')

