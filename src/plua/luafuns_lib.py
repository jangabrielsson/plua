"""
Python functions library for Lua integration
Decorators and utilities for exporting Python functions to Lua's _PY table
"""

import os
import sys
import time
import json
from typing import Any, Callable, Dict, List, Tuple
from functools import wraps
import requests
from datetime import datetime
from collections import deque
from threading import Thread, Lock
import socket


def _python_to_lua_table(lua_runtime, python_obj):
    """Recursively convert Python object to Lua table"""
    if python_obj is None:
        return None
    elif isinstance(python_obj, (str, int, float, bool)):
        return python_obj
    elif isinstance(python_obj, list):
        # Convert list to Lua table with 1-based indexing
        lua_table = lua_runtime.table()
        for i, item in enumerate(python_obj, 1):
            lua_table[i] = _python_to_lua_table(lua_runtime, item)
        return lua_table
    elif isinstance(python_obj, dict):
        # Convert dict to Lua table
        lua_table = lua_runtime.table()
        for key, value in python_obj.items():
            lua_table[key] = _python_to_lua_table(lua_runtime, value)
        return lua_table
    else:
        # For any other type, try to convert to string
        return str(python_obj)


class LuaExporter:
    """
    Manages Python functions that are exported to Lua's _PY table
    """

    def __init__(self):
        self.exported_functions: Dict[str, Callable] = {}
        self.function_metadata: Dict[str, Dict[str, str]] = {}  # Store function metadata

    def export(self, name: str = None, description: str = None, category: str = "general", inject_runtime: bool = False, user_facing: bool = False):
        """
        Decorator to export a Python function to Lua's _PY table

        Args:
            name: Optional name for the function in Lua (defaults to function name)
            description: Description of what the function does
            category: Category for organizing functions (e.g., "html", "file", "network")
            inject_runtime: Whether to inject lua_runtime as first parameter
            user_facing: Whether this function is intended for end-user Lua scripts (vs internal plua use)

        Usage:
            @lua_exporter.export()
            def my_function():
                return "hello"

            @lua_exporter.export("customName", description="Does something cool", category="utility", user_facing=True)
            def another_function():
                return {"key": "value"}

            @lua_exporter.export(inject_runtime=True, user_facing=False)
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
                "inject_runtime": inject_runtime,
                "user_facing": user_facing
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

    def list_user_facing_functions(self) -> List[str]:
        """
        Get list of functions marked as user-facing

        Returns:
            List of function names that are intended for end users
        """
        return [
            func_name for func_name, metadata in self.function_metadata.items()
            if metadata.get("user_facing", False)
        ]

    def list_internal_functions(self) -> List[str]:
        """
        Get list of functions marked as internal

        Returns:
            List of function names that are for internal plua use
        """
        return [
            func_name for func_name, metadata in self.function_metadata.items()
            if not metadata.get("user_facing", False)
        ]

    def list_functions_by_user_facing(self) -> Dict[str, List[str]]:
        """
        Get functions grouped by user_facing status

        Returns:
            Dictionary with 'user_facing' and 'internal' keys mapping to lists of function names
        """
        return {
            "user_facing": self.list_user_facing_functions(),
            "internal": self.list_internal_functions()
        }

    def list_user_facing_by_category(self) -> Dict[str, List[str]]:
        """
        Get user-facing functions grouped by category

        Returns:
            Dictionary of category names to lists of user-facing function names
        """
        categories = {}
        for func_name, metadata in self.function_metadata.items():
            if metadata.get("user_facing", False):
                category = metadata["category"]
                if category not in categories:
                    categories[category] = []
                categories[category].append(func_name)
        return categories


# Global exporter instance
lua_exporter = LuaExporter()


# Function introspection exports - for Lua scripts to explore available functions
@lua_exporter.export(description="List all user-facing functions in _PY table", category="introspection", user_facing=True)
def list_user_functions() -> List[str]:
    """Get list of functions intended for end-user Lua scripts"""
    return lua_exporter.list_user_facing_functions()


@lua_exporter.export(description="List user-facing functions grouped by category", category="introspection", user_facing=True)
def list_user_functions_by_category() -> Dict[str, List[str]]:
    """Get user-facing functions organized by category"""
    return lua_exporter.list_user_facing_by_category()


@lua_exporter.export(description="Get metadata for all _PY functions", category="introspection", user_facing=True)
def get_function_info() -> Dict[str, Dict[str, Any]]:
    """Get complete metadata for all exported functions"""
    return lua_exporter.get_function_metadata()


@lua_exporter.export(description="Get functions grouped by user_facing status", category="introspection")
def list_functions_by_user_facing() -> Dict[str, List[str]]:
    """Get functions split into user_facing and internal categories"""
    return lua_exporter.list_functions_by_user_facing()


# Exported Python functions for Lua
@lua_exporter.export(description="Get current epoch time with milliseconds as float", category="time", user_facing=True)
def millitime() -> float:
    """
    Return the current epoch time as a float with milliseconds in the decimal part.
    """
    return time.time()


@lua_exporter.export(description="Get the current working directory", category="file", user_facing=True)
def getcwd() -> str:
    """
    Get the current working directory

    Returns:
        Current working directory path
    """
    return os.getcwd()


@lua_exporter.export(description="Get an environment variable value", category="system", user_facing=True)
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


@lua_exporter.export(description="List directory contents", category="file", user_facing=True)
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


@lua_exporter.export(description="Read the entire contents of a file", category="file", user_facing=True)
def readFile(path: str) -> str:
    """
    Read the entire contents of a file

    Args:
        path: File path to read

    Returns:
        File contents as string

    Raises:
        Exception if file cannot be read
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading file '{path}': {str(e)}")


