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
import asyncio
from extensions.network_extensions import loop_manager


# Timer execution gate for synchronizing timer callbacks
class TimerExecutionGate:
    """Controls when timer callbacks are allowed to run using asyncio.Lock"""

    def __init__(self):
        self.lock = asyncio.Lock()
        self.queue = []
        self._locked = True
        self._initialized = False

    async def initialize(self):
        """Initialize the gate - should be called once when the event loop is ready"""
        if not self._initialized:
            await self.lock.acquire()
            self._initialized = True

    async def acquire(self):
        """Lock the gate - no timer callbacks can run"""
        if not self._initialized:
            await self.initialize()
        self._locked = True
        if not self.lock.locked():
            await self.lock.acquire()

    async def release(self):
        """Unlock the gate and run all queued callbacks"""
        self._locked = False
        if self.lock.locked():
            self.lock.release()

        # Run all queued callbacks
        while self.queue:
            callback, args, kwargs = self.queue.pop(0)
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Error in queued callback: {e}", file=sys.stderr)

    def run_or_queue(self, callback, *args, **kwargs):
        """Run callback immediately if unlocked, otherwise queue it"""
        if not self._locked:
            callback(*args, **kwargs)
        else:
            self.queue.append((callback, args, kwargs))

    def is_locked(self):
        """Check if the gate is currently locked"""
        return self._locked


# Global timer execution gate instance
timer_gate = TimerExecutionGate()


# Timer management class
class TimerManager:
    """Manages setTimeout and clearTimeout functionality using asyncio Tasks"""

    def __init__(self):
        self.timers = {}
        self.next_id = 1
        self.lock = threading.Lock()

    def setTimeout(self, func, ms):
        """Schedule a function to run after ms milliseconds using asyncio"""
        with self.lock:
            timer_id = self.next_id
            self.next_id += 1

        async def timer_coroutine():
            try:
                # Use a different approach for sleep
                start_time = time.time()
                while time.time() - start_time < ms / 1000.0:
                    await asyncio.sleep(0.01)  # Sleep in small chunks

                # Use the timer gate to control execution
                timer_gate.run_or_queue(func)
            except Exception as e:
                print(f"Timer error: {e}", file=sys.stderr)
            finally:
                with self.lock:
                    if timer_id in self.timers:
                        del self.timers[timer_id]

        # Check if we're in an event loop context
        try:
            asyncio.get_running_loop()
            # We're in an async context, use asyncio
            task = loop_manager.create_task(timer_coroutine())
            self.timers[timer_id] = task
        except RuntimeError:
            # No event loop running, use threading for short timers
            if ms < 1000:  # Only use threading for timers under 1 second
                def thread_timer():
                    time.sleep(ms / 1000.0)
                    try:
                        # Use the timer gate to control execution
                        timer_gate.run_or_queue(func)
                    except Exception as e:
                        print(f"Timer error: {e}", file=sys.stderr)
                    finally:
                        with self.lock:
                            if timer_id in self.timers:
                                del self.timers[timer_id]

                thread = threading.Thread(target=thread_timer, daemon=True)
                thread.start()
                self.timers[timer_id] = thread
            else:
                # For longer timers, still try to use asyncio
                task = loop_manager.create_task(timer_coroutine())
                self.timers[timer_id] = task

        return timer_id

    def clearTimeout(self, timer_id):
        """Cancel a timer by its ID"""
        with self.lock:
            if timer_id in self.timers:
                timer_obj = self.timers[timer_id]
                if hasattr(timer_obj, 'cancel'):  # asyncio.Task
                    timer_obj.cancel()
                elif hasattr(timer_obj, 'join'):  # threading.Thread
                    # Threads can't be cancelled, but we can mark them for removal
                    pass
                del self.timers[timer_id]
                return True
        return False

    def has_active_timers(self):
        """Check if there are any active timers (tasks that are not done)"""
        with self.lock:
            # Remove any finished tasks or threads
            to_remove = []
            for tid, timer_obj in self.timers.items():
                if hasattr(timer_obj, 'done') and timer_obj.done():  # asyncio.Task
                    to_remove.append(tid)
                elif hasattr(timer_obj, 'is_alive') and not timer_obj.is_alive():  # threading.Thread
                    to_remove.append(tid)

            for tid in to_remove:
                del self.timers[tid]
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


@registry.register(description="Sleep for specified seconds (non-blocking when possible)", category="system")
def sleep(seconds):
    """Sleep for specified number of seconds (non-blocking when event loop available)"""
    import asyncio
    try:
        # Check if we're in an event loop context
        asyncio.get_running_loop()
        # We're in an async context, use setTimeout for non-blocking sleep
        import threading
        import time

        # Create an event to signal completion
        event = threading.Event()

        # Set a timeout to prevent infinite waiting
        def timeout_handler():
            event.set()

        # Schedule the timeout
        timer_id = timer_manager.setTimeout(timeout_handler, seconds * 1000)

        # Wait for the event with a timeout to prevent deadlock
        if not event.wait(timeout=seconds + 1.0):  # Add 1 second buffer
            # If we timeout, clean up the timer
            timer_manager.clearTimeout(timer_id)
            # Fall back to blocking sleep
            time.sleep(seconds)

    except RuntimeError:
        # No event loop running, use blocking sleep
        import time
        time.sleep(seconds)

    return None


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
@registry.register(description="Parse JSON string to table", category="json", inject_runtime=True)
def parse_json(lua_runtime, json_string):
    """Parse JSON string and return as Lua table"""
    try:
        # Handle empty or None input
        if not json_string or json_string == "":
            return None
        
        python_obj = json.loads(json_string)
        # Use Lupa's table conversion
        return lua_runtime.table_from(python_obj)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"JSON conversion error: {e}", file=sys.stderr)
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


