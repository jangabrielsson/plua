"""
Lua-Python bindings for the PLua engine.

This module provides the bridge between Lua scripts and Python functionality,
specifically for timer operations and other engine features.
"""

import logging
from typing import Any, Callable, Dict, Optional
import os
import socket
import subprocess
import platform
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
            """Exit the PLua process with the specified exit code"""
            import os
            import sys
            
            # Simple approach: just exit and let the system handle cleanup
            # On Windows, multiprocessing might complain but that's after we've exited
            sys.exit(code)
            
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
                    "cwd": os.getcwd().replace("\\", "/"),
                    "user": os.environ.get("USERNAME") or os.environ.get("USER", "unknown"),
                    "home": (os.environ.get("USERPROFILE") or os.environ.get("HOME", "unknown")).replace("\\", "/"),
                    "path_separator": os.pathsep,
                    "line_separator": os.linesep
                },
                "runtime": {
                    "current_time": time.time(),
                    "pid": os.getpid()
                }
            }
            return python_to_lua_table(info)
            
        @export_to_lua("getConfig")
        def get_config() -> Any:
            """Get the current engine configuration as Lua table."""
            if self.engine and hasattr(self.engine, 'config') and self.engine.config:
                return python_to_lua_table(self.engine.config)
            else:
                return python_to_lua_table({})
        
        # Additional utility functions
        @export_to_lua("utime")
        def utime(file: str, creation: int, mod: int) -> float:
            """Update the access and modification times of a file."""
            return os.utime(file, (creation, mod))

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
        
        @export_to_lua("is_directory")
        def is_directory(filename: str) -> bool:
            """
            Check if a file is a directory.
            """
            import os
            return os.path.isdir(filename)

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
        
        @export_to_lua("start_repl")
        def start_repl():
            """Start async REPL that reads from stdin and writes to stdout"""
            import asyncio
            import sys
            
            # Check if REPL is already running
            if hasattr(self, 'repl_running') and self.repl_running:
                return "REPL already running"
            
            # Initialize REPL state
            self.repl_running = False
            self.repl_task = None
            
            async def repl_loop():
                """Main async REPL loop with prompt_toolkit"""
                try:
                    # Try to import prompt_toolkit for enhanced REPL
                    try:
                        from prompt_toolkit import PromptSession
                        from prompt_toolkit.shortcuts import print_formatted_text
                        from prompt_toolkit.formatted_text import HTML
                        has_prompt_toolkit = True
                    except ImportError:
                        has_prompt_toolkit = False
                        logger.warning("prompt_toolkit not available, using basic input")
                    
                    if has_prompt_toolkit:
                        session = PromptSession()
                        print_formatted_text(HTML('<ansigreen>🚀 PLua Interactive REPL</ansigreen>'))
                        print_formatted_text(HTML('<ansicyan>Type Lua commands and press Enter to execute</ansicyan>'))
                        print_formatted_text(HTML('<ansicyan>Type "exit" or "quit" to stop, Ctrl+C to interrupt</ansicyan>'))
                    else:
                        # Import Rich console for better REPL output
                        try:
                            from .console import console
                            console.print("🚀 PLua Interactive REPL", style="version")
                            console.print("Type Lua commands and press Enter to execute", style="info")
                            console.print("Type 'exit' or 'quit' to stop, Ctrl+C to interrupt", style="dim")
                        except ImportError:
                            # Fallback if Rich is not available
                            print("🚀 PLua Interactive REPL")
                            print("Type Lua commands and press Enter to execute")
                            print("Type 'exit' or 'quit' to stop, Ctrl+C to interrupt")
                    
                    self.repl_running = True
                    
                    while self.repl_running:
                        try:
                            if has_prompt_toolkit:
                                # Use prompt_toolkit for better user experience
                                command = await session.prompt_async('lua> ')
                            else:
                                # Fallback to basic input
                                print('lua> ', end='', flush=True)
                                command = await asyncio.get_event_loop().run_in_executor(None, input)
                            
                            command = command.strip()
                            if not command:
                                continue
                            
                            # Handle exit commands
                            if command.lower() in ['exit', 'quit']:
                                try:
                                    from .console import console
                                    console.print("👋 Goodbye!", style="success")
                                except ImportError:
                                    print("👋 Goodbye!")
                                self.repl_running = False
                                break
                            
                            # Execute Lua command
                            try:
                                lua_globals = self.engine._lua.globals()
                                if "_PY" in lua_globals and "clientExecute" in lua_globals["_PY"]:
                                    # Use clientId=0 for stdout output
                                    lua_globals["_PY"]["clientExecute"](0, command)
                                else:
                                    # Fallback: execute directly in Lua and print result
                                    result = self.engine._lua.execute(command)
                                    if result is not None:
                                        try:
                                            from .console import console
                                            console.print(f"=> {result}", style="bright")
                                        except ImportError:
                                            print(f"=> {result}")
                            except Exception as e:
                                try:
                                    from .console import console
                                    console.print(f"Error: {e}", style="error")
                                except ImportError:
                                    print(f"Error: {e}")
                            
                        except (EOFError, KeyboardInterrupt):
                            try:
                                from .console import console
                                console.print("\n👋 Goodbye!", style="success")
                            except ImportError:
                                print("\n👋 Goodbye!")
                            self.repl_running = False
                            break
                        except Exception as e:
                            logger.error(f"[REPL] Error: {e}")
                            break
                            
                except Exception as e:
                    logger.error(f"[REPL] Fatal error: {e}")
                finally:
                    self.repl_running = False
                    logger.info("[REPL] Stopped")
            
            # Start REPL as an asyncio task
            if not self.repl_running:
                self.repl_running = True  # Set to True before starting task
                loop = asyncio.get_event_loop()
                self.repl_task = loop.create_task(repl_loop())
                logger.info("[REPL] Started on stdin/stdout")
                return "REPL started on stdin/stdout"
            else:
                return "REPL already running"
        
        @export_to_lua("stop_repl")
        def stop_repl():
            """Stop the async REPL"""
            if hasattr(self, 'repl_running') and self.repl_running:
                self.repl_running = False
                if hasattr(self, 'repl_task') and self.repl_task:
                    try:
                        self.repl_task.cancel()
                    except Exception:
                        pass
                return "REPL stopped"
            else:
                return "REPL not running"
        
        @export_to_lua("get_repl_status")
        def get_repl_status():
            """Get REPL status"""
            if hasattr(self, 'repl_running') and self.repl_running:
                return "Running on stdin/stdout"
            else:
                return "Not running"
        
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
                    welcome_msg = "🚀 PLua Interactive REPL\nType Lua commands and press Enter to execute\nType 'exit' or 'quit' to disconnect\n"
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
                                # Exit the entire PLua process
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
        
        # Refresh states polling and event queue functions (HC3 compatible)
        
        # Initialize global state for refresh states
        if not hasattr(self, '_refresh_thread'):
            self._refresh_thread = None
        if not hasattr(self, '_refresh_running'):
            self._refresh_running = False
        if not hasattr(self, '_events'):
            from collections import deque
            self._events = deque(maxlen=1000)  # MAX_EVENTS = 1000
        if not hasattr(self, '_event_count'):
            self._event_count = 0
        if not hasattr(self, '_events_lock'):
            import threading
            self._events_lock = threading.Lock()
        
        def _convert_lua_table(lua_table):
            """Convert Lua table to Python dict"""
            if isinstance(lua_table, dict):
                return lua_table
            elif hasattr(lua_table, 'items'):
                return dict(lua_table.items())
            else:
                return {}
        
        @export_to_lua("pollRefreshStates")
        def pollRefreshStates(start: int, url: str, options: Any) -> dict:
            """Start polling refresh states in a background thread (HC3 compatible)"""
            import threading
            import time
            import requests
            import sys
            # Stop existing thread if running
            if self._refresh_running and self._refresh_thread:
                self._refresh_running = False
                self._refresh_thread.join(timeout=1)
            
            # Convert Lua options to Python dict
            options_dict = _convert_lua_table(options)
            
            def refresh_runner():
                last, retries = start, 0
                self._refresh_running = True
                
                while self._refresh_running:
                    try:
                        nurl = url + str(last) + "&lang=en&rand=7784634785"
                        resp = requests.get(nurl, headers=options_dict.get('headers', {}), timeout=30)
                        if resp.status_code == 200:
                            retries = 0
                            data = resp.json()
                            last = data.get('last', last)
                            
                            if data.get('events'):
                                for event in data['events']:
                                    # Use addEvent function directly with dict for efficiency
                                    addEvent(event)
                        
                        elif resp.status_code == 401:
                            logger.error("HC3 credentials error")
                            logger.error("Exiting refreshStates loop")
                            break
                    
                    except requests.exceptions.Timeout:
                        pass
                    except requests.exceptions.ConnectionError:
                        retries += 1
                        if retries > 5:
                            logger.error(f"Connection error: {nurl}")
                            logger.error("Exiting refreshStates loop")
                            break
                    except Exception as e:
                        logger.error(f"Error: {e} {nurl}")

                    # Sleep between requests
                    time.sleep(1)
                
                self._refresh_running = False
            
            # Start the thread
            self._refresh_thread = threading.Thread(target=refresh_runner, daemon=True)
            self._refresh_thread.start()
            
            return {"status": "started", "thread_id": self._refresh_thread.ident}
        
        @export_to_lua("addEvent")
        def addEvent(event: Any) -> dict:
            """Add an event to the event queue - accepts dict only (HC3 compatible)"""
            import json
            try:
                with self._events_lock:
                    self._event_count += 1
                    event_with_counter = {'last': self._event_count, 'event': event}
                    self._events.append(event_with_counter)
                
                # Call _PY.newRefreshStatesEvent if it exists (for Lua event hooks)
                try:
                    if hasattr(self.engine._lua.globals(), '_PY') and hasattr(self.engine._lua.globals()['_PY'], 'newRefreshStatesEvent'):
                        if isinstance(event, str):
                            self.engine._lua.globals()['_PY']['newRefreshStatesEvent'](event)
                        else:
                            self.engine._lua.globals()['_PY']['newRefreshStatesEvent'](json.dumps(event))
                except Exception as e:
                    # Silently ignore errors in event hook - don't break the queue
                    pass
                
                return {"status": "added", "event_count": self._event_count}
            except Exception as e:
                logger.error(f"Error adding event: {e}")
                return {"status": "error", "error": str(e)}
        
        @export_to_lua("addEventFromLua")
        def addEventFromLua(event_json: str) -> dict:
            """Add an event to the event queue from Lua (JSON string input)"""
            import json
            try:
                event = json.loads(event_json)
                return addEvent(event)
            except Exception as e:
                logger.error(f"Error parsing event JSON: {e}")
                return {"status": "error", "error": str(e)}
        
        @export_to_lua("getEvents")
        def getEvents(counter: int = 0) -> dict:
            """Get events since the given counter (HC3 compatible)"""
            import time
            from datetime import datetime
            
            with self._events_lock:
                events = list(self._events)  # Copy to avoid race conditions
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
            return python_to_lua_table(res)
        
        @export_to_lua("stopRefreshStates")
        def stopRefreshStates() -> bool:
            """Stop refresh states polling (HC3 compatible)"""
            try:
                if self._refresh_running and self._refresh_thread:
                    self._refresh_running = False
                    self._refresh_thread.join(timeout=2.0)
                    self._refresh_thread = None
                    return True
                return False
            except Exception as e:
                logger.error(f"Error stopping refresh states: {e}")
                return False
        
        @export_to_lua("getRefreshStatesStatus")
        def getRefreshStatesStatus() -> dict:
            """Get refresh states polling status (HC3 compatible)"""
            try:
                if self._refresh_thread and self._refresh_running:
                    return {
                        'running': self._refresh_thread.is_alive() if self._refresh_thread else False,
                        'thread_id': self._refresh_thread.ident if self._refresh_thread else None
                    }
                return {'running': False}
            except Exception as e:
                logger.error(f"Error getting refresh states status: {e}", file=sys.stderr)
                return {'running': False, 'error': str(e)}

    def get_all_bindings(self) -> Dict[str, Any]:
        """
        Get all available bindings for Lua.
        
        Returns:
            Dictionary containing all exported functions
        """
        return get_exported_functions()

