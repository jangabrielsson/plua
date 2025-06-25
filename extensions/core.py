"""
Core Extensions for PLua
Provides basic functionality like timers, I/O, system, math, and utility functions.
"""

import sys
import threading
import time
from .registry import registry
import json
import os
import base64
import re


# Timer management class
class TimerManager:
    """Manages setTimeout and clearTimeout functionality"""

    def __init__(self):
        self.timers = {}
        self.next_id = 1
        self.lock = threading.Lock()

    def setTimeout(self, func, ms):
        """Schedule a function to run after ms milliseconds"""
        with self.lock:
            timer_id = self.next_id
            self.next_id += 1

        def wrapped_func():
            try:
                func()
            except Exception as e:
                print(f"Timer error: {e}", file=sys.stderr)
            finally:
                with self.lock:
                    if timer_id in self.timers:
                        del self.timers[timer_id]

        timer = threading.Timer(ms / 1000.0, wrapped_func)
        self.timers[timer_id] = timer
        timer.start()

        return timer_id

    def clearTimeout(self, timer_id):
        """Cancel a timer by its ID"""
        with self.lock:
            if timer_id in self.timers:
                timer = self.timers[timer_id]
                timer.cancel()
                del self.timers[timer_id]
                return True
        return False

    def has_active_timers(self):
        """Check if there are any active timers"""
        with self.lock:
            return len(self.timers) > 0


# Global timer manager instance
timer_manager = TimerManager()


# Timer Extensions
@registry.register(description="Schedule a function to run after specified milliseconds", category="timers")
def setTimeout(func, ms):
    """Schedule a function to run after ms milliseconds"""
    return timer_manager.setTimeout(func, ms)


@registry.register(description="Cancel a timer using its reference ID", category="timers")
def clearTimeout(timer_id):
    """Cancel a timer by its ID"""
    return timer_manager.clearTimeout(timer_id)


@registry.register(description="Check if there are active timers", category="timers")
def has_active_timers():
    """Check if there are any active timers"""
    return timer_manager.has_active_timers()


# I/O Extensions
@registry.register(description="Get user input from stdin", category="io")
def input_lua(prompt=""):
    """Get user input with optional prompt"""
    return input(prompt)


@registry.register(description="Read contents of a file", category="io")
def read_file(filename):
    """Read and return the contents of a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file '{filename}': {e}", file=sys.stderr)
        return None


@registry.register(description="Write content to a file", category="io")
def write_file(filename, content):
    """Write content to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(content))
        return True
    except Exception as e:
        print(f"Error writing file '{filename}': {e}", file=sys.stderr)
        return False


# System Extensions
@registry.register(description="Get current timestamp in seconds", category="system")
def get_time():
    """Get current timestamp"""
    return time.time()


@registry.register(description="Sleep for specified seconds (non-blocking)", category="system")
def sleep(seconds):
    """Sleep for specified number of seconds (non-blocking)"""
    # Use a simple busy wait for short sleeps, setTimeout for longer ones
    if seconds < 0.1:
        # For very short sleeps, use busy wait to avoid timer overhead
        end_time = time.time() + seconds
        while time.time() < end_time:
            pass
    else:
        # For longer sleeps, use setTimeout to avoid blocking
        import threading
        event = threading.Event()
        timer_manager.setTimeout(lambda: event.set(), seconds * 1000)
        event.wait()


@registry.register(description="Get Python version information", category="system")
def get_python_version():
    """Get Python version information"""
    return f"Python {sys.version}"


# List all extensions function
@registry.register(name="list_extensions", description="List all available Python extensions", category="utility")
def list_extensions():
    """List all available extensions"""
    registry.list_extensions()


# Helper function to convert Python list to Lua table
def _to_lua_table(pylist):
    """Convert Python list to Lua table"""
    lua_table = {}
    for i, item in enumerate(pylist, 1):  # Lua uses 1-based indexing
        lua_table[i] = item
    return lua_table


# JSON processing functions
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
            keys = list(data.keys())
            if keys and all(isinstance(k, (int, float)) for k in keys):
                sorted_keys = sorted(keys)
                if sorted_keys == list(range(1, len(sorted_keys) + 1)):
                    python_list = []
                    for i in range(1, len(sorted_keys) + 1):
                        value = data[i]
                        if hasattr(value, 'values'):
                            python_list.append(to_json(value))
                        else:
                            python_list.append(value)
                    return json.dumps(python_list)
            python_dict = {}
            for key, value in data.items():
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


