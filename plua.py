#!/usr/bin/env python3
"""
PLua - A Lua interpreter in Python using Lupa library
Supports Lua 5.4 environment with custom Python-extended functions for timer management.
"""

import sys
import os
import argparse
import time
from lupa import LuaRuntime
from extensions import get_lua_extensions

# Import extension modules to register them (side effect: registers all extensions)
import extensions.core  # noqa: F401
import extensions.network_extensions  # noqa: F401


class PLuaInterpreter:
    """Main Lua interpreter class"""
    def __init__(self, debug=False):
        self.debug = debug
        self.lua_runtime = LuaRuntime(unpack_returned_tuples=True)
        self.setup_lua_environment()

    def debug_print(self, message):
        """Print debug message only if debug mode is enabled"""
        if self.debug:
            print(f"DEBUG: {message}", file=sys.stderr)

    def setup_lua_environment(self):
        """Setup Lua environment with custom functions using the extension system"""
        # Get the Lua globals table
        lua_globals = self.lua_runtime.globals()

        # Set up package.path to include our local directories first
        plua_dir = os.path.dirname(os.path.abspath(__file__))
        local_paths = [
            os.path.join(plua_dir, "lua", "?.lua"),
            os.path.join(plua_dir, "lua", "?", "init.lua")
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

    def execute_file(self, filename):
        """Execute a Lua file"""
        try:
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
            # Only wait for active operations if there are any
            if self._has_active_operations():
                self.wait_for_active_operations()
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
            # Only wait for active operations if there are any
            if self._has_active_operations():
                self.wait_for_active_operations()
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
        try:
            from extensions.core import timer_manager
            from extensions.network_extensions import network_manager

            has_timers = timer_manager.has_active_timers()
            has_network = network_manager.has_active_operations()

            return has_timers or has_network
        except Exception:
            # If there's any error checking operations, assume there are none
            return False

    def wait_for_active_operations(self):
        """Wait for active network operations and timers to complete"""
        from extensions.core import timer_manager
        from extensions.network_extensions import network_manager

        # Wait for operations to complete (with timeout)
        timeout = 60  # 60 second timeout for complex operations
        start_time = time.time()

        while time.time() - start_time < timeout:
            has_timers = timer_manager.has_active_timers()
            has_network = network_manager.has_active_operations()

            if not has_timers and not has_network:
                # No active operations, safe to exit
                break

            # Wait a bit before checking again
            time.sleep(0.1)

        # If we hit timeout, print a warning
        if time.time() - start_time >= timeout:
            print("Warning: Some operations may still be running (timeout reached)", file=sys.stderr)
            print(f"Active timers: {timer_manager.has_active_timers()}", file=sys.stderr)
            print(f"Active network operations: {network_manager.has_active_operations()}", file=sys.stderr)
            # Force cleanup to prevent hanging
            network_manager.force_cleanup()
            print("Forced cleanup of network operations", file=sys.stderr)

        # Always cleanup network manager on exit
        try:
            from extensions.network_extensions import loop_manager
            loop_manager.shutdown()
        except Exception:
            pass  # Ignore cleanup errors

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
                elif not line:
                    continue

                self.execute_code(line)

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                print("\nExiting...")
                break


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PLua - A Lua interpreter in Python using Lupa library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  plua script.lua                                    # Run a Lua file
  plua -e "print('Hello')"                          # Execute Lua code
  plua -e "x=10" -e "print(x)"                      # Execute multiple code strings
  plua -e "require('debugger')" -e "debugger.start()" script.lua  # Multiple -e before file
  plua -i                                            # Start interactive shell
  plua -l socket script.lua                          # Load socket library before running script
  plua -l socket -l debugger                         # Load multiple libraries in interactive mode
  plua -l socket -e "print(socket.http.request('http://example.com'))"  # Load library and execute code
  plua -e "require('debugger')" -e "debugger.break()" script.lua  # Debugger mode: execute code then file
  plua -d script.lua                                # Run with debug output
  plua -d -e "print('debug mode')" script.lua      # Debug mode with -e commands
  """
    )

    parser.add_argument('file', nargs='?', help='Lua file to execute')
    parser.add_argument('-e', '--execute', action='append', dest='execute_list',
                        help='Execute Lua code string (can be used multiple times)')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Start interactive shell')
    parser.add_argument('-l', '--library', action='append', dest='libraries',
                        help='Load library before executing script (can be used multiple times)')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug output')
    parser.add_argument('-v', '--version', action='version', version='PLua 1.0.0')

    args = parser.parse_args()

    interpreter = PLuaInterpreter(debug=args.debug)

    # Load libraries specified with -l flags
    if args.libraries:
        print(f"Loading libraries: {', '.join(args.libraries)}", file=sys.stderr)
        if not interpreter.load_libraries(args.libraries):
            print("Failed to load one or more libraries", file=sys.stderr)
            sys.exit(1)

    # Handle different execution modes
    if args.execute_list and args.file:
        # Multiple -e flags with file: execute all code strings first, then the file
        interpreter.debug_print(f"Executing {len(args.execute_list)} code strings then file")

        # Execute all -e code strings first (these don't have filenames)
        all_code = "\n".join(args.execute_list)
        interpreter.debug_print("Executing all -e code as a single chunk")
        success = interpreter.execute_code(all_code)
        if not success:
            print("Failed to execute -e code chunk", file=sys.stderr)
            sys.exit(1)

        # Then execute the file with proper filename mapping
        interpreter.debug_print(f"Executing file '{args.file}' with filename mapping")
        success = interpreter.execute_file(args.file)
        if not success:
            print("Failed to execute file", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    elif args.execute_list:
        # Execute multiple code strings from -e flags
        print(f"Executing {len(args.execute_list)} code strings", file=sys.stderr)
        # Concatenate all code strings into one chunk
        all_code = "\n".join(args.execute_list)
        interpreter.debug_print("Executing all -e code as a single chunk")
        success = interpreter.execute_code(all_code)
        if not success:
            print("Failed to execute -e code chunk", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    elif args.interactive:
        # Start interactive shell
        interpreter.run_interactive()

    elif args.file:
        # Execute Lua file
        success = interpreter.execute_file(args.file)
        sys.exit(0 if success else 1)

    else:
        # No arguments provided, start interactive shell
        interpreter.run_interactive()


if __name__ == "__main__":
    main()