@export_to_lua("wake_network_device")
def wake_network_device(host: str, timeout: float = 5.0) -> bool:
    """
    Attempt to wake up a network device that may have sleeping network interfaces.
    
    This function tries multiple approaches:
    1. ARP ping to refresh ARP tables
    2. TCP connection attempts on common ports
    3. Platform-specific ping with broadcast
    
    Args:
        host: IP address or hostname of the device
        timeout: Timeout in seconds for each attempt
        
    Returns:
        True if device responds, False otherwise
    """
    try:
        logger.info(f"Attempting to wake network device: {host}")
        
        # Method 1: Try ARP ping (if available)
        try:
            if platform.system().lower() == "linux":
                result = subprocess.run(
                    ["arping", "-c", "1", "-W", str(int(timeout)), host],
                    capture_output=True,
                    timeout=timeout
                )
                if result.returncode == 0:
                    logger.info(f"ARP ping successful for {host}")
                    return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # arping not available or timed out
        
        # Method 2: TCP connection attempts on common ports
        common_ports = [80, 443, 22, 23, 8080, 11111]  # Common HC3 ports
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout / len(common_ports))
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    logger.info(f"TCP connection successful to {host}:{port}")
                    return True
            except Exception:
                continue
        
        # Method 3: ICMP ping with broadcast-like behavior
        try:
            ping_cmd = ["ping", "-c", "1", "-W", str(int(timeout * 1000))]
            if platform.system().lower() == "darwin":  # macOS
                ping_cmd = ["ping", "-c", "1", "-t", str(int(timeout))]
            elif platform.system().lower() == "windows":
                ping_cmd = ["ping", "-n", "1", "-w", str(int(timeout * 1000))]
            
            ping_cmd.append(host)
            result = subprocess.run(ping_cmd, capture_output=True, timeout=timeout)
            if result.returncode == 0:
                logger.info(f"Ping successful for {host}")
                return True
        except subprocess.TimeoutExpired:
            pass
        
        # Method 4: Try UDP broadcast on same subnet (last resort)
        try:
            # Parse IP to determine broadcast address
            ip_parts = host.split('.')
            if len(ip_parts) == 4:
                broadcast_addr = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.255"
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.settimeout(1.0)
                # Send a small UDP packet to broadcast
                sock.sendto(b"wake", (broadcast_addr, 9))
                sock.close()
                logger.info(f"Sent broadcast packet to wake {host}")
        except Exception:
            pass
        
        logger.warning(f"Failed to wake network device: {host}")
        return False
        
    except Exception as e:
        logger.error(f"Error in wake_network_device: {e}")
        return False

@export_to_lua("py_sleep")
def py_sleep(milliseconds: int):
    """Sleep for the specified number of milliseconds (blocking)."""
    import time
    time.sleep(milliseconds / 1000.0)
        
