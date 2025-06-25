"""
PLua Interpreter - Core interpreter class
"""

import sys
import os
import time
import asyncio
from lupa import LuaRuntime
from extensions import get_lua_extensions
from .version import __version__ as PLUA_VERSION

# Import extension modules to register them (side effect: registers all extensions)
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
        self.stable_threshold = 10  # Number of stable checks needed to consider program dead (increased from 3)

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
                # Timer and interval tasks should be counted as active operations
                active_tasks = [
                    task for task in pending_tasks
                    if not task.done() and
                    not task.get_name().startswith('asyncio') and
                    # Exclude the main execution task (Task-1) but keep timer/interval tasks
                    not (task.get_name() == 'Task-1')
                ]

                # Debug: show all task names
                if self.interpreter.debug:
                    print(f"DEBUG: All pending tasks: {[task.get_name() for task in pending_tasks if not task.done()]}", file=sys.stderr)
                    print(f"DEBUG: Active tasks after filtering: {[task.get_name() for task in active_tasks]}", file=sys.stderr)
                    # Show task states
                    for task in pending_tasks:
                        if not task.done():
                            print(f"DEBUG: Task {task.get_name()}: done={task.done()}, cancelled={task.cancelled()}", file=sys.stderr)

                # Also check for active timers
                active_timers = timer_manager.has_active_timers()
                if self.interpreter.debug and active_timers:
                    print(f"DEBUG: Active timers detected: {active_timers}", file=sys.stderr)

                return len(active_tasks) + (1 if active_timers else 0)
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
                print(f"DEBUG: Execution phase: {self.execution_phase}", file=sys.stderr)
                print(f"DEBUG: Active operations: {current_count}", file=sys.stderr)
                print(f"DEBUG: Web server running: {self.web_server_running}", file=sys.stderr)
                print(f"DEBUG: Interactive mode: {self.interactive_mode}", file=sys.stderr)
                print(f"DEBUG: Operation count: {current_count}, Last count: {self.last_operation_count}, Stable checks: {self.stable_checks}", file=sys.stderr)
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
                print(f"DEBUG: Terminating - no operations and {self.stable_checks} stable checks", file=sys.stderr)
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

            if self.interpreter.debug:
                print("DEBUG: Forced cleanup completed", file=sys.stderr)

        except Exception as e:
            if self.interpreter.debug:
                print(f"DEBUG: Error during force cleanup: {e}", file=sys.stderr)


class PLuaInterpreter:
    """Main Lua interpreter class"""
    def __init__(self, debug=False, debugger_enabled=False):
        self.debug = debug
        self.debugger_enabled = debugger_enabled
        self.lua_runtime = LuaRuntime(unpack_returned_tuples=True)
        self.execution_tracker = ExecutionTracker(self)
        self.setup_lua_environment()
        # Print greeting with versions
        print(f"{Colors.BOLD}{Colors.CYAN}PLua{Colors.RESET} {Colors.YELLOW}version: {Colors.WHITE}{PLUA_VERSION}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}Python{Colors.RESET} {Colors.YELLOW}version: {Colors.WHITE}{sys.version.split()[0]}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}Lua{Colors.RESET} {Colors.YELLOW}version: {Colors.WHITE}{self.lua_runtime.globals()._VERSION}{Colors.RESET}")
        sys.stdout.flush()  # Ensure greeting appears before any Lua code runs

    def debug_print(self, message):
        """Print debug message only if debug mode is enabled"""
        if self.debug:
            print(f"DEBUG: {message}", file=sys.stderr)

    def setup_lua_environment(self):
        """Setup Lua environment with custom functions using the extension system"""
        # Get the Lua globals table
        lua_globals = self.lua_runtime.globals()

        # Set up package.path to include our local directories first
        # Calculate path relative to project root (one level up from plua/ directory)
        plua_dir = os.path.dirname(os.path.abspath(__file__))  # This is the plua/ directory
        project_root = os.path.dirname(plua_dir)  # Go up one level to project root
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

        # Get all registered extensions and add them to the Lua environment
        extension_functions = get_lua_extensions(self.lua_runtime)

        # Create the _PY table and add it to Lua globals
        lua_globals['_PY'] = extension_functions

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
            # Operations will be waited for after both fragments and main phases complete
            return True
        except Exception as e:
            print(f"Lua execution error: {e}", file=sys.stderr)
            return False

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
            # Operations will be waited for after both fragments and main phases complete
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

            # Use Lua's require function to load the library and assign it to a global variable
            require_code = f"{library_name} = require('{library_name}')"
            self.lua_runtime.execute(require_code)
            return True
        except Exception as e:
            print(f"Error loading library '{library_name}': {e}", file=sys.stderr)
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
            print("Warning: Some operations may still be running (timeout reached)", file=sys.stderr)
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
                    # Use Lua's load to check if it's an expression that returns a value
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

    async def async_execute_code(self, lua_code):
        """Async wrapper for execute_code that runs in a thread"""
        import threading
        import queue

        result_queue = queue.Queue()

        def execute_in_thread():
            try:
                result = self.execute_code(lua_code)
                result_queue.put(("success", result))
            except Exception as e:
                result_queue.put(("error", str(e)))

        # Lock the timer execution gate before starting
        try:
            from extensions.core import acquire_timer_gate
            await acquire_timer_gate()
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Could not acquire timer gate: {e}", file=sys.stderr)

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
        
        # Release the timer gate to allow pending timer callbacks to run
        try:
            from extensions.core import release_timer_gate
            await release_timer_gate()
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Could not release timer gate: {e}", file=sys.stderr)
        
        return result

    async def async_execute_file(self, filename):
        """Async wrapper for execute_file that runs in a thread"""
        import threading
        import queue

        result_queue = queue.Queue()

        def execute_in_thread():
            try:
                result = self.execute_file(filename)
                result_queue.put(("success", result))
            except Exception as e:
                result_queue.put(("error", str(e)))

        # Lock the timer execution gate before starting
        try:
            from extensions.core import acquire_timer_gate
            await acquire_timer_gate()
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Could not acquire timer gate: {e}", file=sys.stderr)

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
        
        # Release the timer gate to allow pending timer callbacks to run
        try:
            from extensions.core import release_timer_gate
            await release_timer_gate()
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Could not release timer gate: {e}", file=sys.stderr)
        
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
                        result_queue.put(("error", "Failed to execute fragments"))
                        return

                # Then execute main file
                if main_file:
                    # Set the mainfile variable in _PY table
                    self.lua_runtime.globals()['_PY']['mainfile'] = main_file
                    main_result = self.execute_file(main_file)
                    if not main_result:
                        result_queue.put(("error", "Failed to execute main file"))
                        return

                result_queue.put(("success", True))
            except Exception as e:
                result_queue.put(("error", str(e)))

        # Lock the timer execution gate before starting
        try:
            from extensions.core import acquire_timer_gate
            await acquire_timer_gate()
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Could not acquire timer gate: {e}", file=sys.stderr)

        # Start Lua execution in a thread
        thread = threading.Thread(target=execute_in_thread)
        thread.start()

        # Block completely until thread completes - no yielding to event loop
        thread.join()
        
        # Get the result
        status, result = result_queue.get()
        if status == "error":
            raise Exception(result)
        
        # Now that both fragments and main file are completely processed,
        # release the timer gate to allow pending timer callbacks to run
        try:
            from extensions.core import release_timer_gate
            await release_timer_gate()
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Could not release timer gate: {e}", file=sys.stderr)
        
        return result 