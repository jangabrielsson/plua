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
import tempfile
from extensions.network_extensions import loop_manager
import requests
from datetime import datetime
from collections import deque
from threading import Thread, Lock
# from typing import List, Any, Optional


# Timer management class
class TimerManager:
    """Manages setTimeout and clearTimeout functionality using asyncio Tasks"""

    def __init__(self):
        self.timers = {}
        self.next_id = 1
        self.lock = threading.Lock()
        self.callback_queue = []
        self.queue_lock = threading.Lock()

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

                # Queue the callback for safe execution
                with self.queue_lock:
                    self.callback_queue.append(func)
            except Exception as e:
                print(f"Timer error: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
            finally:
                # Delay removal until after the next event loop tick
                async def remove_timer():
                    await asyncio.sleep(0)  # Yield to event loop
                    with self.lock:
                        if timer_id in self.timers:
                            del self.timers[timer_id]
                try:
                    loop = loop_manager.get_loop()
                    loop.create_task(remove_timer())
                except Exception:
                    # Fallback: remove immediately if loop not available
                    with self.lock:
                        if timer_id in self.timers:
                            del self.timers[timer_id]

        # Always use asyncio for consistency and to avoid thread safety issues
        # The loop_manager will handle creating the event loop if needed
        task = loop_manager.create_task(timer_coroutine())
        self.timers[timer_id] = task

        return timer_id

    def process_callbacks(self):
        """Process any queued callbacks - should be called from the main thread"""
        with self.queue_lock:
            callbacks = self.callback_queue.copy()
            self.callback_queue.clear()
        
        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Callback execution error: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()

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

    # Process any pending timer callbacks
    timer_manager.process_callbacks()

    return None


@registry.register(description="Process pending timer callbacks", category="timers")
def process_timer_callbacks():
    """Process any pending timer callbacks - useful for manual control"""
    timer_manager.process_callbacks()


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
        # Convert Python object to Lua table recursively
        return _python_to_lua_table(lua_runtime, python_obj)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"JSON conversion error: {e}", file=sys.stderr)
        return None


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


@registry.register(description="Convert table to JSON string", category="json")
def to_json(data):
    """Convert data to JSON string"""
    try:
        # Convert Lua table to Python dict/list if needed
        if hasattr(data, 'values'):  # Lua table
            # Use _convert_lua_to_python to properly handle nested structures
            python_obj = _convert_lua_to_python(data)
            return json.dumps(python_obj)
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
        # Fast check for JSON array: if key 1 exists and table length matches expected array length
        try:
            if 1 in lua_obj:
                # Check if this looks like a sequential array starting from 1
                length = len(lua_obj)
                # For a proper array, the highest key should equal the length
                # and all keys from 1 to length should exist
                if all(i in lua_obj for i in range(1, length + 1)):
                    # Convert to Python list
                    python_list = []
                    for i in range(1, length + 1):
                        value = lua_obj[i]
                        python_list.append(_convert_lua_to_python(value))
                    return python_list
        except (KeyError, TypeError):
            pass  # If any key access fails, treat as dict

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


@registry.register(description="Create a temporary directory with specified name", category="filesystem")
def create_temp_directory(name):
    """Create a temporary directory with the specified name in the OS temp directory
    
    Args:
        name: Name of the directory to create
        
    Returns:
        str: Full path to the created temporary directory, or None on error
        
    Examples:
        - On macOS: /var/tmp/myapp/
        - On Windows: C:/Users/<user>/AppData/Local/Temp/myapp/
    """
    try:
        # Get the system temp directory
        temp_dir = tempfile.gettempdir()
        
        # Create the full path for the temporary directory
        temp_path = os.path.join(temp_dir, name)
        
        # Create the directory (and parent directories if needed)
        os.makedirs(temp_path, exist_ok=True)
        
        return temp_path
    except OSError as e:
        print(f"Error creating temporary directory '{name}': {e}", file=sys.stderr)
        return None


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

                    # Queue the callback for safe execution
                    with timer_manager.queue_lock:
                        timer_manager.callback_queue.append(func)
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
    """Yield control to the event loop (synchronous wrapper)"""
    try:
        import time
        time.sleep(0.01)  # 10ms sleep
    except Exception as e:
        print(f"Yield error: {e}", file=sys.stderr)


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


@registry.register(description="Start polling refresh states", category="refresh", inject_runtime=True)
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


@registry.register(description="Add event to the event queue", category="refresh", inject_runtime=True)
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


@registry.register(description="Add event to the event queue from Lua", category="refresh", inject_runtime=True)
def addEventFromLua(lua_runtime, event_json: str):
    """Add an event to the event queue from Lua (JSON string input)"""
    try:
        event = json.loads(event_json)
        return addEvent(lua_runtime, event)
    except Exception as e:
        print(f"Error parsing event JSON: {e}", file=sys.stderr)
        return {"status": "error", "error": str(e)}


@registry.register(description="Get events since counter", category="refresh", inject_runtime=True)
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


@registry.register(description="Stop refresh states polling", category="refresh", inject_runtime=True)
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


@registry.register(description="Get refresh states status", category="refresh", inject_runtime=True)
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


# QuickApps UI Update Functions
@registry.register(description="Broadcast UI update to all connected WebSocket clients", category="quickapps", inject_runtime=True)
def broadcast_ui_update(lua_runtime, device_id):
    """
    Broadcast a UI update event to all connected WebSocket clients.
    This will trigger a reload of the QuickApps UI in the frontend.

    Args:
        device_id: The ID of the device whose UI has been updated (can be number, string, or Lua table with .id)

    Returns:
        bool: True if the broadcast was successful
    """
    try:
        # Convert device_id to integer, handling different input types
        actual_device_id = None

        if isinstance(device_id, (int, float)):
            actual_device_id = int(device_id)
        elif isinstance(device_id, str):
            try:
                actual_device_id = int(device_id)
            except ValueError:
                print(f"Error: device_id string '{device_id}' cannot be converted to integer", file=sys.stderr)
                return False
        elif hasattr(device_id, 'id'):
            # Handle Lua table with .id property (like self)
            try:
                actual_device_id = int(device_id.id)
            except (TypeError, ValueError, AttributeError):
                print("Error: device_id object has .id but it's not a valid integer", file=sys.stderr)
                return False
        else:
            print("Error: device_id must be a number, string, or object with .id property, got {}".format(type(device_id)), file=sys.stderr)
            return False

        # Get the interpreter instance from _PY_INTERPRETER
        lua_globals = lua_runtime.globals()
        if '_PY_INTERPRETER' in lua_globals:
            interpreter = lua_globals['_PY_INTERPRETER']
            if interpreter and interpreter.embedded_api_server:
                # Run the broadcast in a new thread to avoid blocking
                import threading
                import asyncio

                def run_broadcast():
                    try:
                        # Create new event loop for this thread
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            interpreter.embedded_api_server.broadcast_ui_update(actual_device_id)
                        )
                    except Exception as e:
                        print(f"Error in broadcast thread: {e}", file=sys.stderr)

                # Start broadcast in background thread
                thread = threading.Thread(target=run_broadcast)
                thread.daemon = True
                thread.start()
                return True
            else:
                print("Warning: Embedded API server not available", file=sys.stderr)
                return False
        else:
            print("Warning: Interpreter reference not available", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Error broadcasting UI update: {e}", file=sys.stderr)
        return False