@registry.register(description="Pretty print a Lua table by converting to JSON", category="json")
def pretty_print(data, indent=2):
    """Pretty print a Lua table by converting to JSON with indentation"""
    try:
        # Convert Lua table to Python dict/list if needed
        if hasattr(data, 'values'):  # Lua table
            keys = list(data.keys())
            if keys and all(isinstance(k, (int, float)) for k in keys):
                sorted_keys = sorted(keys)
                if sorted_keys == list(range(1, len(sorted_keys) + 1)):
                    python_list = []
                    for i in range(1, len(sorted_keys) + 1):
                        value = data[i]
                        if hasattr(value, 'values'):
                            # Recursively convert nested Lua tables
                            python_list.append(_convert_lua_to_python(value))
                        else:
                            python_list.append(value)
                    return json.dumps(python_list, indent=indent)
            python_dict = {}
            for key, value in data.items():
                if hasattr(value, 'values'):
                    # Recursively convert nested Lua tables
                    python_dict[key] = _convert_lua_to_python(value)
                else:
                    python_dict[key] = value
            return json.dumps(python_dict, indent=indent)
        else:
            return json.dumps(data, indent=indent)
    except Exception as e:
        print(f"Pretty print error: {e}", file=sys.stderr)
        return None


def _convert_lua_to_python(lua_obj):
    """Convert Lua object to Python object recursively"""
    if hasattr(lua_obj, 'values'):  # Lua table
        keys = list(lua_obj.keys())
        if keys and all(isinstance(k, (int, float)) for k in keys):
            sorted_keys = sorted(keys)
            if sorted_keys == list(range(1, len(sorted_keys) + 1)):
                # Convert to Python list
                python_list = []
                for i in range(1, len(sorted_keys) + 1):
                    value = lua_obj[i]
                    python_list.append(_convert_lua_to_python(value))
                return python_list
        # Convert to Python dict
        python_dict = {}
        for key, value in lua_obj.items():
            python_dict[key] = _convert_lua_to_python(value)
        return python_dict
    else:
        # Return as-is for primitive types
        return lua_obj


@registry.register(description="Print a Lua table in a pretty format", category="json")
def print_table(data, indent=2):
    """Print a Lua table in a pretty format to stdout"""
    try:
        pretty_json = pretty_print(data, indent)
        if pretty_json is not None:
            print(pretty_json)
            return True
        else:
            print("Error: Could not convert table to JSON", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Print table error: {e}", file=sys.stderr)
        return False


# File system functions
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


# Network functions


# Configuration functions
@registry.register(description="Get environment variable", category="config")
def get_env_var(name, default=None):
    """Get environment variable value, also checking .env files"""
    # First check if already loaded from .env files
    if not hasattr(get_env_var, '_env_loaded'):
        get_env_var._env_loaded = True
        _load_env_files()
    return os.environ.get(name, default)


def _load_env_files():
    """Load environment variables from .env files"""
    current_dir = os.getcwd()
    dirs_to_check = [current_dir]
    parent_dir = os.path.dirname(current_dir)
    for _ in range(3):
        if parent_dir and parent_dir != current_dir:
            dirs_to_check.append(parent_dir)
            current_dir = parent_dir
            parent_dir = os.path.dirname(parent_dir)
        else:
            break
    for directory in dirs_to_check:
        env_file = os.path.join(directory, '.env')
        if os.path.exists(env_file):
            _parse_env_file(env_file)


def _parse_env_file(env_file_path):
    """Parse a .env file and load variables into os.environ"""
    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    if key not in os.environ:
                        os.environ[key] = value
    except Exception:
        pass


@registry.register(description="Set environment variable", category="config")
def set_env_var(name, value):
    """Set environment variable"""
    os.environ[name] = str(value)
    return True


# Base64 encoding/decoding functions
@registry.register(description="Encode string to base64", category="encoding")
def base64_encode(data):
    """Encode data to base64 string"""
    try:
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = bytes(data)
        encoded_bytes = base64.b64encode(data_bytes)
        return encoded_bytes.decode('utf-8')
    except Exception as e:
        print(f"Base64 encoding error: {e}", file=sys.stderr)
        return None


@registry.register(description="Decode base64 string", category="encoding")
def base64_decode(encoded_data):
    """Decode base64 string to original data"""
    try:
        if isinstance(encoded_data, str):
            decoded_bytes = base64.b64decode(encoded_data)
            try:
                return decoded_bytes.decode('utf-8')
            except UnicodeDecodeError:
                return decoded_bytes
        else:
            decoded_bytes = base64.b64decode(encoded_data)
            try:
                return decoded_bytes.decode('utf-8')
            except UnicodeDecodeError:
                return decoded_bytes
    except Exception as e:
        print(f"Base64 decoding error: {e}", file=sys.stderr)
        return None
