"""
PLua Interpreter - Core interpreter class

This version uses a single-process architecture: the FastAPI server is always started and managed by the PLua interpreter itself (embedded). Do NOT run api_server.py directly.
"""

import os
import sys
import uuid
import asyncio
import time
import re
import threading
from lupa import LuaRuntime
from extensions import get_lua_extensions
from .version import __version__ as PLUA_VERSION

# Import extension modules to register them (side effect: registers all
# extensions)
import extensions.core  # noqa: F401
import extensions.network_extensions  # noqa: F401
import extensions.web_server  # noqa: F401


# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'


class ExecutionTracker:
    """Tracks execution phases and determines when to terminate"""

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.execution_phase = "init"  # init, fragments, main, tracking, interactive
        self.fragments_completed = False
        self.main_completed = False
        self.interactive_mode = False
        self.web_server_running = False
        self.last_operation_count = 0
        self.stable_checks = 0  # Number of consecutive stable checks
        # Number of stable checks needed to consider program dead (increased
        # from 3)
        self.stable_threshold = 10

    def start_fragments(self):
        """Mark the start of -e fragment execution"""
        self.execution_phase = "fragments"
        self.fragments_completed = False

    def complete_fragments(self):
        """Mark the completion of -e fragment execution"""
        self.fragments_completed = True
        if not self.main_completed:
            self.execution_phase = "main"
        else:
            self.start_tracking()

    def start_main(self):
        """Mark the start of main file execution"""
        self.execution_phase = "main"

    def complete_main(self):
        """Mark the completion of main file execution"""
        self.main_completed = True
        # Always start tracking when main is completed
        self.start_tracking()

    def start_tracking(self):
        """Start tracking active operations for termination"""
        self.execution_phase = "tracking"
        self.last_operation_count = 0
        self.stable_checks = 0
        if self.interpreter.debug:
            print("DEBUG: Started tracking phase", file=sys.stderr)

    def start_interactive(self):
        """Mark that we're in interactive mode"""
        self.interactive_mode = True
        self.execution_phase = "interactive"

    def set_web_server_running(self, running):
        """Mark web server as running/stopped"""
        self.web_server_running = running

    def get_operation_count(self):
        """Get the total count of active operations"""
        try:
            from extensions.network_extensions import loop_manager
            from extensions.core import timer_manager

            # Get the event loop and check for pending tasks
            loop = loop_manager.get_loop()
            if loop and not loop.is_closed():
                pending_tasks = asyncio.all_tasks(loop)

                # Filter out the main execution task and any system tasks
                # The main execution task is the one that runs all Lua code
                # Timer and interval tasks should be counted as active
                # operations
                active_tasks = [
                    task for task in pending_tasks
                    if not task.done() and
                    not task.get_name().startswith('asyncio') and
                    # Exclude the main execution task (Task-1) but keep
                    # timer/interval tasks
                    not (task.get_name() == 'Task-1')
                ]

                # Debug: show all task names
                if self.interpreter.debug:
                    print(
                        f"DEBUG: All pending tasks: {[task.get_name() for task in pending_tasks if not task.done()]}",
                        file=sys.stderr)
                    print(
                        f"DEBUG: Active tasks after filtering: {[task.get_name() for task in active_tasks]}",
                        file=sys.stderr)
                    # Show task states
                    for task in pending_tasks:
                        if not task.done():
                            print(
                                f"DEBUG: Task {task.get_name()}: done={task.done()}, cancelled={task.cancelled()}",
                                file=sys.stderr)

                # Also check for active timers
                active_timers = timer_manager.has_active_timers()
                if self.interpreter.debug and active_timers:
                    print(
                        f"DEBUG: Active timers detected: {active_timers}",
                        file=sys.stderr)

                # Check for active WebSocket operations
                try:
                    from extensions.websocket_extensions import has_active_websocket_operations
                    active_websockets = has_active_websocket_operations()
                    if self.interpreter.debug and active_websockets:
                        print(
                            f"DEBUG: Active WebSocket operations detected: {active_websockets}",
                            file=sys.stderr)
                except ImportError:
                    active_websockets = False

                return len(active_tasks) + (1 if active_timers else 0) + \
                    (1 if active_websockets else 0)
            return 0

        except Exception:
            return 0

    def should_terminate(self):
        """Determine if the process should terminate"""
        # Never terminate in interactive mode
        if self.interactive_mode:
            return False

        # Don't terminate if web server is running (daemon mode)
        if self.web_server_running:
            return False

        # Only check for active operations if we're in tracking phase
        if self.execution_phase != "tracking":
            return False

        # Get current operation count
        current_count = self.get_operation_count()

        # Debug output
        if self.interpreter.debug:
            try:
                print(
                    f"DEBUG: Execution phase: {self.execution_phase}",
                    file=sys.stderr)
                print(
                    f"DEBUG: Active operations: {current_count}",
                    file=sys.stderr)
                print(
                    f"DEBUG: Web server running: {self.web_server_running}",
                    file=sys.stderr)
                print(
                    f"DEBUG: Interactive mode: {self.interactive_mode}",
                    file=sys.stderr)
                print(
                    f"DEBUG: Operation count: {current_count}, Last count: {self.last_operation_count}, Stable checks: {self.stable_checks}",
                    file=sys.stderr)
            except Exception as e:
                print(f"DEBUG: Error in debug output: {e}", file=sys.stderr)

        # Check if operation count is stable (not changing)
        if current_count == self.last_operation_count:
            self.stable_checks += 1
        else:
            # Operation count changed, reset stability counter
            self.stable_checks = 0

        self.last_operation_count = current_count

        # Terminate if no operations AND we've had stable checks
        if current_count == 0 and self.stable_checks >= self.stable_threshold:
            if self.interpreter.debug:
                print(
                    f"DEBUG: Terminating - no operations and {self.stable_checks} stable checks",
                    file=sys.stderr)
            return True

        return False

    async def wait_for_termination(self, timeout=60):
        """Wait for termination conditions to be met (async version)"""
        if self.interactive_mode:
            return False
        if self.web_server_running:
            return False
        if self.execution_phase != "tracking":
            return False

        # Use longer timeout when debugger is enabled (5 minutes)
        if self.interpreter.debugger_enabled:
            timeout = 300  # 5 minutes
            if self.interpreter.debug:
                print("DEBUG: Using extended timeout (5 minutes) for debugger mode", file=sys.stderr)

        # Check if we should terminate immediately
        if self.should_terminate():
            return True

        try:
            from extensions.network_extensions import loop_manager
            loop_manager.get_loop()  # Just ensure the loop exists
        except Exception:
            # No event loop available, use simple polling
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.should_terminate():
                    return True
                await asyncio.sleep(0.1)
            return False

        # Event loop is available, use it for polling
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.should_terminate():
                return True
            await asyncio.sleep(0.1)
        if self.interpreter.debug:
            print("DEBUG: Termination timeout reached", file=sys.stderr)
        return False

    def force_cleanup(self):
        """Force cleanup of all operations"""
        try:
            from extensions.network_extensions import loop_manager

            # Cancel all pending tasks on the event loop
            loop = loop_manager.get_loop()
            if loop and not loop.is_closed():
                pending_tasks = asyncio.all_tasks(loop)
                for task in pending_tasks:
                    if not task.done():
                        task.cancel()

            # Force cleanup WebSocket connections
            try:
                from extensions.websocket_extensions import websocket_manager
                websocket_manager.force_cleanup()
            except ImportError:
                pass

            if self.interpreter.debug:
                print("DEBUG: Forced cleanup completed", file=sys.stderr)

        except Exception as e:
            if self.interpreter.debug:
                print(
                    f"DEBUG: Error during force cleanup: {e}",
                    file=sys.stderr)


