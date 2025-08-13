"""
Lua-Python bindings for the EPLua engine.

This module provides the bridge between Lua scripts and Python functionality,
specifically for timer operations and other engine features.
"""

import logging
from typing import Any, Callable, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# Registry for decorated functions
_exported_functions: Dict[str, Callable] = {}

# Global engine instance reference
_global_engine = None


def set_global_engine(engine):
    """Set the global engine instance."""
    global _global_engine
    _global_engine = engine


def get_global_engine():
    """Get the global engine instance."""
    return _global_engine


def python_to_lua_table(data: Any) -> Any:
    """
    Convert Python data structures to Lua tables using Lupa.
    
    Args:
        data: Python data (dict, list, or primitive)
        
    Returns:
        Lua table or primitive value
    """
    if _global_engine is None:
        raise RuntimeError("Global engine not set. Call set_global_engine() first.")
    
    if isinstance(data, (dict, list)):
        return _global_engine._lua.table_from(data, recursive=True)
    else:
        return data


def lua_to_python_table(lua_table: Any) -> Any:
    """
    Convert Lua tables to Python data structures.
    
    Args:
        lua_table: Lua table or primitive value
        
    Returns:
        Python dict, list, or primitive value
    """
    if _global_engine is None:
        raise RuntimeError("Global engine not set. Call set_global_engine() first.")
    
    # Check if it's a Lua table
    if hasattr(lua_table, '__class__') and 'lua' in str(lua_table.__class__).lower():
        try:
            # Convert to Python dict first
            temp_dict = {}
            for key, value in lua_table.items():
                # Recursively convert nested tables
                python_key = lua_to_python_table(key) if hasattr(key, '__class__') and 'lua' in str(key.__class__).lower() else key
                python_value = lua_to_python_table(value) if hasattr(value, '__class__') and 'lua' in str(value.__class__).lower() else value
                temp_dict[python_key] = python_value
            
            # Check if this looks like an array (consecutive integer keys starting from 1)
            if temp_dict and all(isinstance(k, (int, float)) and k > 0 for k in temp_dict.keys()):
                keys = sorted([int(k) for k in temp_dict.keys()])
                if keys == list(range(1, len(keys) + 1)):
                    # This is a Lua array, convert to Python list
                    return [temp_dict[k] for k in keys]
            
            return temp_dict
        except Exception:
            # If conversion fails, return string representation
            return str(lua_table)
    else:
        return lua_table


def export_to_lua(name: Optional[str] = None):
    """
    Decorator to automatically export Python functions to the _PY table.
    
    Args:
        name: Optional name for the function in Lua. If None, uses the Python function name.
        
    Usage:
        @export_to_lua()
        def my_function(arg1, arg2):
            return arg1 + arg2
            
        @export_to_lua("custom_name")
        def another_function():
            print("Hello from Python!")
    """
    def decorator(func: Callable) -> Callable:
        lua_name = name if name is not None else func.__name__
        _exported_functions[lua_name] = func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_exported_functions() -> Dict[str, Callable]:
    """Get all functions marked for export to Lua."""
    return _exported_functions.copy()