@registry.register(description="Get all environment variables as a table", category="config", inject_runtime=True)
def get_all_env_vars(lua_runtime):
    """Get all environment variables as a Lua table, with .env file variables taking precedence"""
    # First ensure .env files are loaded
    if not hasattr(get_env_var, '_env_loaded'):
        get_env_var._env_loaded = True
        _load_env_files()

    # Create a Lua table with all environment variables
    env_table = lua_runtime.table()

    # Add all environment variables to the table
    for key, value in os.environ.items():
        env_table[key] = value

    return env_table


@registry.register(description="Import Python module", category="system")
def import_module(module_name):
    """Import a Python module and return it"""
    try:
        return __import__(module_name)
    except ImportError as e:
        print(f"Failed to import module '{module_name}': {e}", file=sys.stderr)
        return None


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


# Interval management class
class IntervalManager:
    """Manages setInterval and clearInterval functionality"""
    def __init__(self):
        self.intervals = {}
        self.next_id = 1
        self.lock = threading.Lock()

    def setInterval(self, func, ms):
        """Schedule a function to run every ms milliseconds"""
        with self.lock:
            interval_id = self.next_id
            self.next_id += 1

        async def interval_coroutine():
            try:
                while True:
                    # Use the same approach for sleep as timers
                    start_time = time.time()
                    while time.time() - start_time < ms / 1000.0:
                        await asyncio.sleep(0.01)  # Sleep in small chunks

                    # Use the timer gate to control execution
                    timer_gate.run_or_queue(func)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Interval error: {e}", file=sys.stderr)
            finally:
                with self.lock:
                    if interval_id in self.intervals:
                        del self.intervals[interval_id]

        task = loop_manager.create_task(interval_coroutine())
        self.intervals[interval_id] = task
        return interval_id

    def clearInterval(self, interval_id):
        """Cancel an interval by its ID"""
        with self.lock:
            if interval_id in self.intervals:
                task = self.intervals[interval_id]
                task.cancel()
                del self.intervals[interval_id]
                return True
        return False

    def has_active_intervals(self):
        """Check if there are any active intervals"""
        with self.lock:
            to_remove = [iid for iid, t in self.intervals.items() if t.done()]
            for iid in to_remove:
                del self.intervals[iid]
            return len(self.intervals) > 0

    def force_cleanup(self):
        """Force cleanup of all intervals"""
        with self.lock:
            for iid, task in list(self.intervals.items()):
                task.cancel()
            self.intervals.clear()


# Global interval manager instance
interval_manager = IntervalManager()


# Interval Extensions
@registry.register(description="Schedule a function to run repeatedly every specified milliseconds", category="timers")
def setInterval(func, ms):
    """Schedule a function to run every ms milliseconds"""
    return interval_manager.setInterval(func, ms)


@registry.register(description="Cancel an interval using its reference ID", category="timers")
def clearInterval(interval_id):
    """Cancel an interval by its ID"""
    return interval_manager.clearInterval(interval_id)


@registry.register(description="Check if there are active intervals", category="timers")
def has_active_intervals():
    """Check if there are any active intervals"""
    return interval_manager.has_active_intervals()


@registry.register(description="Get event loop debug info", category="debug")
def _get_event_loop_info():
    """Get debug information about the event loop"""
    try:
        from extensions.network_extensions import loop_manager
        loop = loop_manager.get_loop()
        if loop:
            tasks = asyncio.all_tasks(loop)
            return {
                "loop_running": loop.is_running(),
                "loop_closed": loop.is_closed(),
                "pending_tasks": len(tasks),
                "task_names": [task.get_name() for task in tasks]
            }
        else:
            return {"error": "No event loop available"}
    except Exception as e:
        return {"error": str(e)}


@registry.register(description="Yield control to the event loop", category="async")
async def yield_to_event_loop():
    """Yield control back to the Python event loop to allow timers and async operations to fire"""
    await asyncio.sleep(0)


@registry.register(description="Yield control to the event loop (sync wrapper)", category="async")
def yield_to_loop():
    """Synchronous wrapper that allows the event loop to process pending tasks"""
    try:
        import time
        # Simple sleep to allow event loop to process pending tasks
        time.sleep(0.01)  # 10ms sleep
    except Exception as e:
        print(f"Yield error: {e}", file=sys.stderr)


# Timer gate control functions (for interpreter use)
async def acquire_timer_gate():
    """Lock the timer execution gate - no timer callbacks can run"""
    await timer_gate.acquire()


async def release_timer_gate():
    """Unlock the timer execution gate and run all queued callbacks"""
    await timer_gate.release()


def is_timer_gate_locked():
    """Check if the timer execution gate is currently locked"""
    return timer_gate.is_locked()
