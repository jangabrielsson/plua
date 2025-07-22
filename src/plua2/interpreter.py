"""
Lua interpreter class for managing Lua runtime and script execution
"""

import lupa
from datetime import datetime
from typing import Any, Callable, Optional
from . import __version__
from .syncsocket import SynchronousTCPManager
from .luafuns_lib import lua_exporter
from . import html_extensions  # Import to register HTML functions
from . import network  # Import to register network functions


class LuaInterpreter:
    """
    A class that manages the Lua runtime environment and script execution
    """
    
    def __init__(self, debug: bool = False):
        self.lua: Optional[lupa.LuaRuntime] = None
        self._debug = debug
        self.tcp_manager = SynchronousTCPManager(debug_print=self.debug_print)  # Handle TCP socket operations
        self.output_buffer = []  # Buffer for capturing print output
        self.web_mode = False  # Flag to control HTML/ANSI conversion
        self._fastapi_app = None  # Store FastAPI app reference for internal calls
        
    def debug_print(self, message: str) -> None:
        """Centralized debug printing - can be extended with other global utilities"""
        if self._debug:
            print(message)
            
    def set_broadcast_view_update_hook(self, broadcast_func: Callable[[int, str, str, str], None]) -> None:
        """Set the granular broadcast view update hook function"""
        if self.lua and hasattr(self, 'PY') and self.PY:
            self.PY.broadcast_view_update = broadcast_func  
        else:
            # Store for later if _PY table doesn't exist yet
            self._pending_view_hook = broadcast_func
            
    def set_debug_mode(self, debug: bool) -> None:
        """Update debug mode setting after construction"""
        self._debug = debug
        # Update the network manager's debug function to use the new setting
        self.tcp_manager._debug_print = self.debug_print

    def curr_time(self) -> str:
        """Get current time formatted as HH:MM:SS.mmm"""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def lua_print(self, *args: Any) -> None:
        """Lua print function that converts HTML to terminal-friendly output and captures to buffer"""
        import re
        import sys
        from .html_extensions import html2console
        
        # Convert each argument to string and join them
        output = " ".join(str(arg) for arg in args)
        
        # Check if output contains HTML tags (like <font color='...'>)
        has_html = re.search(r'<[^>]+>', output)
        
        if has_html:
            # Store the original HTML version in the buffer for web interface
            self.output_buffer.append(output)
            
            # For terminal output, convert to ANSI only if not in web mode
            if not self.web_mode:
                try:
                    # Apply HTML conversion to handle font tags, br, &nbsp;, etc.
                    ansi_output = html2console(output)
                    print(ansi_output, file=sys.stdout)
                    sys.stdout.flush()
                except Exception:
                    # If conversion fails, print original
                    print(output, file=sys.stdout)
                    sys.stdout.flush()
        else:
            # No HTML, store and print as-is
            self.output_buffer.append(output)
            if not self.web_mode:
                print(output, file=sys.stdout)
                sys.stdout.flush()

    def initialize(
        self, 
        python_timer_func: Callable[[int, int], Any],
        python_cancel_timer_func: Callable[[int], bool]
    ) -> None:
        """
        Initialize the Lua runtime and set up environment
        
        Args:
            python_timer_func: Function to call when setting timers from Lua
            python_cancel_timer_func: Function to call when canceling timers from Lua
        """
        start_time = self.curr_time()
        self.debug_print(f"Starting Lua runtime...")
        
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        # _PY table with native python functions exported to Lua
        py_table = self.lua.table()
        self.PY = py_table  # Store for convenience
        self.lua.globals()._PY = py_table

        # Initialize broadcast hooks as nil - FastAPI will set them when ready
        py_table.broadcast_view_update = getattr(self, '_pending_view_hook', None)
        
        # Clean up pending hooks
        if hasattr(self, '_pending_view_hook'):
            delattr(self, '_pending_view_hook')

        # Set up Lua globals
        self.lua.globals().print = self.lua_print
        
        py_table._debug = self._debug
        py_table.pythonTimer = python_timer_func
        py_table.pythonCancelTimer = python_cancel_timer_func
        
        # Initialize hook system (hooks will be set by init.lua and can be overridden)
        # py_table.main_file_hook will be set by init.lua with default implementation
        py_table.fibaro_api_hook = None  # Function to handle Fibaro API requests: (method, path, data) -> (data, status_code)
        
        # Set up _PY table with synchronous TCP functions for socket.lua
        py_table.tcp_connect_sync = self.tcp_manager.tcp_connect_sync
        py_table.tcp_write_sync = self.tcp_manager.tcp_write_sync
        py_table.tcp_read_sync = self.tcp_manager.tcp_read_sync
        py_table.tcp_close_sync = self.tcp_manager.tcp_close_sync
        py_table.tcp_set_timeout_sync = self.tcp_manager.tcp_set_timeout_sync
        
        # Export get runtime state function
        def get_runtime_state():
            """Get runtime state for Lua isRunning hook"""
            return self.get_runtime_state()
        
        get_runtime_state._lua_runtime = self.lua
        py_table.getRuntimeState = get_runtime_state

        # Add exported Python functions from luafuns_lib BEFORE executing init script
        self._register_exported_functions(py_table)
        
        # Set up config table with system information
        try:
            config_data = py_table.get_config()
            py_table.config = config_data
        except Exception as e:
            self.debug_print(f"Warning: Could not initialize _PY.config: {e}")
            py_table.config = {}
        
        # Execute init script after all functions are registered
        # Use loadfile for proper source mapping and debugging support
        import os
        init_script_path = os.path.join(os.path.dirname(__file__), '..', 'lua', 'init.lua')
        
        # Use Lua's loadfile for proper source mapping
        init_load_script = f"""
local func, err = loadfile({init_script_path!r})
if func then
    func()
else
    error("Failed to load init.lua: " .. tostring(err))
end
"""
        self.lua.execute(init_load_script)
        
        self.debug_print(f"Lua runtime initialized")

    def execute_script(self, script: str, source_name: str = None, debugging: bool = False, debug: bool = False) -> None:
        """
        Execute a Lua script
        
        Args:
            script: The Lua script to execute
            source_name: Optional source file name for source mapping (e.g., "test_debugger.lua")
            debugging: Whether this script should be loaded for debugging (deferred execution)
            debug: Whether debug logging is enabled
        """
        if not self.lua:
            raise RuntimeError("Lua runtime not initialized. Call initialize() first.")
        
        execution_time = self.curr_time()
        self.debug_print(f"Executing Lua script...")
        
        if source_name:
            # Use source name for proper debugging source mapping
            debug_source = f"@{source_name}"
            
            if debugging:
                # For debugging: load the function but defer execution
                load_script = f"""
local func, err = (loadstring or load)({script!r}, {debug_source!r})
if func then
    _PY._debug_main_function = func
    if {str(debug).lower()} then
        print("[MOBDEBUG-LOAD] Script loaded, ready for debugging")
    end
else
    error("Failed to load script: " .. tostring(err))
end
"""
            else:
                # Normal execution with source mapping
                load_script = f"""
local func, err = (loadstring or load)({script!r}, {debug_source!r})
if func then
    coroutine.wrap(func)()
else
    error("Failed to load script: " .. tostring(err))
end
"""
            if debug:
                print(f"[{self.curr_time()}] LUA: Loading script with source: {debug_source} (debugging={debugging})")
            self.lua.execute(load_script)
        else:
            # No source mapping needed (fragments, inline scripts)
            self.lua.execute(f"coroutine.wrap(function () {script} end)()")

    def execute_file(self, filepath: str, debugging: bool = False, debug: bool = False) -> None:
        """
        Execute a Lua file using the main_file_hook
        
        Args:
            filepath: Path to the Lua file to execute
            debugging: Whether this script should be loaded for debugging (deferred execution)
            debug: Whether debug logging is enabled
        """
        if not self.lua:
            raise RuntimeError("Lua runtime not initialized. Call initialize() first.")
        
        self.debug_print(f"Executing file: {filepath}")
        
        # Always use the main_file_hook (which has a default implementation in init.lua)
        try:
            self.PY.main_file_hook(filepath)
        except Exception as e:
            raise RuntimeError(f"main_file_hook failed for {filepath}: {e}")

    def execute_debug_main(self, debug: bool = False) -> None:
        """Execute the main debug function that was previously loaded"""
        if not self.lua:
            raise RuntimeError("Lua runtime not initialized.")
        
        execution_time = self.curr_time()
        if debug:
            print(f"[{execution_time}] Checking for debug main function...")
        
        # First check if debug main function exists
        check_script = """
return _PY._debug_main_function ~= nil
"""
        has_debug_main = self.lua.execute(check_script)
        
        if not has_debug_main:
            if debug:
                print(f"[{execution_time}] No debug main function found, skipping...")
            return
        
        if debug:
            print(f"[{execution_time}] Executing debug main function...")
        
        execute_script = f"""
if _PY._debug_main_function then
    if {str(debug).lower()} then
        print("[MOBDEBUG-EXEC] Executing main function with debug hooks...")
    end
    _PY._debug_main_function()
    _PY._debug_main_function = nil
else
    error("No debug main function loaded")
end
"""
        self.lua.execute(execute_script)

    def get_globals(self) -> Any:
        """Get the Lua globals table"""
        if not self.lua:
            raise RuntimeError("Lua runtime not initialized.")
        return self.lua.globals()

    def is_initialized(self) -> bool:
        """Check if the Lua runtime is initialized"""
        return self.lua is not None

    def get_lua_runtime(self) -> Optional[lupa.LuaRuntime]:
        """Get the Lua runtime instance"""
        return self.lua

    def set_fastapi_app(self, app):
        """Set the FastAPI app reference for internal HTTP calls"""
        self._fastapi_app = app
        # Also store it in the Lua runtime if available
        if self.lua:
            self.lua._api_server_app = app
        
    def _register_exported_functions(self, py_table: Any) -> None:
        """
        Register all exported Python functions to the _PY table
        
        Args:
            py_table: The Lua _PY table to add functions to
        """
        exported_functions = lua_exporter.get_exported_functions()
        for name, func in exported_functions.items():
            # Set the lua runtime on the wrapper for proper conversion
            func._lua_runtime = self.lua
            setattr(py_table, name, func)
            # Note: debug_print may not show output here since debug mode 
            # is set after initialization in some cases
            self.debug_print(f"Exported Python function: _PY.{name}")

    def get_runtime_state(self) -> dict:
        """Get current runtime state information for the isRunning hook"""
        if not self.lua:
            return {
                'active_timers': 0,
                'pending_callbacks': 0, 
                'total_tasks': 0
            }
        
        # Get timer count from Lua
        timer_count_script = """
local count = 0
for timer_id, timer in pairs(_pending_timers) do
    if not timer.cancelled then
        count = count + 1
    end
end
return count
"""
        try:
            active_timers = self.lua.execute(timer_count_script) or 0
        except:
            active_timers = 0
            
        # Get callback count from Lua  
        callback_count_script = """
local count = 0
for callback_id, callback in pairs(_callback_registry) do
    count = count + 1
end
return count
"""
        try:
            pending_callbacks = self.lua.execute(callback_count_script) or 0
        except:
            pending_callbacks = 0
            
        return {
            'active_timers': active_timers,
            'pending_callbacks': pending_callbacks,
            'total_tasks': active_timers + pending_callbacks
        }
    
    def check_is_running_hook(self) -> bool:
        """Check if user-defined _PY.isRunning hook says we should continue running"""
        if not self.lua:
            return True
            
        try:
            # Check if the hook exists and call it with runtime state
            check_script = """
if _PY.isRunning and type(_PY.isRunning) == "function" then
    local state = _PY.getRuntimeState()
    return _PY.isRunning(state)
else
    return true  -- Default to continue running if no hook defined
end
"""
            result = self.lua.execute(check_script)
            return bool(result) if result is not None else True
        except Exception as e:
            self.debug_print(f"Error in isRunning hook: {e}")
            return True  # Default to continue running on error

    def execute_lua_callback(self, callback_id: int, data: Any) -> None:
        """Execute a registered Lua callback with data"""
        if not self.lua:
            raise RuntimeError("Lua runtime not initialized.")
        
        # Handle the case where data is None (e.g., for timers)
        if data is not None:
            # Convert Python data to Lua table using the existing conversion system
            from .luafuns_lib import lua_exporter
            lua_data = lua_exporter._convert_to_lua(data, self.lua)
            
            # Set the data in a Lua global temporarily and then call the callback
            self.lua.globals().temp_callback_data = lua_data
            
            # Execute the callback with data
            execute_script = f"""
if _PY.executeCallback then
    _PY.executeCallback({callback_id}, temp_callback_data)
    temp_callback_data = nil  -- Clean up
else
    error("Callback system not initialized")
end
"""
        else:
            # Execute the callback without data (e.g., for timers)
            execute_script = f"""
if _PY.executeCallback then
    _PY.executeCallback({callback_id})
else
    error("Callback system not initialized")
end
"""
        
        self.lua.execute(execute_script)

    def clear_output_buffer(self) -> None:
        """Clear the output buffer"""
        self.output_buffer.clear()
    
    def get_output_buffer(self) -> str:
        """Get the current output buffer content and clear it"""
        output = "\n".join(self.output_buffer)
        self.output_buffer.clear()
        return output
    
    def set_web_mode(self, web_mode: bool) -> None:
        """Set web mode to control HTML/ANSI conversion"""
        self.web_mode = web_mode