class LuaBindings:
    """
    Provides Python functions that can be called from Lua scripts.
    
    This class creates the bridge between Lua and Python, exposing
    Python functionality to Lua scripts in a controlled manner.
    """
    
    def __init__(self, timer_manager, engine_instance):
        """
        Initialize Lua bindings.
        
        Args:
            timer_manager: Instance of AsyncTimerManager
            engine_instance: Instance of LuaEngine for callbacks
        """
        self.timer_manager = timer_manager
        self.engine = engine_instance
        self._setup_exported_functions()
        
    def _setup_exported_functions(self):
        """Setup exported functions with access to self."""
        # Timer functions
        @export_to_lua("set_timeout")
        def set_timeout(callback_id: int, delay_ms: int) -> str:
            """
            Set a timeout timer from Lua.
            
            Args:
                callback_id: ID of the Lua callback
                delay_ms: Delay in milliseconds
                
            Returns:
                Python timer ID
            """
            logger.debug(f"Setting timeout: {delay_ms}ms for callback {callback_id}")
            
            def python_callback():
                """Callback that notifies Lua when timer expires."""
                try:
                    # Call back into Lua
                    self.engine._lua.globals()["_PY"]["timerExpired"](callback_id)
                except Exception as e:
                    logger.error(f"Error in timeout callback {callback_id}: {e}")
                    
            return self.timer_manager.set_timeout(delay_ms, python_callback)
        
        @export_to_lua("clear_timeout")
        def clear_timeout(timer_id: str) -> bool:
            """
            Clear a timeout timer from Lua.
            
            Args:
                timer_id: Python timer ID to clear
                
            Returns:
                True if timer was cleared, False otherwise
            """
            logger.debug(f"Clearing timeout: {timer_id}")
            return self.timer_manager.clear_timer(timer_id)
        
        @export_to_lua("get_timer_count")
        def get_timer_count() -> int:
            """Get the number of active timers."""
            return self.timer_manager.get_timer_count()
        
        # Engine functions
        @export_to_lua("print")
        def lua_print(*args) -> None:
            """Enhanced print function for Lua scripts."""
            message = " ".join(str(arg) for arg in args)
            logger.info(f"Lua: {message}")
            print(f"{message}", flush=True)
        
        @export_to_lua("log")
        def lua_log(level: str, message: str) -> None:
            """Logging function for Lua scripts."""
            level = level.upper()
            if level == "DEBUG":
                logger.debug(f"Lua: {message}")
            elif level == "INFO":
                logger.info(f"Lua: {message}")
            elif level == "WARNING":
                logger.warning(f"Lua: {message}")
            elif level == "ERROR":
                logger.error(f"Lua: {message}")
            else:
                logger.info(f"Lua [{level}]: {message}")
        
        @export_to_lua("get_time")
        def get_time() -> float:
            """Get current time in seconds."""
            import time
            return time.time()
        
        @export_to_lua("sleep")
        def sleep(seconds: float) -> None:
            """Sleep function (note: this is blocking, prefer timers for async)."""
            import time
            time.sleep(seconds)
            
        @export_to_lua("python_2_lua_table")
        def python_2_lua_table(data: Any) -> Any:
            """Convert Python data to Lua table."""
            return python_to_lua_table(data)
        
        @export_to_lua("os.exit")
        def os_exit(code: int = 0) -> None:
            """Exit the EPLua process with the specified exit code"""
            import os
            os._exit(code)  # Use _exit to avoid cleanup issues
            
        @export_to_lua("get_platform")
        def get_platform() -> Any:
            """Get the current platform information as Lua table."""
            import platform
            platform_info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
            return python_to_lua_table(platform_info)
            
        @export_to_lua("get_system_info")
        def get_system_info() -> Any:
            """Get comprehensive system information as Lua table."""
            import platform
            import os
            import time
            
            info = {
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "python_version": platform.python_version()
                },
                "environment": {
                    "cwd": os.getcwd(),
                    "user": os.environ.get("USER", "unknown"),
                    "home": os.environ.get("HOME", "unknown"),
                    "path_separator": os.pathsep,
                    "line_separator": os.linesep
                },
                "runtime": {
                    "current_time": time.time(),
                    "pid": os.getpid()
                }
            }
            return python_to_lua_table(info)
            
        # Additional utility functions
        @export_to_lua("math_add")
        def math_add(a: float, b: float) -> float:
            """Add two numbers."""
            return a + b
            
        @export_to_lua("random_number")
        def random_number(min_val: float = 0, max_val: float = 1) -> float:
            """Generate a random number between min_val and max_val."""
            import random
            return random.uniform(min_val, max_val)
            
        @export_to_lua("threadRequestResult")
        def thread_request_result(request_id: str, result: Any) -> None:
            """
            Handle the result of a thread-safe script execution request.
            Called from Lua when a threadRequest completes.
            
            Args:
                request_id: The ID of the execution request
                result: The result data from the Lua execution
            """
            if self.engine:
                self.engine.handle_thread_request_result(request_id, result)
                
        @export_to_lua("parse_json")
        def parse_json(json_string: str) -> Any:
            """
            Parse a JSON string and return the corresponding Python/Lua data structure.
            
            Args:
                json_string: The JSON string to parse
                
            Returns:
                Tuple of (parsed_data, error). If successful, error is None.
                If failed, parsed_data is None and error contains the error message.
            """
            import json
            try:
                parsed_data = json.loads(json_string)
                # Convert Python data to Lua-compatible format
                lua_data = python_to_lua_table(parsed_data)
                return lua_data, None
            except json.JSONDecodeError as e:
                return None, str(e)
            except Exception as e:
                return None, f"Unexpected error: {str(e)}"
        
        @export_to_lua("file_exists")
        def fs_file_exists(filename: str) -> bool:
            """
            Check if a file exists.
            """
            import os
            return os.path.exists(filename)
        
        @export_to_lua("fwrite_file")
        def fwrite_file(filename: str, data: str) -> bool:
            """
            Write data to a file.
            """
            with open(filename, 'w') as f:
                f.write(data)
            return True
        
        @export_to_lua("fread_file")
        def fread_file(filename: str) -> str:
            """
            Read data from a file.
            """
            with open(filename, 'r') as f:
                return f.read()
        
        @export_to_lua("base64_encode")
        def base64_encode(data: str) -> str:
            """
            Encode a string to base64.
            """
            import base64
            return base64.b64encode(data.encode('utf-8')).decode('utf-8')
        
        @export_to_lua("base64_decode")
        def base64_decode(data: str) -> str:
            """
            Decode a base64-encoded string.
            """
            import base64
            return base64.b64decode(data.encode('utf-8')).decode('utf-8')
        
        @export_to_lua("milli_time")
        def milli_time() -> float:
            """
            Get the current time in seconds with milliseconds precision.
            """
            import time
            return time.time()
        
        @export_to_lua("dotgetenv")
        def dotgetenv(key: str, default: str = None) -> str:
            """
            Read environment variables from .env files and system environment.
            
            This function reads .env files in the following order:
            1. Current working directory (.env)
            2. Home directory (~/.env)
            3. System environment variables
            
            Args:
                key: The environment variable name to look up
                default: Default value if the key is not found (optional)
                
            Returns:
                The value of the environment variable, or the default value if not found
            """
            import os
            from pathlib import Path
            
            # First check system environment variables
            value = os.getenv(key)
            if value is not None:
                return value
            
            # Check .env files
            env_files = []
            
            # Check current working directory
            cwd_env = Path.cwd() / ".env"
            if cwd_env.exists():
                env_files.append(cwd_env)
            
            # Check home directory
            home_env = Path.home() / ".env"
            if home_env.exists():
                env_files.append(home_env)
            
            # Read .env files in order (cwd first, then home)
            for env_file in env_files:
                try:
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            
                            # Skip empty lines and comments
                            if not line or line.startswith('#'):
                                continue
                            
                            # Parse key=value format
                            if '=' in line:
                                env_key, env_value = line.split('=', 1)
                                env_key = env_key.strip()
                                env_value = env_value.strip()
                                
                                # Remove quotes if present
                                if (env_value.startswith('"') and env_value.endswith('"')) or \
                                   (env_value.startswith("'") and env_value.endswith("'")):
                                    env_value = env_value[1:-1]
                                
                                if env_key == key:
                                    return env_value
                                    
                except Exception as e:
                    logger.warning(f"Error reading .env file {env_file}: {e}")
                    continue
            
            # Return default value if not found
            return default
        
        @export_to_lua("start_telnet_server")
        def start_telnet_server(port=8023):
            """Start async telnet server for remote REPL access"""
            import asyncio
            
            # Store active connections and server state
            self.telnet_clients = []
            self.telnet_server_running = False
            self.telnet_server_task = None
            
            async def handle_client(reader, writer):
                """Handle individual client connection asynchronously"""
                client_address = writer.get_extra_info('peername')
                logger.info(f"[Telnet] Client connected: {client_address}")
                
                try:
                    # Send welcome message (user-friendly, no mention of telnet)
                    welcome_msg = "🚀 EPLua Interactive REPL\nType Lua commands and press Enter to execute\nType 'exit' or 'quit' to disconnect\n"
                    writer.write(welcome_msg.encode('utf-8'))
                    await writer.drain()
                    
                    while self.telnet_server_running:
                        try:
                            # Receive command from client
                            data = await reader.read(1024)
                            if not data:
                                break  # Client disconnected
                            
                            command = data.decode('utf-8').strip()
                            if not command:
                                continue
                            
                            # Handle exit commands
                            if command.lower() in ['exit', 'quit']:
                                writer.write("👋 Goodbye!\n".encode('utf-8'))
                                await writer.drain()
                                # Exit the entire EPLua process
                                import os
                                os._exit(0)
                                break
                            
                            # Execute Lua command using decoupled architecture
                            try:
                                # Call Lua's _PY.clientExecute which handles execution and output
                                lua_globals = self.engine._lua.globals()
                                if "_PY" in lua_globals and "clientExecute" in lua_globals["_PY"]:
                                    lua_globals["_PY"]["clientExecute"](1, command)  # client_id = 1 for now
                                else:
                                    # Fallback: execute directly in Lua
                                    result = self.engine._lua.execute(command)
                                    if result is not None:
                                        writer.write(f"{result}\n".encode('utf-8'))
                                        await writer.drain()
                            except Exception as e:
                                # Fallback error handling
                                error_msg = f"Error: {e}\n"
                                writer.write(error_msg.encode('utf-8'))
                                await writer.drain()
                            
                        except Exception as e:
                            logger.error(f"[Telnet] Client error: {e}")
                            break
                            
                except Exception as e:
                    logger.error(f"[Telnet] Client handling error: {e}")
                finally:
                    logger.info(f"[Telnet] Client disconnected: {client_address}")
                    try:
                        writer.close()
                        await writer.wait_closed()
                    except Exception:
                        pass
                    if (reader, writer) in self.telnet_clients:
                        self.telnet_clients.remove((reader, writer))
            
            async def telnet_server_loop():
                """Main async server loop"""
                try:
                    # Create async server
                    server = await asyncio.start_server(
                        handle_client, 
                        'localhost', 
                        port,
                        reuse_address=True
                    )
                    
                    logger.info(f"[Telnet] Server started on localhost:{port}")
                    logger.info("[Telnet] Waiting for connections...")
                    
                    self.telnet_server_running = True
                    
                    async with server:
                        await server.serve_forever()
                        
                except Exception as e:
                    logger.error(f"[Telnet] Server startup error: {e}")
                finally:
                    # Cleanup
                    self.telnet_server_running = False
                    logger.info("[Telnet] Server stopped")
            
            # Start server as an asyncio task
            loop = asyncio.get_event_loop()
            self.telnet_server_task = loop.create_task(telnet_server_loop())
            
            return f"Async telnet server started on localhost:{port}"
        
        @export_to_lua("stop_telnet_server")
        def stop_telnet_server():
            """Stop the async telnet server"""
            if hasattr(self, 'telnet_server_running') and self.telnet_server_running:
                self.telnet_server_running = False
                if hasattr(self, 'telnet_server_task') and self.telnet_server_task:
                    try:
                        self.telnet_server_task.cancel()
                    except Exception:
                        pass
                return "Async telnet server stopped"
            else:
                return "Telnet server not running"
        
        @export_to_lua("get_telnet_status")
        def get_telnet_status():
            """Get telnet server status"""
            if hasattr(self, 'telnet_server_running') and self.telnet_server_running:
                client_count = len(self.telnet_clients) if hasattr(self, 'telnet_clients') else 0
                return f"Running - {client_count} clients connected"
            else:
                return "Not running"
        
        @export_to_lua("clientExecute")
        def client_execute(client_id: int, code: str) -> None:
            """Execute Lua code in client-specific context"""
            # This function is called from Lua's _PY.clientExecute
            # The actual execution is handled by Lua, this just provides the interface
            pass
        
        @export_to_lua("clientPrint")
        def client_print(client_id: int, message: str) -> None:
            """Send output to specific client(s) or stdout"""
            import asyncio
            # print(f"CP {client_id}: {message}", flush=True)
            if client_id == 0 or client_id is None:
                # Print to stdout
                print(message, flush=True)
            elif client_id == -1:
                # Broadcast to all telnet clients, fall back to stdout if no clients
                has_clients = False
                if hasattr(self, 'telnet_server_running') and self.telnet_server_running:
                    if hasattr(self, 'telnet_clients') and self.telnet_clients:
                        has_clients = True
                        disconnected_clients = []
                        for reader, writer in self.telnet_clients:
                            try:
                                # Only add newline if message doesn't already end with one
                                if message.endswith('\n'):
                                    writer.write(message.encode('utf-8'))
                                else:
                                    writer.write(f"{message}\n".encode('utf-8'))
                                # Schedule the drain operation
                                loop = asyncio.get_event_loop()
                                loop.create_task(writer.drain())
                            except Exception:
                                # Client disconnected
                                disconnected_clients.append((reader, writer))
                        
                        # Remove disconnected clients
                        for reader, writer in disconnected_clients:
                            try:
                                writer.close()
                                loop = asyncio.get_event_loop()
                                loop.create_task(writer.wait_closed())
                            except Exception:
                                pass
                            self.telnet_clients.remove((reader, writer))
                
                # If no telnet clients are connected, print to stdout
                if not has_clients:
                    print(message, flush=True)
            elif client_id > 0:
                # Send to specific client
                if hasattr(self, 'telnet_clients') and self.telnet_clients:
                    # Find client by ID (we'll need to track client IDs)
                    # For now, broadcast to all clients
                    # TODO: Implement client ID tracking
                    disconnected_clients = []
                    for reader, writer in self.telnet_clients:
                        try:
                            # Only add newline if message doesn't already end with one
                            if message.endswith('\n'):
                                writer.write(message.encode('utf-8'))
                            else:
                                writer.write(f"{message}\n".encode('utf-8'))
                            # Schedule the drain operation
                            loop = asyncio.get_event_loop()
                            loop.create_task(writer.drain())
                        except Exception:
                            # Client disconnected
                            disconnected_clients.append((reader, writer))
                    
                    # Remove disconnected clients
                    for reader, writer in disconnected_clients:
                        try:
                            writer.close()
                            loop = asyncio.get_event_loop()
                            loop.create_task(writer.wait_closed())
                        except Exception:
                            pass
                        self.telnet_clients.remove((reader, writer))
        
        # Refresh states polling and event queue functions
        
        @export_to_lua("start_refresh_states_polling")
        def start_refresh_states_polling(url: str, interval_seconds: float = 1.0) -> bool:
            """Start background polling for refresh states"""
            import threading
            import time
            import requests
            from typing import Dict, Any
            
            try:
                def poll_refresh_states():
                    """Background thread function for polling refresh states"""
                    while getattr(threading.current_thread(), "running", True):
                        try:
                            # Make the HTTP request
                            response = requests.get(url, timeout=5)
                            if response.status_code == 200:
                                data = response.json()
                                
                                # Convert Python data to Lua-compatible format
                                lua_data = python_to_lua_table(data)
                                
                                # Send result to Lua via thread-safe callback
                                self.engine.execute_script_from_thread(
                                    f"if _G.onRefreshStatesUpdate then _G.onRefreshStatesUpdate({lua_data}) end"
                                )
                            
                        except Exception as e:
                            # Log error and continue polling
                            print(f"Refresh states polling error: {e}")
                        
                        # Sleep for the specified interval
                        time.sleep(interval_seconds)
                
                # Create and start the polling thread
                thread = threading.Thread(target=poll_refresh_states, daemon=True)
                thread.running = True
                thread.start()
                
                # Store thread reference for later cleanup
                if not hasattr(self, 'refresh_states_thread'):
                    self.refresh_states_thread = thread
                
                return True
                
            except Exception as e:
                print(f"Failed to start refresh states polling: {e}")
                return False
        
        @export_to_lua("stop_refresh_states_polling")
        def stop_refresh_states_polling() -> bool:
            """Stop background polling for refresh states"""
            try:
                if hasattr(self, 'refresh_states_thread') and self.refresh_states_thread:
                    # Signal thread to stop
                    self.refresh_states_thread.running = False
                    self.refresh_states_thread.join(timeout=2.0)
                    self.refresh_states_thread = None
                    return True
                return False
            except Exception as e:
                print(f"Failed to stop refresh states polling: {e}")
                return False
        
        @export_to_lua("init_event_queue")
        def init_event_queue() -> bool:
            """Initialize the global event queue"""
            try:
                import queue
                
                if not hasattr(self, 'event_queue'):
                    self.event_queue = queue.Queue()
                return True
                
            except Exception as e:
                print(f"Failed to initialize event queue: {e}")
                return False
        
        @export_to_lua("add_event")
        def add_event(event_data: Any) -> bool:
            """Add an event to the global event queue"""
            try:
                # Initialize queue if not exists
                if not hasattr(self, 'event_queue'):
                    init_event_queue()
                
                # Convert to Lua-compatible format before storing
                lua_event = python_to_lua_table(event_data)
                self.event_queue.put(lua_event)
                return True
                
            except Exception as e:
                print(f"Failed to add event to queue: {e}")
                return False
        
        @export_to_lua("get_events")
        def get_events(max_events: int = 10) -> Any:
            """Get events from the global event queue (non-blocking)"""
            try:
                import queue
                
                if not hasattr(self, 'event_queue'):
                    init_event_queue()
                    return python_to_lua_table([])
                
                events = []
                q = self.event_queue
                
                # Get up to max_events from the queue
                for _ in range(max_events):
                    try:
                        event = q.get_nowait()
                        events.append(event)
                    except queue.Empty:
                        break
                
                return python_to_lua_table(events)
                
            except Exception as e:
                print(f"Failed to get events from queue: {e}")
                return python_to_lua_table([])
        
        @export_to_lua("get_event_count")
        def get_event_count() -> int:
            """Get the current number of events in the queue"""
            try:
                if hasattr(self, 'event_queue'):
                    return self.event_queue.qsize()
                return 0
                
            except Exception as e:
                print(f"Failed to get event count: {e}")
                return 0
        
        @export_to_lua("clear_events")
        def clear_events() -> bool:
            """Clear all events from the global event queue"""
            try:
                if hasattr(self, 'event_queue'):
                    q = self.event_queue
                    # Clear the queue
                    while not q.empty():
                        try:
                            q.get_nowait()
                        except:
                            break
                    return True
                return False
                
            except Exception as e:
                print(f"Failed to clear event queue: {e}")
                return False
        
    def get_all_bindings(self) -> Dict[str, Any]:
        """
        Get all available bindings for Lua.
        
        Returns:
            Dictionary containing all exported functions
        """
        return get_exported_functions()
        
    def create_timer_bindings(self) -> Dict[str, Callable]:
        """
        Legacy method for timer bindings (deprecated, use get_all_bindings).
        """
        bindings = get_exported_functions()
        return {
            "set_timeout": bindings["set_timeout"],
            "clear_timeout": bindings["clear_timeout"], 
            "get_timer_count": bindings["get_timer_count"],
        }
        
    def create_engine_bindings(self) -> Dict[str, Callable]:
        """
        Legacy method for engine bindings (deprecated, use get_all_bindings).
        """
        bindings = get_exported_functions()
        return {
            "print": bindings["print"],
            "log": bindings["log"],
            "get_time": bindings["get_time"],
            "sleep": bindings["sleep"],
        }
