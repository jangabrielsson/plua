"""
Core Lua Engine with Async Timer Support

This module provides the main LuaEngine class that integrates Lupa for Lua script
execution with Python's async timer functionality.
"""

import asyncio
import logging
import uuid
import time
import queue

import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union
import lupa

from .timers import AsyncTimerManager
from .lua_bindings import LuaBindings, set_global_engine
# Import extensions to register decorated functions
from . import extensions  # noqa: F401,F811

logger = logging.getLogger(__name__)


class LuaEngine:
    """
    Core engine for executing Lua scripts with integrated async timer support.

    This class provides the main interface for running Lua scripts that can
    interact with Python's async timer system and other Python functionality.
    """

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Lua engine.

        Args:
            loop: Event loop to use. If None, will try to get the current loop.
            config: Configuration dictionary with platform info and CLI flags.
        """
        logger.debug("Initializing Lua engine")
        # Store config for later use
        self._config = config or {}
        # Add pylib directory to Python path for FFI library loading
        pylib_path = Path(__file__).parent.parent / "pylib"
        if pylib_path.exists() and str(pylib_path) not in sys.path:
            sys.path.insert(0, str(pylib_path.parent))
            logger.debug(f"Added pylib parent directory to Python path: {pylib_path.parent}")

        if loop:
            self._loop = loop
        else:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, we'll set it when start() is called
                self._loop = None

        self._lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        self._timer_manager = AsyncTimerManager()
        self._bindings = LuaBindings(self._timer_manager, self)
        self._running = False
        self._scripts: Dict[str, str] = {}  # Store loaded scripts

        # Thread-safe queue for cross-thread callback communication
        self._callback_queue = queue.Queue()

        # Thread-safe queue for execution requests from other threads
        self._execution_queue = queue.Queue()
        self._execution_results = {}  # Store results by request ID

        self._queue_processor_task = None

        # Set this engine as the global instance
        set_global_engine(self)

        self._setup_lua_environment()

    def _setup_lua_environment(self):
        """Set up the Lua environment with Python bindings."""
        logger.debug("Setting up Lua environment")

        # Get all exported functions
        all_bindings = self._bindings.get_all_bindings()

        # Create _PY table for Python bridge functions
        py_table = self._lua.table()
        for name, func in all_bindings.items():
            py_table[name] = func

        # Add config table with platform information
        config_table = self._lua.table()

        # Use provided config or create default
        config_data = self._config
        if not config_data:
            # Fallback: create default config if none provided
            config_data = {
                "platform": sys.platform,
                "fileSeparator": "\\\\" if sys.platform == "win32" else "/",
                "pathSeparator": ";" if sys.platform == "win32" else ":",
                "isWindows": sys.platform == "win32",
                "isMacOS": sys.platform == "darwin",
                "isLinux": sys.platform.startswith("linux"),
                "pythonVersion": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "enginePath": str(Path(__file__).parent.parent).replace("\\", "/"),
                "luaLibPath": str(Path(__file__).parent.parent / "lua").replace("\\", "/"),
                "offline": False,
            }

        # Populate Lua table with config data
        from .lua_bindings import python_to_lua_table
        for key, value in config_data.items():
            if isinstance(value, list):
                # Convert Python lists to Lua tables
                config_table[key] = python_to_lua_table(value)
            else:
                config_table[key] = value

        py_table["config"] = config_table

        self._lua.globals()["_PY"] = py_table

        # Override Lua's print function with our enhanced version
        if "print" in all_bindings:
            self._lua.globals()["print"] = all_bindings["print"]

        # Load the init.lua file that sets up timer functions
        init_lua_path = Path(__file__).parent.parent / "lua" / "init.lua"
        if init_lua_path.exists():
            logger.debug("Loading init.lua")
            # Use Lua's loadfile function with qualified filename
            qualified_filename = str(init_lua_path)
            qualified_filename = qualified_filename.replace("\\", "\\\\")  # Escape backslashes for Lua
            lua_loadfile_code = f"loadfile('{qualified_filename}')()"
            self._lua.execute(lua_loadfile_code)
        else:
            logger.warning("init.lua not found, timer functions may not be available")

        logger.debug("Lua environment setup complete")

    async def start(self):
        """Start the Lua engine and timer manager."""
        if self._running:
            logger.warning("Engine is already running")
            return

        # Set the loop if we don't have one yet
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        logger.info("Starting Lua engine")
        self._running = True
        await self._timer_manager.start()

        # Start the queue processor task
        self._queue_processor_task = asyncio.create_task(self._process_queues())

    async def _process_queues(self):
        """Process callbacks and execution requests from other threads."""
        while self._running:
            try:
                # Process callback queue
                try:
                    callback_data = self._callback_queue.get_nowait()
                    callback_id, error, result = callback_data

                    # Call the Lua callback
                    self._lua.globals()["_PY"]["timerExpired"](callback_id, error, result)

                except queue.Empty:
                    pass  # No callbacks pending

                # Process execution queue
                try:
                    execution_request = self._execution_queue.get_nowait()
                    request_id, script, timeout_seconds, is_json = execution_request

                    # Execute the script via Lua's threadRequest system
                    try:
                        start_time = time.time()

                        # Call the Lua threadRequest function which will handle execution
                        # and callback to threadRequestResult when done
                        self._lua.globals()["_PY"]["threadRequest"](request_id, script, is_json)

                        # Note: The actual result will be stored via handle_thread_request_result
                        # when Lua calls _PY.threadRequestResult(id, result)

                    except Exception as e:
                        # Store the error immediately if Lua call fails
                        self._execution_results[request_id] = {
                            "success": False,
                            "result": None,
                            "execution_time": time.time() - start_time,
                            "error": f"Failed to execute threadRequest: {str(e)}"
                        }

                except queue.Empty:
                    pass  # No execution requests pending

                # Sleep briefly if no work was done
                await asyncio.sleep(0.01)

            except Exception as e:
                logger.error(f"Error processing callback queue: {e}")
                await asyncio.sleep(0.1)

    async def stop(self):
        """Stop the Lua engine and clean up resources."""
        if not self._running:
            logger.warning("Engine is not running")
            return

        logger.info("Stopping Lua engine")
        self._running = False
        await self._timer_manager.stop()

        # Cancel the queue processor task
        if self._queue_processor_task:
            self._queue_processor_task.cancel()
            try:
                await self._queue_processor_task
            except asyncio.CancelledError:
                pass

    def execute_lua(self, lua_code: str, script_name: Optional[str] = None) -> Any:
        """
        Execute Lua code synchronously.

        Args:
            lua_code: The Lua code to execute
            script_name: Optional name for the script (for debugging)

        Returns:
            Result of the Lua execution

        Raises:
            lupa.LuaError: If there's an error in the Lua code
        """
        if script_name:
            logger.debug(f"Executing Lua script: {script_name}")
        else:
            logger.debug("Executing Lua code")

        try:
            result = self._lua.execute(lua_code)
            logger.debug("Lua execution completed successfully")
            return result
        except lupa.LuaError as e:
            logger.error(f"Lua execution error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Lua execution: {e}")
            raise

    async def run_script(self, lua_code: str, script_name: Optional[str] = None) -> Any:
        """
        Run Lua code asynchronously.

        Args:
            lua_code: The Lua code to execute
            script_name: Optional name for the script (for debugging)

        Returns:
            Result of the Lua execution
        """
        if not self._running:
            await self.start()

        # Store the script if a name is provided
        if script_name:
            self._scripts[script_name] = lua_code

        # Execute directly in the main thread for now to avoid threading issues
        # with timer creation. In a production system, you might want to use
        # a different approach for CPU-intensive Lua scripts.
        try:
            result = self.execute_lua(lua_code, script_name)
            return result
        except Exception as e:
            logger.error(f"Error in run_script: {e}")
            raise

    async def load_and_run_file(self, file_path: Union[str, Path]) -> Any:
        """
        Load and run a Lua script from a file.

        Args:
            file_path: Path to the Lua script file

        Returns:
            Result of the Lua execution

        Raises:
            FileNotFoundError: If the file doesn't exist
            lupa.LuaError: If there's an error in the Lua code
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Lua script not found: {file_path}")

        logger.info(f"Loading Lua script from: {file_path}")
        lua_code = file_path.read_text(encoding='utf-8')

        return await self.run_script(lua_code, script_name=file_path.name)

    def get_lua_global(self, name: str) -> Any:
        """
        Get a global variable from the Lua environment.

        Args:
            name: Name of the global variable

        Returns:
            Value of the global variable
        """
        return self._lua.globals()[name]

    def set_lua_global(self, name: str, value: Any) -> None:
        """
        Set a global variable in the Lua environment.

        Args:
            name: Name of the global variable
            value: Value to set
        """
        self._lua.globals()[name] = value

    def get_timer_manager(self) -> AsyncTimerManager:
        """Get the timer manager instance."""
        return self._timer_manager

    def get_pending_callback_count(self) -> int:
        """Get the count of pending callbacks (includes timers, HTTP requests, etc.)."""
        try:
            return self._lua.globals()["_PY"]["getPendingCallbackCount"]()
        except Exception:
            # If the function doesn't exist or there's an error, return 0
            return 0

    def get_running_intervals_count(self) -> int:
        """Get the count of active intervals."""
        try:
            return self._lua.globals()["_PY"]["getRunningIntervalsCount"]()
        except Exception:
            # If the function doesn't exist or there's an error, return 0
            return 0

    def has_active_operations(self) -> bool:
        """Check if there are any active async operations (callbacks or intervals)."""
        callback_count = self.get_pending_callback_count()
        interval_count = self.get_running_intervals_count()
        
        # Debug logging to understand what's keeping the script alive
        if callback_count > 0 or interval_count > 0:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Active operations: callbacks={callback_count}, intervals={interval_count}")
        
        return callback_count > 0 or interval_count > 0

    def post_callback_from_thread(self, callback_id: int, error=None, result=None):
        """
        Post a callback result from another thread.

        This is thread-safe and can be called from any Python thread.
        The callback will be executed in the main event loop.

        Args:
            callback_id: The callback ID from _PY.registerCallback()
            error: Error message if any (None for success)
            result: Result data to pass to the callback
        """
        try:
            self._callback_queue.put_nowait((callback_id, error, result))
        except queue.Full:
            logger.error(f"Callback queue is full, dropping callback {callback_id}")

    def execute_script_from_thread(self, script: str, timeout_seconds: float = 30.0, is_json: bool = False):
        """
        Execute a Lua script from another thread and wait for the result.

        This is thread-safe and can be called from any Python thread.
        The script will be executed in the main event loop.

        Args:
            script: The Lua script to execute OR JSON function call data
            timeout_seconds: Maximum time to wait for execution
            is_json: If True, treat script as JSON function call data

        Returns:
            Dict with execution result: {"success": bool, "result": Any, "execution_time": float, "error": str}
        """

        request_id = str(uuid.uuid4())

        try:
            # Post the execution request with the is_json flag
            self._execution_queue.put_nowait((request_id, script, timeout_seconds, is_json))
        except queue.Full:
            return {
                "success": False,
                "result": None,
                "execution_time": 0,
                "error": "Execution queue is full"
            }

        # Wait for the result with timeout
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if request_id in self._execution_results:
                result = self._execution_results.pop(request_id)
                return result
            time.sleep(0.01)  # Small sleep to avoid busy waiting

        # Cleanup if timeout
        self._execution_results.pop(request_id, None)
        return {
            "success": False,
            "result": None,
            "execution_time": timeout_seconds,
            "error": f"Script execution timeout after {timeout_seconds} seconds"
        }

    def handle_thread_request_result(self, request_id: str, result: Any):
        """
        Handle the result of a thread-safe script execution request.
        Called from Lua via the threadRequestResult function.

        Args:
            request_id: The ID of the execution request
            result: The result data from the Lua execution
        """
        # Convert Lua result to Python data if needed
        if result is not None and hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
            try:
                from .lua_bindings import lua_to_python_table
                result = lua_to_python_table(result)
            except Exception as conv_error:
                logger.warning(f"Failed to convert Lua result: {conv_error}")
                # Keep the original result if conversion fails

        # Store the result for the waiting thread
        self._execution_results[request_id] = result

    def get_bindings(self) -> LuaBindings:
        """Get the Lua bindings instance."""
        return self._bindings

    def is_running(self) -> bool:
        """Check if the engine is running."""
        return self._running

    def get_loaded_scripts(self) -> Dict[str, str]:
        """Get a dictionary of loaded scripts."""
        return self._scripts.copy()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
