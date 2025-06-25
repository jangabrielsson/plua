"""
Custom Extensions Example
This file demonstrates how to add custom Python functions to the Lua environment
using the decorator system from lua_extensions.py
"""

from .registry import registry
import json
import os
import sys


# Helper function to convert Python list to Lua table
def _to_lua_table(pylist):
    """Convert Python list to Lua table"""
    lua_table = {}
    for i, item in enumerate(pylist, 1):  # Lua uses 1-based indexing
        lua_table[i] = item
    return lua_table


# Example: JSON processing functions
@registry.register(description="Parse JSON string to table", category="json")
def parse_json(json_string):
    """Parse JSON string and return as Lua table"""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        return None


@registry.register(description="Convert table to JSON string", category="json")
def to_json(data):
    """Convert data to JSON string"""
    try:
        # Convert Lua table to Python dict/list if needed
        if hasattr(data, 'values'):  # Lua table
            # Check if this is a sequential array (1-based numeric keys)
            keys = list(data.keys())
            if keys and all(isinstance(k, (int, float)) for k in keys):
                # Check if keys form a sequential sequence starting from 1
                sorted_keys = sorted(keys)
                if sorted_keys == list(range(1, len(sorted_keys) + 1)):
                    # This is a Lua array, convert to Python list
                    python_list = []
                    for i in range(1, len(sorted_keys) + 1):
                        value = data[i]
                        # Recursively convert nested Lua tables
                        if hasattr(value, 'values'):
                            python_list.append(to_json(value))
                        else:
                            python_list.append(value)
                    return json.dumps(python_list)

            # This is a Lua table/dict, convert to Python dict
            python_dict = {}
            for key, value in data.items():
                # Recursively convert nested Lua tables
                if hasattr(value, 'values'):
                    python_dict[key] = to_json(value)
                else:
                    python_dict[key] = value
            return json.dumps(python_dict)
        else:
            return json.dumps(data)
    except Exception as e:
        print(f"JSON conversion error: {e}", file=sys.stderr)
        return None


# Example: File system functions
@registry.register(description="Check if file exists", category="filesystem")
def file_exists(filename):
    """Check if file exists"""
    return os.path.exists(filename)


@registry.register(description="Get file size in bytes", category="filesystem")
def get_file_size(filename):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filename)
    except OSError:
        return None


@registry.register(description="List files in directory", category="filesystem", inject_runtime=True)
def list_files(lua_runtime, directory="."):
    """List files in directory and return as a real Lua table"""
    try:
        return lua_runtime.table(*os.listdir(directory))
    except OSError as e:
        print(f"Error listing directory '{directory}': {e}", file=sys.stderr)
        return None


@registry.register(description="Create directory", category="filesystem")
def create_directory(path):
    """Create directory (and parent directories if needed)"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError as e:
        print(f"Error creating directory '{path}': {e}", file=sys.stderr)
        return False


# Example: Network functions (simplified)
@registry.register(description="Get hostname", category="network")
def get_hostname():
    """Get current hostname"""
    import socket
    return socket.gethostname()


@registry.register(description="Check if port is open", category="network")
def check_port(host, port):
    """Check if port is open on host"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


# Example: Configuration functions
@registry.register(description="Get environment variable", category="config")
def get_env_var(name, default=None):
    """Get environment variable value, also checking .env files"""
    import os

    # First check if already loaded from .env files
    if not hasattr(get_env_var, '_env_loaded'):
        get_env_var._env_loaded = True
        _load_env_files()

    return os.environ.get(name, default)


def _load_env_files():
    """Load environment variables from .env files"""
    import os

    # Look for .env files in current directory and parent directories
    current_dir = os.getcwd()
    dirs_to_check = [current_dir]

    # Add parent directories (up to 3 levels up)
    parent_dir = os.path.dirname(current_dir)
    for _ in range(3):
        if parent_dir and parent_dir != current_dir:
            dirs_to_check.append(parent_dir)
            current_dir = parent_dir
            parent_dir = os.path.dirname(parent_dir)
        else:
            break

    # Process .env files in order (closest to current directory first)
    for directory in dirs_to_check:
        env_file = os.path.join(directory, '.env')
        if os.path.exists(env_file):
            _parse_env_file(env_file)


def _parse_env_file(env_file_path):
    """Parse a .env file and load variables into os.environ"""
    import os
    import re

    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE format
                # Support both KEY=value and KEY="value" formats
                match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip()

                    # Handle quoted values
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Only set if not already in environment (don't override existing env vars)
                    if key not in os.environ:
                        os.environ[key] = value

    except Exception:
        # Silently ignore .env file parsing errors
        pass


@registry.register(description="Set environment variable", category="config")
def set_env_var(name, value):
    """Set environment variable"""
    import os
    os.environ[name] = str(value)
    return True


# Base64 encoding/decoding functions
@registry.register(description="Encode string to base64", category="encoding")
def base64_encode(data):
    """Encode data to base64 string"""
    import base64

    try:
        if isinstance(data, str):
            # Encode string to bytes first
            data_bytes = data.encode('utf-8')
        else:
            # Assume it's already bytes or can be converted
            data_bytes = bytes(data)

        # Encode to base64
        encoded_bytes = base64.b64encode(data_bytes)
        return encoded_bytes.decode('utf-8')
    except Exception as e:
        print(f"Base64 encoding error: {e}", file=sys.stderr)
        return None


@registry.register(description="Decode base64 string", category="encoding")
def base64_decode(encoded_data):
    """Decode base64 string to original data"""
    import base64

    try:
        if isinstance(encoded_data, str):
            # Decode base64 string
            decoded_bytes = base64.b64decode(encoded_data)
            # Try to decode as UTF-8 string, fall back to bytes if it fails
            try:
                return decoded_bytes.decode('utf-8')
            except UnicodeDecodeError:
                return decoded_bytes
        else:
            # Assume it's bytes
            decoded_bytes = base64.b64decode(encoded_data)
            try:
                return decoded_bytes.decode('utf-8')
            except UnicodeDecodeError:
                return decoded_bytes
    except Exception as e:
        print(f"Base64 decoding error: {e}", file=sys.stderr)
        return None
