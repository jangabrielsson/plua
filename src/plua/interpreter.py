"""
Lua interpreter class for managing Lua runtime and script execution
"""

import lupa
from datetime import datetime
from typing import Any, Callable, Optional
# from . import __version__
from .syncsocket import SynchronousTCPManager
from .luafuns_lib import lua_exporter
from .luafuns_lib import _python_to_lua_table
from . import html_extensions  # Import to register HTML functions  # noqa: F401
from . import network  # Import to register network functions  # noqa: F401


class LuaInterpreter:
    """
    A class that manages the Lua runtime environment and script execution
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.lua: Optional[lupa.LuaRuntime] = None
        self._debug = self.config.get('debug', False)
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
        # start_time = self.curr_time()
        self.debug_print("Starting Lua runtime...")

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
            # add runtime config if available
            if hasattr(self, 'config'):
                config_data.runtime_config = _python_to_lua_table(self.lua, self.config)
            py_table.config = config_data
        except Exception as e:
            print(f"Warning: Could not initialize _PY.config: {e}")
            py_table.config = {}

        # Execute init script after all functions are registered
        # Use loadfile for proper source mapping and debugging support
        # Simplified path resolution for Nuitka and development
        import os
        import sys
        
        if getattr(sys, 'frozen', False):
            # Nuitka onefile/onedir: look for lua/init.lua next to the executable or in cwd
            executable_dir = os.path.dirname(sys.executable)
            possible_paths = [
                os.path.join(executable_dir, 'lua', 'init.lua'),
                os.path.join(os.getcwd(), 'lua', 'init.lua'),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    init_script_path = path
                    break
            else:
                # Not found, use the first and let it fail
                init_script_path = possible_paths[0]
                if self.debug:
                    print(f"[DEBUG] Tried paths: {possible_paths}", file=sys.stderr)
                    print(f"[DEBUG] Executable location: {sys.executable}", file=sys.stderr)
                    print(f"[DEBUG] Current working directory: {os.getcwd()}", file=sys.stderr)
        else:
            # Regular pip install: lua directory is a separate package in site-packages
            # The wheel installs lua as a top-level package alongside plua
            package_dir = os.path.dirname(__file__)  # .../site-packages/plua or .../local-packages/plua
            site_packages = os.path.dirname(package_dir)  # .../site-packages or .../local-packages
            
            # For Windows user installs, we need to check both user and system site-packages
            import site
            user_site = getattr(site, 'USER_SITE', None)
            system_sites = getattr(site, 'getsitepackages', lambda: [])()
            
            possible_paths = [
                # Standard pip install: lua as top-level package in same site-packages as plua
                os.path.join(site_packages, 'lua', 'init.lua'),
                # User site-packages (Windows user install)
                os.path.join(user_site, 'lua', 'init.lua') if user_site else None,
                # System site-packages fallbacks
                *[os.path.join(sp, 'lua', 'init.lua') for sp in system_sites if sp],
                # Alternative: inside the plua package (just in case)
                os.path.join(package_dir, 'lua', 'init.lua'),
                # Legacy: sibling to plua package (old location)
                os.path.join(os.path.dirname(package_dir), 'lua', 'init.lua'),
                # Development: relative to this file  
                os.path.join(package_dir, '..', 'lua', 'init.lua'),
                # Additional Windows paths
                os.path.join(package_dir, '..', '..', 'lua', 'init.lua'),
            ]
            
            # Filter out None values
            possible_paths = [p for p in possible_paths if p is not None]
            
            init_script_path = None
            for path in possible_paths:
                normalized_path = os.path.normpath(path)
                if os.path.exists(normalized_path):
                    init_script_path = normalized_path
                    break
            
            if init_script_path is None:
                # Not found, use the first and let it fail with better error message
                init_script_path = possible_paths[0]

        # Verify the file exists
        if not os.path.exists(init_script_path):
            # Show debug output when init.lua is not found to help troubleshoot
            print("\n" + "="*60, file=sys.stderr)
            print("PLUA ERROR - init.lua NOT FOUND", file=sys.stderr)
            print("="*60, file=sys.stderr)
            print(f"[ERROR] init.lua not found at: {init_script_path}", file=sys.stderr)
            print(f"[DEBUG] sys.executable: {sys.executable}", file=sys.stderr)
            print(f"[DEBUG] sys.frozen: {getattr(sys, 'frozen', False)}", file=sys.stderr)
            print(f"[DEBUG] Platform: {sys.platform}", file=sys.stderr)
            print(f"[DEBUG] Python version: {sys.version}", file=sys.stderr)
            print(f"[DEBUG] Package file location: {__file__}", file=sys.stderr)
            print(f"[DEBUG] Current working directory: {os.getcwd()}", file=sys.stderr)
            
            if not getattr(sys, 'frozen', False):
                # Show detailed path information for pip installs
                package_dir = os.path.dirname(__file__)
                site_packages = os.path.dirname(package_dir)
                import site
                user_site = getattr(site, 'USER_SITE', None)
                system_sites = getattr(site, 'getsitepackages', lambda: [])()
                
                print(f"[DEBUG] User site-packages: {user_site}", file=sys.stderr)
                print(f"[DEBUG] System site-packages: {system_sites}", file=sys.stderr)
                print(f"[DEBUG] Current package location: {package_dir}", file=sys.stderr)
                print(f"[DEBUG] Inferred site-packages: {site_packages}", file=sys.stderr)
                print(f"[DEBUG] All attempted paths:", file=sys.stderr)
                for i, path in enumerate(possible_paths):
                    normalized_path = os.path.normpath(path)
                    exists = os.path.exists(normalized_path)
                    selected = "← SELECTED" if normalized_path == init_script_path else ""
                    print(f"  {i+1}. {normalized_path} {'✓' if exists else '✗'} {selected}", file=sys.stderr)
            
            # Try to list contents of key directories
            try:
                package_dir = os.path.dirname(__file__)
                site_packages = os.path.dirname(package_dir)
                print(f"[DEBUG] Package directory ({package_dir}) contents:", file=sys.stderr)
                package_contents = os.listdir(package_dir)
                for item in sorted(package_contents):
                    item_path = os.path.join(package_dir, item)
                    item_type = "DIR" if os.path.isdir(item_path) else "FILE"
                    print(f"  - {item} ({item_type})", file=sys.stderr)
                print(f"[DEBUG] Site-packages directory ({site_packages}) contents:", file=sys.stderr)
                site_contents = os.listdir(site_packages)
                lua_related = [d for d in site_contents if 'lua' in d.lower() or d.startswith('plua')]
                for item in sorted(lua_related):
                    item_path = os.path.join(site_packages, item)
                    item_type = "DIR" if os.path.isdir(item_path) else "FILE"
                    print(f"  - {item} ({item_type})", file=sys.stderr)
                if not lua_related:
                    print(f"  - No lua-related directories found", file=sys.stderr)
                    print(f"  - Total directories: {len([d for d in site_contents if os.path.isdir(os.path.join(site_packages, d))])}", file=sys.stderr)
                    # Show first 10 items to get a sense of the structure
                    print(f"  - Sample contents: {sorted(site_contents)[:10]}", file=sys.stderr)
            except Exception as e:
                print(f"[DEBUG] Could not list directories: {e}", file=sys.stderr)
                
            print("="*60, file=sys.stderr)
            # Flush stderr to ensure debug output is visible before exception
            sys.stderr.flush()
            raise FileNotFoundError(f"init.lua not found at: {init_script_path}")

        py_table.config.init_script_path = init_script_path  # export path to Lua

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

        self.debug_print("Lua runtime initialized")

    def execute_script(self, script: str, source_name: str = None, debugging: bool = False, debug: bool = False) -> None:
        """
        Execute a Lua script string

        Args:
            script: The Lua script to execute
            source_name: Optional source name for debugging
            debugging: Whether this script should be loaded for debugging (deferred execution)
            debug: Whether debug logging is enabled
        """
        if not self.lua:
            raise RuntimeError("Lua runtime not initialized. Call initialize() first.")

        if source_name:
            # Use source mapping for better debugging
            debug_source = source_name
            if debug:
                print(f"[{self.curr_time()}] LUA: Loading script with source: {debug_source}")
            self.lua.execute(f"coroutine.wrap(function () {script} end)()")
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
for timer_id, timer in pairs(_PY._pending_timers) do
    if not timer.cancelled then
        count = count + 1
    end
end
return count
"""
        try:
            active_timers = self.lua.execute(timer_count_script) or 0
        except Exception:
            active_timers = 0

        # Get callback count from Lua
        callback_count_script = """
local count = 0
for callback_id, callback in pairs(_PY._callback_registry) do
    count = count + 1
end
return count
"""
        try:
            pending_callbacks = self.lua.execute(callback_count_script) or 0
        except Exception:
            pending_callbacks = 0

        res = {
            'active_timers': active_timers,
            'pending_callbacks': pending_callbacks,
            'total_tasks': active_timers + pending_callbacks
        }

        res = _python_to_lua_table(self.lua, res)  # Convert to Lua table format
        return res


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

        executeCallback = self.lua.globals()._PY.executeCallback
        if not executeCallback:
            raise RuntimeError("Callback system not initialized")
      
        # Handle the case where data is None (e.g., for timers)
        if data is not None:
            # Convert Python data to Lua table using the existing conversion system
            from .luafuns_lib import lua_exporter
            lua_data = lua_exporter._convert_to_lua(data, self.lua)
            executeCallback(callback_id, lua_data)
        else:
            executeCallback(callback_id)

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