@lua_exporter.export(description="Write content to a file", category="file", user_facing=True)
def writeFile(path: str, content: str) -> None:
    """
    Write content to a file, creating or overwriting it

    Args:
        path: File path to write to
        content: Content to write

    Raises:
        Exception if file cannot be written
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"Error writing file '{path}': {str(e)}")


@lua_exporter.export(description="Check if a file or directory exists", category="file", user_facing=True)
def fileExist(path: str) -> bool:
    """
    Check if a file or directory exists

    Args:
        path: Path to check

    Returns:
        True if the path exists, False otherwise
    """
    if path is None:
        return False
    return os.path.exists(path)


@lua_exporter.export(description="Example function demonstrating multiple return values", category="example")
def multiple_values_example() -> Tuple[str, int, Dict[str, str]]:
    """
    Example function that returns multiple values to Lua

    Returns:
        Tuple of multiple values (Lua will unpack these)
    """
    return "hello", 42, {"status": "ok", "message": "multiple values work"}


@lua_exporter.export(description="Encode a Lua table to JSON string", category="json", user_facing=True)
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


@lua_exporter.export(description="Encode a Lua table to JSON string formated", category="json", user_facing=True)
def json_encode_formated(lua_table) -> str:
    """
    Encode a Lua table to JSON string formated

    Args:
        lua_table: Lua table or Python dict/list to encode

    Returns:
        JSON string representation formated
    """
    try:
        # Convert Lua table to Python object first
        python_obj = _lua_to_python(lua_table)
        return json.dumps(python_obj, ensure_ascii=False, indent=4, separators=(',', ': '))
    except Exception as e:
        # Return JSON error object instead of raising
        return json.dumps({"error": f"JSON encoding failed: {str(e)}"})


@lua_exporter.export(description="Decode JSON string to Lua table", category="json", user_facing=True)
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


@lua_exporter.export(description="Get system configuration and environment information", category="system", inject_runtime=True)
def get_config(lua_runtime) -> Dict[str, Any]:
    """
    Get system configuration and environment information

    Returns:
        Dictionary with system configuration information
    """
    import os
    import platform
    import sys
    from . import __version__

    def get_host_ip():
        try:
            # This method works even if not connected to the internet
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            try:
                # Doesn't have to be reachable
                s.connect(('10.255.255.255', 1))
                ip = s.getsockname()[0]
            except Exception:
                ip = '127.0.0.1'
            finally:
                s.close()
            return ip
        except Exception:
            return '127.0.0.1'

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
        # Plua specific
        "plua_version": __version__,
        "lua_version": "5.4",
        # HOST IP address
        "host_ip": get_host_ip(),
    }

    return config


@lua_exporter.export(description="Make a synchronous HTTP call from Lua", category="network", user_facing=True)
def http_call_sync(method, url, data=None, headers=None):
    """Make a synchronous HTTP call from Lua"""
    import requests

    try:
        method = method.upper()
        # Ensure data is a UTF-8 encoded string
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        elif isinstance(data, str):
            data = data.encode('utf-8')

        # Default headers
        if headers is None:
            headers = {}

        # Make the HTTP request
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, data=data, headers=headers, timeout=30)
        elif method == "PUT":
            response = requests.put(url, data=data, headers=headers, timeout=30)
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


@lua_exporter.export(description="Base64 encode a string", category="utility", user_facing=True)
def base64_encode(data):
    """Encode data as base64"""
    import base64
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.b64encode(data).decode('utf-8')


@lua_exporter.export(description="Base64 decode a string", category="utility", user_facing=True)
def base64_decode(data):
    """Decode base64 data"""
    import base64
    return base64.b64decode(data).decode('utf-8')


@lua_exporter.export(description="Open URL in VS Code Simple Browser", category="vscode", user_facing=True)
def open_in_vscode_browser(url):
    """Open a URL in VS Code's Simple Browser"""
    import subprocess
    # import os

    try:
        # Method 1: Try the command palette approach
        cmd1 = ["code", "--command", "simpleBrowser.show", "--args", url]
        result1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=3)

        if result1.returncode == 0:
            return {"success": True, "message": f"Opened {url} in VS Code Simple Browser (method 1)", "method": "command_palette"}

        # Method 2: Try opening a workspace file that triggers Simple Browser
        # This is a workaround using VS Code's URI scheme
        # cmd2 = ["code", "--command", "workbench.action.showCommands"]
        # result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=3)

        # Method 3: Try using VS Code's built-in command with different syntax
        cmd3 = ["code", "--command", "simpleBrowser.api.open", "--args", f'["{url}"]']
        result3 = subprocess.run(cmd3, capture_output=True, text=True, timeout=3)

        if result3.returncode == 0:
            return {"success": True, "message": f"Opened {url} in VS Code Simple Browser (method 3)", "method": "api_open"}

        # Method 4: Create a temporary file with VS Code command
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(f"""# Open Simple Browser

Click this link to open in Simple Browser:
- [Open Web Interface]({url})

Or use Command Palette:
1. Press Cmd+Shift+P (macOS) or Ctrl+Shift+P (Windows/Linux)
2. Type "Simple Browser: Show"
3. Enter URL: {url}
""")
            temp_file = f.name

        # Open the temp file in VS Code
        cmd4 = ["code", temp_file]
        result4 = subprocess.run(cmd4, capture_output=True, text=True, timeout=3)

        if result4.returncode == 0:
            return {
                "success": True,
                "message": f"Opened instructions in VS Code. Use Command Palette > 'Simple Browser: Show' > {url}",
                "method": "instruction_file",
                "temp_file": temp_file
            }

        # If all methods fail, try fallback
        import webbrowser
        webbrowser.open(url)
        return {
            "success": True,
            "message": f"Opened {url} in default browser (VS Code methods failed)",
            "method": "fallback",
            "debug": {
                "cmd1_result": result1.returncode,
                "cmd1_stderr": result1.stderr,
                "cmd3_result": result3.returncode,
                "cmd3_stderr": result3.stderr,
                "cmd4_result": result4.returncode,
                "cmd4_stderr": result4.stderr
            }
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "VS Code command timed out", "method": "timeout"}
    except FileNotFoundError:
        # VS Code not in PATH, try default browser
        try:
            import webbrowser
            webbrowser.open(url)
            return {"success": True, "message": f"Opened {url} in default browser (VS Code not found)", "method": "browser_fallback"}
        except Exception as e:
            return {"success": False, "error": f"Failed to open URL: {str(e)}", "method": "failed"}
    except Exception as e:
        return {"success": False, "error": f"Failed to open URL: {str(e)}", "method": "exception"}