class PLuaInterpreter:
    """Main Lua interpreter class"""

    def __init__(
            self,
            debug=False,
            debugger_enabled=False,
            start_api_server=True,
            api_server_port=8000):
        self.debug = debug
        self.debugger_enabled = debugger_enabled
        self.lua_runtime = LuaRuntime(unpack_returned_tuples=True)
        self.execution_tracker = ExecutionTracker(self)
        self.api_server_port = api_server_port
        self.api_server_host = "127.0.0.1"
        self.instance_id = str(uuid.uuid4())  # Generate unique instance ID
        self.embedded_api_server = None

        self.debug_print(
            f"PLuaInterpreter constructor called with start_api_server={start_api_server}")

        self.setup_lua_environment()

        # Start embedded API server if requested
        if start_api_server:
            self.debug_print("Starting embedded API server")
            self.start_embedded_api_server()
        else:
            self.debug_print("Embedded API server startup skipped")

        # Print greeting with versions
        print(f"{Colors.BOLD}{Colors.CYAN}PLua{Colors.RESET} {Colors.YELLOW}version: {Colors.WHITE}{PLUA_VERSION}{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.GREEN}Python{Colors.RESET} {Colors.YELLOW}version: {Colors.WHITE}{sys.version.split()[0]}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}Lua{Colors.RESET} {Colors.YELLOW}version: {Colors.WHITE}{self.lua_runtime.globals()._VERSION}{Colors.RESET}")
        if self.embedded_api_server and self.embedded_api_server.is_running():
            print(f"{Colors.BOLD}{Colors.BLUE}API Server{Colors.RESET} {Colors.YELLOW}running on: {Colors.WHITE}http://{self.api_server_host}:{self.api_server_port}{Colors.RESET}")
        sys.stdout.flush()

    def debug_print(self, message):
        """Print debug message only if debug mode is enabled"""
        if self.debug:
            print(f"DEBUG: {message}", file=sys.stderr)

    def setup_lua_environment(self):
        """Setup Lua environment with custom functions using the extension system"""
        # Get the Lua globals table
        lua_globals = self.lua_runtime.globals()

        # Set up package.path to include our local directories first
        # Calculate path relative to project root (one level up from plua/
        # directory)
        plua_dir = os.path.dirname(os.path.abspath(
            __file__))  # This is the plua/ directory
        # Go up one level to project root
        project_root = os.path.dirname(plua_dir)
        local_paths = [
            os.path.join(project_root, "lua", "?.lua"),
            os.path.join(project_root, "lua", "?", "init.lua")
        ]

        # Set package.path with local paths first
        existing_path = lua_globals.package.path
        new_path = ";".join(local_paths + [existing_path])
        # Properly escape the path string for Lua execution
        escaped_path = new_path.replace('\\', '\\\\').replace('"', '\\"')
        self.lua_runtime.execute(f'package.path = "{escaped_path}"')
        # lua_globals.package.path = new_path

        self.debug_print(f"Set package.path to: {new_path}")

        # Initialize output capture buffer
        self.output_buffer = []

        # Create a custom print function that captures output
        def captured_print(*args):
            # Convert all arguments to strings and join them
            output = " ".join(str(arg) for arg in args)

            # Check if output contains HTML tags (like <font color='...'>)
            has_html = re.search(r'<[^>]+>', output)

            if has_html:
                # Store the original HTML version in the buffer for web
                # interface
                self.output_buffer.append(output)

                # Convert to ANSI for terminal output
                try:
                    # Get the html2console function from _PY if available
                    lua_globals = self.lua_runtime.globals()
                    if hasattr(
                            lua_globals,
                            '_PY') and hasattr(
                            lua_globals['_PY'],
                            'html2console'):
                        html2console = lua_globals['_PY']['html2console']
                        ansi_output = html2console(output)
                        print(ansi_output, file=sys.stdout)
                        sys.stdout.flush()
                    else:
                        # Fallback: just print the HTML as-is
                        print(output, file=sys.stdout)
                        sys.stdout.flush()
                except Exception:
                    # If conversion fails, print original
                    print(output, file=sys.stdout)
                    sys.stdout.flush()
            else:
                # No HTML, store and print as-is
                self.output_buffer.append(output)
                print(output, file=sys.stdout)
                sys.stdout.flush()

        # Replace the original print function with our captured version
        lua_globals['print'] = captured_print

        # Get all registered extensions and add them to the Lua environment
        extension_functions = get_lua_extensions(self.lua_runtime)

        # Create the _PY table and add it to Lua globals
        lua_globals['_PY'] = extension_functions

        # Store reference to interpreter for _PY functions to access
        lua_globals['_PY_INTERPRETER'] = self

        # Always load plua_init.lua for global Lua setup
        plua_init_path = os.path.join(project_root, "lua", "plua", "plua_init.lua")
        if os.path.exists(plua_init_path):
            with open(plua_init_path, 'r', encoding='utf-8') as f:
                plua_init_code = f.read()
            self.lua_runtime.execute(plua_init_code, self.lua_runtime.globals())
            self.debug_print("Loaded plua_init.lua for global Lua setup")
        else:
            self.debug_print("plua_init.lua not found, skipping global Lua setup")

        # Load Fibaro API automatically
        try:
            fibaro_api_path = os.path.join(
                project_root, "lua", "plua", "fibaro_api.lua")
            if os.path.exists(fibaro_api_path):
                with open(fibaro_api_path, 'r', encoding='utf-8') as f:
                    fibaro_api_code = f.read()
                self.lua_runtime.execute(
                    fibaro_api_code, self.lua_runtime.globals())
                self.debug_print("Loaded Fibaro API automatically")
            else:
                self.debug_print(
                    "Fibaro API file not found, skipping automatic load")
        except Exception as e:
            self.debug_print(f"Failed to load Fibaro API: {e}")

        # Load configuration files (.plua.lua)
        self._load_plua_config()

        # Add timer functions to the default Lua environment for convenience
        # These are also available in _PY for backward compatibility
        try:
            from extensions.core import timer_manager, interval_manager

            # Add timer functions to global scope using the actual functions,
            # not bound methods
            lua_globals['setTimeout'] = lambda func, ms: timer_manager.setTimeout(
                func, ms)
            lua_globals['clearTimeout'] = lambda timer_id: timer_manager.clearTimeout(
                timer_id)
            lua_globals['setInterval'] = lambda func, ms: interval_manager.setInterval(
                func, ms)
            lua_globals['clearInterval'] = lambda interval_id: interval_manager.clearInterval(
                interval_id)

            self.debug_print(
                "Added timer functions to default Lua environment")
        except ImportError:
            # Timer extensions might not be available, that's okay
            self.debug_print("Timer extensions not available")

        # Add some standard Python functions that might be helpful
        # Note: Lua's native print function is already available
        lua_globals['input'] = input

        # Expose PLua version to Lua
        lua_globals['_PLUA_VERSION'] = PLUA_VERSION

        # Initialize mainfile as None (will be set when a file is executed)
        lua_globals['_PY']['mainfile'] = None

        # Set execution tracker in web server extension
        try:
            from extensions.web_server import set_execution_tracker
            set_execution_tracker(self.execution_tracker)
        except Exception:
            pass  # Web server extension might not be available

    def _load_plua_config(self):
        """Load configuration from .plua.lua files in home directory and current working directory"""
        def load_lua_table_from_file(path):
            if not os.path.exists(path):
                return None
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lua_code = f.read()
                # Remove leading comments and whitespace, then a leading
                # 'return'
                code = re.sub(
                    r'^(\s*--.*\n)*\s*return\s+',
                    '',
                    lua_code,
                    flags=re.MULTILINE)
                code = code.strip()
                code = f'({code})'
                table = self.lua_runtime.eval(code)
                if hasattr(table, 'items'):
                    return table
            except Exception as e:
                print(
                    f"Warning: Failed to load config from {path}: {e}",
                    file=sys.stderr)
            return None

        # Load home config
        home_config_path = os.path.join(os.path.expanduser("~"), ".plua.lua")
        home_table = load_lua_table_from_file(home_config_path)
        # Load cwd config
        cwd_config_path = os.path.join(os.getcwd(), ".plua.lua")
        cwd_table = load_lua_table_from_file(cwd_config_path)

        # Merge tables: cwd takes precedence
        merged = {}
        if home_table:
            for k, v in home_table.items():
                merged[k] = v
        if cwd_table:
            for k, v in cwd_table.items():
                merged[k] = v

        # Convert Python dict to Lua table and assign to _PY.pluaconfig
        if merged:
            # Create a Lua table and populate it with the merged data
            lua_table = self.lua_runtime.table()
            for k, v in merged.items():
                lua_table[k] = v
            self.lua_runtime.globals()['_PY']['pluaconfig'] = lua_table
            self.debug_print(
                f"Loaded pluaconfig with {len(merged)} items (cwd takes precedence)")
        else:
            self.lua_runtime.globals(
            )['_PY']['pluaconfig'] = self.lua_runtime.table()
            self.debug_print(
                "No configuration files found, created empty pluaconfig table")

    def execute_file(self, filename):
        """Execute a Lua file"""
        try:
            # Set the mainfile variable in _PY table
            self.lua_runtime.globals()['_PY']['mainfile'] = filename

            with open(filename, 'r', encoding='utf-8') as f:
                lua_code = f.read()
            # Use load() with filename for proper debugger support
            return self.execute_code_with_filename(lua_code, filename)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error reading file '{filename}': {e}", file=sys.stderr)
            return False

    def execute_code(self, lua_code):
        """Execute Lua code string (for -e commands and interactive mode)"""
        try:
            self.lua_runtime.execute(lua_code, self.lua_runtime.globals())
            # Don't wait for operations during execution phases
            # Operations will be waited for after both fragments and main
            # phases complete
            return True
        except Exception as e:
            # Get any captured output before the error
            error_output = self.get_captured_output()
            error_msg = f"Lua execution error: {e}"
            if error_output:
                error_msg = f"{error_output}\n{error_msg}"
            raise Exception(error_msg)

    def execute_code_with_filename(self, lua_code, filename):
        """Execute Lua code with filename for proper debugger support"""
        try:
            # Use Lua's load() function with filename to provide proper source mapping
            # This allows the debugger to know which file the code belongs to
            load_code = f"""
local func, err = load([[\
{self._escape_lua_string(lua_code)}\
]], "{filename}", "t", _G)
if not func then
  error("Failed to load code: " .. tostring(err))
end
func()
"""
            self.lua_runtime.execute(load_code, self.lua_runtime.globals())
            # Don't wait for operations during execution phases
            # Operations will be waited for after both fragments and main
            # phases complete
            return True
        except Exception as e:
            print(f"Lua execution error: {e}", file=sys.stderr)
            return False

    def _escape_lua_string(self, text):
        """Escape a string for use in Lua code"""
        # Only escape backslashes for Lua long string literals
        # Square brackets don't need escaping in [[...]] strings
        return text.replace('\\', '\\\\')

    def load_library(self, library_name):
        """Load a Lua library using require()"""
        try:
            # Special handling for package module - it's already available
            if library_name == "package":
                # Package is already loaded as a global, just verify it exists
                verify_code = "if not package then error('package module not found') end"
                self.lua_runtime.execute(verify_code)
                return True

            # Use Lua's require function to load the library and assign it to a
            # global variable
            require_code = f"{library_name} = require('{library_name}')"
            self.lua_runtime.execute(require_code)
            return True
        except Exception as e:
            print(
                f"Error loading library '{library_name}': {e}",
                file=sys.stderr)
            return False

    def load_libraries(self, libraries):
        """Load multiple Lua libraries"""
        success = True
        for library in libraries:
            if not self.load_library(library):
                success = False
        return success

    def _has_active_operations(self):
        """Check if there are any active operations without waiting"""
        return not self.execution_tracker.should_terminate()

    async def wait_for_active_operations(self):
        """Async version: Wait for active operations to complete using the execution tracker"""
        terminated = await self.execution_tracker.wait_for_termination()
        if not terminated:
            print(
                "Warning: Some operations may still be running (timeout reached)",
                file=sys.stderr)
            self.execution_tracker.force_cleanup()
        if not self.debugger_enabled:
            try:
                from extensions.network_extensions import loop_manager
                loop_manager.shutdown()
            except Exception:
                pass

    def run_interactive(self):
        """Run interactive Lua shell"""
        print("PLua Interactive Shell (Lua 5.4)")
        print("Type 'exit' or 'quit' to exit")
        print("Type 'help' for available functions")
        print("Type '_PY' to see all Python extensions")

        # No registration with API server needed in embedded mode
        print("Web interface available at: http://127.0.0.1:8000/")

        while True:
            try:
                line = input("plua> ").strip()

                if line.lower() in ['exit', 'quit']:
                    break
                elif line.lower() == 'help':
                    print("Available commands:")
                    print("  exit/quit - Exit the shell")
                    print("  help - Show this help")
                    print("  _PY - Show all available Python extensions")
                    print("  _PY.function_name() - Call a Python extension function")
                    continue
                elif line.strip() == '_PY':
                    # Show all available Python extensions
                    print("Available Python extensions (_PY table):")
                    try:
                        self.lua_runtime.execute("_PY.list_extensions()")
                    except Exception as e:
                        print(f"Error listing extensions: {e}")
                    continue
                elif not line:
                    continue

                # Try to execute as expression first (returns value)
                try:
                    # Use Lua's load to check if it's an expression that
                    # returns a value
                    load_code = f"""
local func, err = load("return {line}")
if func then
    local result = func()
    if result ~= nil then
        print(result)
    end
else
    -- Not an expression, try as statement
    local func2, err2 = load("{line}")
    if func2 then
        func2()
    else
        error(err2 or err)
    end
end
"""
                    self.lua_runtime.execute(load_code)
                except Exception:
                    # If the expression approach fails, try direct execution
                    try:
                        self.execute_code(line)
                    except Exception as e2:
                        print(f"Error: {e2}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                print("\nExiting...")
                break

        # No unregister needed in embedded mode

    async def async_execute_code(self, lua_code):
        """Async wrapper that runs Lua code in a thread"""
        def execute_in_thread():
            try:
                result = self.execute_code(lua_code)
                return f"Success: {result}"
            except Exception as e:
                return f"Error: {str(e)}"

        # Lock the timer execution gate before starting fragments only
        try:
            from extensions.core import acquire_timer_gate, set_fragment_executing
            await acquire_timer_gate()
            set_fragment_executing(True)  # Mark that fragment execution is starting
        except Exception as e:
            if self.debug:
                print(
                    f"DEBUG: Could not acquire timer gate: {e}",
                    file=sys.stderr)

        # Run in thread to avoid blocking
        thread = threading.Thread(target=execute_in_thread)
        thread.start()
        thread.join()

        # Release the timer gate after fragments are done
        try:
            from extensions.core import release_timer_gate
            await release_timer_gate()
        except Exception as e:
            if self.debug:
                print(
                    f"DEBUG: Could not release timer gate: {e}",
                    file=sys.stderr)

        return "Async execution completed"

    async def async_execute_file(self, filename):
        """Async wrapper for execute_file that runs in a thread"""
        import threading
        import queue

        result_queue = queue.Queue()

        def execute_in_thread():
            try:
                # Check if _PY.mainHook is registered
                try:
                    main_hook = self.lua_runtime.globals()['_PY']['mainHook']
                    if main_hook:
                        # Call the mainHook function with the filename
                        self.debug_print(
                            f"Using _PY.mainHook for file '{filename}'")
                        hook_code = f"_PY.mainHook('{filename}')"
                        result = self.execute_code(hook_code)
                        result_queue.put(("success", result))
                        return
                except (KeyError, TypeError):
                    # mainHook doesn't exist or is not callable, proceed with
                    # normal execution
                    pass

                # Normal file execution
                result = self.execute_file(filename)
                result_queue.put(("success", result))
            except Exception as e:
                result_queue.put(("error", str(e)))

        # Start Lua execution in a thread
        thread = threading.Thread(target=execute_in_thread)
        thread.start()

        # Wait for completion while allowing event loop to process other tasks
        while thread.is_alive():
            await asyncio.sleep(0.01)  # Yield to event loop every 10ms

        # Get the result
        status, result = result_queue.get()
        if status == "error":
            raise Exception(result)

        return result

    async def async_execute_all(self, fragments_code, main_file):
        """Async wrapper that runs all Lua code (fragments + main) in a single task"""
        import threading
        import queue

        result_queue = queue.Queue()

        def execute_in_thread():
            try:
                # Execute fragments first
                if fragments_code:
                    fragments_result = self.execute_code(fragments_code)
                    if not fragments_result:
                        result_queue.put(
                            ("error", "Failed to execute fragments"))
                        return

                # Then execute main file
                if main_file:
                    # Set the mainfile variable in _PY table
                    self.lua_runtime.globals()['_PY']['mainfile'] = main_file

                    # Check if _PY.mainHook is registered
                    try:
                        main_hook = self.lua_runtime.globals()[
                            '_PY']['mainHook']
                        if main_hook:
                            # Call the mainHook function with the filename
                            self.debug_print(
                                f"Using _PY.mainHook for file '{main_file}'")
                            hook_code = f"_PY.mainHook('{main_file}')"
                            main_result = self.execute_code(hook_code)
                        else:
                            # Normal file execution
                            main_result = self.execute_file(main_file)
                    except (KeyError, TypeError):
                        # mainHook doesn't exist or is not callable, proceed
                        # with normal execution
                        main_result = self.execute_file(main_file)

                    if not main_result:
                        result_queue.put(
                            ("error", "Failed to execute main file"))
                        return

                result_queue.put(("success", True))
            except Exception as e:
                result_queue.put(("error", str(e)))

        # Start Lua execution in a thread
        thread = threading.Thread(target=execute_in_thread)
        thread.start()

        # Lock the timer execution gate before starting fragments only
        try:
            from extensions.core import acquire_timer_gate, set_fragment_executing
            await acquire_timer_gate()
            set_fragment_executing(True)  # Mark that fragment execution is starting
        except Exception as e:
            if self.debug:
                print(
                    f"DEBUG: Could not acquire timer gate: {e}",
                    file=sys.stderr)

        # Wait for completion with very frequent yields to allow socket operations
        while thread.is_alive():
            await asyncio.sleep(0.0001)  # Yield every 0.1ms for maximum responsiveness

        # Get the result
        status, result = result_queue.get()
        if status == "error":
            raise Exception(result)

        # Release the timer gate after fragments are done
        try:
            from extensions.core import release_timer_gate
            await release_timer_gate()
        except Exception as e:
            if self.debug:
                print(
                    f"DEBUG: Could not release timer gate: {e}",
                    file=sys.stderr)

        return result

    def start_embedded_api_server(self):
        """Start the embedded API server"""
        try:
            # Try to free the port before starting the server
            if not free_port(self.api_server_port, self.api_server_host):
                self.debug_print(f"Could not free port {self.api_server_port}, attempting to start server anyway")
            
            from .embedded_api_server import EmbeddedAPIServer

            self.embedded_api_server = EmbeddedAPIServer(
                self,
                host=self.api_server_host,
                port=self.api_server_port,
                debug=self.debug
            )
            self.embedded_api_server.start()

        except ImportError as e:
            self.debug_print(f"FastAPI not available, skipping embedded API server: {e}")
            self.embedded_api_server = None
        except Exception as e:
            self.debug_print(f"Error starting embedded API server: {e}")
            self.embedded_api_server = None

    def get_lua_runtime(self):
        """Get the Lua runtime for API server callbacks"""
        return self.lua_runtime

    def execute_lua_code(self, code):
        """Execute Lua code and return result (for API server callbacks)"""
        try:
            # Set a reasonable timeout for execution
            import threading

            result = None
            error = None

            def execute_with_timeout():
                nonlocal result, error
                try:
                    result = self.lua_runtime.execute(code)
                except Exception as e:
                    error = str(e)

            # Run execution in a thread with timeout
            thread = threading.Thread(target=execute_with_timeout)
            thread.daemon = True
            thread.start()

            # Wait for completion with timeout
            thread.join(timeout=30)  # 30 second timeout

            if thread.is_alive():
                return {"success": False, "result": None, "error": "Execution timed out after 30 seconds"}

            if error:
                return {"success": False, "result": None, "error": error}

            return {"success": True, "result": result, "error": None}

        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def get_captured_output(self):
        """Get captured output and clear the buffer"""
        output = "\n".join(self.output_buffer)
        self.output_buffer.clear()
        return output

    def clear_output_buffer(self):
        """Clear the output buffer"""
        self.output_buffer.clear()

    def __del__(self):
        """Cleanup when interpreter is destroyed"""
        if hasattr(self, 'embedded_api_server') and self.embedded_api_server:
            self.embedded_api_server.stop()

    def is_api_server_running(self):
        """Check if API server is running"""
        return self.embedded_api_server and self.embedded_api_server.is_running()

    def stop_api_server(self):
        """Stop the API server"""
        if self.embedded_api_server:
            self.embedded_api_server.stop()
            self.debug_print("Embedded API server stopped")

    def execute_lua_code_remote(self, code):
        """Execute Lua code remotely (for API server callbacks)"""
        try:
            # Execute the code
            self.lua_runtime.execute(code)

            # Get captured output
            captured_output = self.get_captured_output()

            return {
                "success": True,
                "result": captured_output if captured_output else None,
                "error": None
            }

        except Exception as e:
            # Get any captured output even if there was an error
            captured_output = self.get_captured_output()

            return {
                "success": False,
                "result": captured_output if captured_output else None,
                "error": str(e)
            }

    def setup_command_line_args(self, args):
        """Setup command-line arguments in _PY.args table for Lua access"""
        lua_globals = self.lua_runtime.globals()
        
        # Create _PY.args table
        args_table = self.lua_runtime.table()
        args_table['debug'] = getattr(args, 'debug', False)
        args_table['port'] = getattr(args, 'port', 8000)
        args_table['task'] = getattr(args, 'task', None)
        
        # Add to _PY table
        lua_globals['_PY']['args'] = args_table
        
        self.debug_print(f"Command-line args available in _PY.args: debug={args_table['debug']}, port={args_table['port']}, task={args_table['task']}")

        # Load Fibaro API automatically


# Recursively convert Lua tables to Python dicts/lists
def lua_to_python(obj):
    """Recursively convert Lua tables to Python dicts/lists"""
    # Check if it's a Lua table by checking if it has keys() method and is not
    # a basic type
    if hasattr(
        obj,
        'keys') and callable(
        getattr(
            obj,
            'keys',
            None)) and not isinstance(
                obj,
                (str,
                 int,
                 float,
                 bool,
                 type(None))):
        try:
            keys = list(obj.keys())
            # Heuristic: if all keys are integers, treat as list
            if all(isinstance(k, int) for k in keys):
                # Sort keys for list order
                return [lua_to_python(obj[k]) for k in sorted(keys)]
            else:
                return {k: lua_to_python(obj[k]) for k in keys}
        except (TypeError, AttributeError):
            # If keys() fails, it's not a Lua table
            return obj
    return obj

def free_port(port, host="127.0.0.1"):
    """Free a port by terminating any process using it"""
    try:
        import psutil
        import socket
        
        # First, try to bind to the port to see if it's actually in use
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            test_socket.bind((host, port))
            test_socket.close()
            return True  # Port is free
        except OSError:
            test_socket.close()
            # Port is in use, find and terminate the process
        
        # Find processes using the port - use a more robust approach
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Get connections for this process
                connections = proc.connections()
                for conn in connections:
                    if (conn.status == psutil.CONN_LISTEN and 
                            conn.laddr.port == port and 
                            conn.laddr.ip == host):
                        print(f"Terminating process {proc.info['pid']} ({proc.info['name']}) using port {port}")
                        proc.terminate()
                        proc.wait(timeout=2)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired, psutil.ZombieProcess):
                continue
            except Exception:
                # Skip processes that don't support connections or have other issues
                continue
        return False
    except ImportError:
        print("psutil not available, cannot free port automatically", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error freeing port {port}: {e}", file=sys.stderr)
        return False
