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