@lua_exporter.export(description="Open plua web interface in VS Code", category="vscode", user_facing=True)
def open_web_interface():
    """Open the plua web interface in VS Code Simple Browser"""
    # Get the API server port from the current runtime
    try:
        from . import network

        runtime = network._current_runtime
        if runtime and hasattr(runtime, 'api_server') and runtime.api_server:
            port = runtime.api_server.port
            url = f"http://localhost:{port}/web"
        else:
            # Default port
            url = "http://localhost:8888/web"

        return open_in_vscode_browser(url)
    except Exception as e:
        return {"success": False, "error": f"Failed to get API server info: {str(e)}"}


@lua_exporter.export(description="Open plua web interface in default browser", category="browser", user_facing=True)
def open_web_interface_browser():
    """Open the plua web interface in the system's default browser"""
    import webbrowser
    
    try:
        from . import network

        runtime = network._current_runtime
        if runtime and hasattr(runtime, 'api_server') and runtime.api_server:
            port = runtime.api_server.port
            url = f"http://localhost:{port}/web"
        else:
            # Default port
            url = "http://localhost:8888/web"

        # Open in default browser
        webbrowser.open(url)
        return {"success": True, "message": f"Opened {url} in default browser", "url": url}
    except Exception as e:
        return {"success": False, "error": f"Failed to open web interface: {str(e)}"}


@lua_exporter.export(description="Open URL in default browser", category="browser", user_facing=True)
def open_browser(url):
    """Open a URL in the system's default browser"""
    import webbrowser
    try:
        webbrowser.open(url)
        return {"success": True, "message": f"Opened {url} in default browser"}
    except Exception as e:
        return {"success": False, "error": f"Failed to open URL: {str(e)}"}


@lua_exporter.export(description="List available browsers on the system", category="browser", user_facing=True)
def list_browsers():
    """List available browsers on the system"""
    import webbrowser
    
    browsers = []
    
    # Get the default browser
    try:
        default_browser = webbrowser.get()
        browsers.append({
            "name": "default",
            "description": f"Default browser: {default_browser.name}"
        })
    except Exception:
        browsers.append({
            "name": "default", 
            "description": "Default browser (unknown)"
        })
    
    # Try to get specific browsers
    browser_names = ["chrome", "firefox", "safari", "edge", "opera"]
    
    for browser_name in browser_names:
        try:
            browser = webbrowser.get(browser_name)
            browsers.append({
                "name": browser_name,
                "description": f"{browser_name.title()}: {browser.name}"
            })
        except Exception:
            # Browser not available, skip
            pass
    
    return browsers


@lua_exporter.export(description="Open URL in specific browser", category="browser", user_facing=True)
def open_browser_specific(url, browser_name):
    """Open a URL in a specific browser"""
    import webbrowser
    
    try:
        if browser_name.lower() == "default":
            browser = webbrowser.get()
        else:
            browser = webbrowser.get(browser_name)
        
        browser.open(url)
        return {"success": True, "message": f"Opened {url} in {browser_name}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to open {url} in {browser_name}: {str(e)}"}


# Global state for refresh states polling
_refresh_thread = None
_refresh_running = False
_events = deque(maxlen=1000)  # MAX_EVENTS = 1000
_event_count = 0
_events_lock = Lock()


def _convert_lua_table(lua_table):
    """Convert Lua table to Python dict"""
    if isinstance(lua_table, dict):
        return lua_table
    elif hasattr(lua_table, 'items'):
        return dict(lua_table.items())
    else:
        return {}


@lua_exporter.export(description="Start polling refresh states", category="refresh", inject_runtime=True)
def pollRefreshStates(lua_runtime, start: int, url: str, options: dict):
    """Start polling refresh states in a background thread"""
    global _refresh_thread, _refresh_running

    # Stop existing thread if running
    if _refresh_running and _refresh_thread:
        _refresh_running = False
        _refresh_thread.join(timeout=1)

    # Convert Lua options to Python dict
    options = _convert_lua_table(options)

    def refresh_runner():
        global _refresh_running, _events, _event_count
        last, retries = start, 0
        _refresh_running = True

        while _refresh_running:
            try:
                nurl = url + str(last) + "&lang=en&rand=7784634785"
                resp = requests.get(nurl, headers=options.get('headers', {}), timeout=30)
                if resp.status_code == 200:
                    retries = 0
                    data = resp.json()
                    last = data.get('last', last)

                    if data.get('events'):
                        for event in data['events']:
                            # Use addEvent function directly with dict for efficiency
                            addEvent(lua_runtime, event)

                elif resp.status_code == 401:
                    print("HC3 credentials error", file=sys.stderr)
                    print("Exiting refreshStates loop", file=sys.stderr)
                    break

            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                retries += 1
                if retries > 5:
                    print(f"Connection error: {nurl}", file=sys.stderr)
                    print("Exiting refreshStates loop", file=sys.stderr)
                    break
            except Exception as e:
                print(f"Error: {e} {nurl}", file=sys.stderr)

            # Sleep between requests
            time.sleep(1)

        _refresh_running = False

    # Start the thread
    _refresh_thread = Thread(target=refresh_runner, daemon=True)
    _refresh_thread.start()

    return {"status": "started", "thread_id": _refresh_thread.ident}


@lua_exporter.export(description="Add event to the event queue", category="refresh", inject_runtime=True)
def addEvent(lua_runtime, event):
    """Add an event to the event queue - accepts dict only"""
    global _events, _event_count

    try:
        with _events_lock:
            _event_count += 1
            event_with_counter = {'last': _event_count, 'event': event}
            _events.append(event_with_counter)

        # Call _PY.newRefreshStatesEvent if it exists (for Lua event hooks)
        try:
            if hasattr(lua_runtime.globals(), '_PY') and hasattr(lua_runtime.globals()['_PY'], 'newRefreshStatesEvent'):
                if isinstance(event, str):
                    lua_runtime.globals()['_PY']['newRefreshStatesEvent'](event)
                else:
                    lua_runtime.globals()['_PY']['newRefreshStatesEvent'](json.dumps(event))
        except Exception:
            # Silently ignore errors in event hook - don't break the queue
            pass

        return {"status": "added", "event_count": _event_count}
    except Exception as e:
        print(f"Error adding event: {e}", file=sys.stderr)
        return {"status": "error", "error": str(e)}


@lua_exporter.export(description="Add event to the event queue from Lua", category="refresh", inject_runtime=True)
def addEventFromLua(lua_runtime, event_json: str):
    """Add an event to the event queue from Lua (JSON string input)"""
    try:
        event = json.loads(event_json)
        return addEvent(lua_runtime, event)
    except Exception as e:
        print(f"Error parsing event JSON: {e}", file=sys.stderr)
        return {"status": "error", "error": str(e)}


@lua_exporter.export(description="Get events since counter", category="refresh", inject_runtime=True)
def getEvents(lua_runtime, counter: int = 0):
    """Get events since the given counter"""
    global _events, _event_count

    with _events_lock:
        events = list(_events)  # Copy to avoid race conditions
        count = events[-1]['last'] if events else 0
        evs = [e['event'] for e in events if e['last'] > counter]

    ts = datetime.now().timestamp()
    tsm = time.time()

    res = {
        'status': 'IDLE',
        'events': evs,
        'changes': [],
        'timestamp': ts,
        'timestampMillis': tsm,
        'date': datetime.fromtimestamp(ts).strftime('%H:%M | %d.%m.%Y'),
        'last': count
    }

    # Return as Lua table directly
    return _python_to_lua_table(lua_runtime, res)


@lua_exporter.export(description="Stop refresh states polling", category="refresh", inject_runtime=True)
def stopRefreshStates(lua_runtime):
    """Stop refresh states polling"""
    try:
        if hasattr(lua_runtime, '_refresh_thread') and lua_runtime._refresh_thread:
            lua_runtime._refresh_thread.stop()
            lua_runtime._refresh_thread = None
            return True
        return False
    except Exception as e:
        print(f"Error stopping refresh states: {e}", file=sys.stderr)
        return False


@lua_exporter.export(description="Get refresh states status", category="refresh", inject_runtime=True)
def getRefreshStatesStatus(lua_runtime):
    """Get refresh states polling status"""
    try:
        if hasattr(lua_runtime, '_refresh_thread') and lua_runtime._refresh_thread:
            return {
                'running': lua_runtime._refresh_thread.is_alive(),
                'url': lua_runtime._refresh_thread.url,
                'start': lua_runtime._refresh_thread.start,
                'options': lua_runtime._refresh_thread.options
            }
        return {'running': False}
    except Exception as e:
        print(f"Error getting refresh states status: {e}", file=sys.stderr)
        return {'running': False, 'error': str(e)}
