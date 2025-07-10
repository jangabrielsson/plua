import sys
import argparse

from plua import PLuaInterpreter
from plua.version import __version__


# Lazy import of network extensions to avoid startup delay
def get_loop_manager():
    import extensions.network_extensions
    return extensions.network_extensions.loop_manager


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PLua - A Lua interpreter in Python using Lupa library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  plua script.lua                                    # Run a Lua file
  plua -e "print('Hello')"                          # Execute Lua code and exit
  plua -e "x=10" -e "print(x)"                      # Execute multiple code strings and exit
  plua -e "require('debugger')" -e "debugger.start()" script.lua  # Multiple -e before file
  plua -i                                            # Start interactive shell
  plua -e "print('Hello')" -i                       # Execute code then start interactive shell
  plua -l socket script.lua                          # Load socket library before running script
  plua -l socket -l debugger                         # Load multiple libraries in interactive mode
  plua -l socket -e "print(socket.http.request('http://example.com'))"  # Load library and execute code
  plua -e "require('debugger')" -e "debugger.break()" script.lua  # Debugger mode: execute code then file
  plua -d script.lua                                # Run with debug output
  plua -d -e "print('debug mode')" script.lua      # Debug mode with -e commands
  plua --debugger script.lua                        # Run with MobDebug server on default port 8818
  plua --debugger --debugger-port 8820 script.lua   # Run with MobDebug server on port 8820
  plua --debugger -e "require('lua.fibaro')" script.lua  # Run with debugger and fibaro module
  plua --debugger --debugger-port 8820 -e "require('lua.fibaro')" script.lua  # Run with debugger on port 8820 and fibaro module
  plua --fibaro script.lua                          # Load fibaro library and run script
  plua --debugger --fibaro script.lua               # Run with debugger and fibaro library
  plua --fibaro -e "print('Hello')" script.lua      # Load fibaro, execute code, then run script
  plua --port 8080 --fibaro -i                      # Run on custom port 8080 with fibaro and interactive shell
  plua --port 9000 script.lua                       # Run script with API server on port 9000
  plua --host 0.0.0.0 --port 8000 script.lua        # Run script with API server on all interfaces
  plua --task "my-task" script.lua                  # Pass task string to Lua (available in _PY.args.task)
  plua -d --port 8080 --task "debug-task" script.lua # Debug mode with custom port and task
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
    parser.add_argument('--debugger', action='store_true',
                        help='Start MobDebug server for remote debugging on default port 8818')
    parser.add_argument('--debugger-port', type=int, default=8818, metavar='PORT',
                        help='Port for MobDebug server (default: 8818)')
    parser.add_argument('--fibaro', action='store_true',
                        help='Load fibaro.lua library (equivalent to -e "require(\'fibaro\')")')
    parser.add_argument('--port', type=int, default=8000, metavar='PORT',
                        help='Port for the embedded API server (default: 8000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', metavar='HOST',
                        help='Host for the embedded API server (default: 0.0.0.0 - all interfaces)')
    parser.add_argument('--task', type=str, metavar='TASK',
                        help='Task string to pass to Lua (available in _PY.args.task)')
    parser.add_argument('-v', '--version', action='version', version=f'PLua {__version__}')

    args = parser.parse_args()

    # Handle --fibaro flag by inserting require('fibaro') into execute_list at the right position
    if args.fibaro:
        # Initialize execute_list if it doesn't exist
        if args.execute_list is None:
            args.execute_list = []

        # Insert require('fibaro') after any debugger-related -e commands
        insert_position = 0
        for i, arg in enumerate(args.execute_list):
            if 'require(\'debugger\')' in arg or 'mobdebug' in arg:
                insert_position = i + 1

        # Insert the fibaro require at the calculated position
        args.execute_list.insert(insert_position, "require('fibaro')")

    async def async_main(args):
        interpreter = PLuaInterpreter(
            debug=args.debug, 
            debugger_enabled=args.debugger_port if args.debugger else False, 
            silent=args.task is not None, 
            api_server_port=args.port, 
            api_server_host=args.host
        )

        # Pass command-line arguments to Lua in _PY.args table
        interpreter.setup_command_line_args(args)

        # Start MobDebug if requested
        if args.debugger:
            debugger_port = args.debugger_port
            try:
                # Load and start MobDebug
                mobdebug_code = f"""
local mobdebug = require("mobdebug")
mobdebug.start('0.0.0.0', {debugger_port})
print("<font color='blue'>MobDebug server</font> <font color='yellow'>started on:</font> <font color='white'>0.0.0.0:{debugger_port}</font>")
"""
                interpreter.execute_code_direct(mobdebug_code)
            except Exception as e:
                print(f"Failed to start MobDebug: {e}", file=sys.stderr)
                sys.exit(1)

        # Load libraries specified with -l flags
        if args.libraries:
            print(f"Loading libraries: {', '.join(args.libraries)}", file=sys.stderr)
            if not interpreter.load_libraries(args.libraries):
                print("Failed to load one or more libraries", file=sys.stderr)
                sys.exit(1)

        # Handle different execution modes
        if args.file:
            # Execute file (with optional fragments from -e flags)
            if args.execute_list:
                interpreter.debug_print(f"Executing {len(args.execute_list)} code strings then file")
            else:
                interpreter.debug_print("Executing file only")

            # Start fragments phase
            interpreter.execution_tracker.start_fragments()

            if args.execute_list:
                # Execute fragments and main file together to keep timer gate locked
                all_code = "\n".join(args.execute_list)
                interpreter.debug_print("Executing all -e code and file together")
                success = await interpreter.async_execute_all(all_code, args.file)
                if not success:
                    print("Failed to execute code", file=sys.stderr)
                    sys.exit(1)
            else:
                # Execute the file only
                interpreter.debug_print(f"Executing file '{args.file}'")
                success = await interpreter.async_execute_file(args.file)
                if not success:
                    print("Failed to execute Lua code", file=sys.stderr)
                    sys.exit(1)

            # Complete fragments and main phases
            interpreter.execution_tracker.complete_fragments()
            interpreter.execution_tracker.complete_main()

            # Wait for termination
            await interpreter.wait_for_active_operations()
            sys.exit(0)

        elif args.execute_list:
            # Execute code strings (fragments), then exit or go interactive
            if args.interactive:
                print(f"Executing {len(args.execute_list)} code strings, then starting interactive shell", file=sys.stderr)
            else:
                print(f"Executing {len(args.execute_list)} code strings", file=sys.stderr)

            # Start fragments phase
            interpreter.execution_tracker.start_fragments()

            all_code = "\n".join(args.execute_list)
            interpreter.debug_print("Executing all -e code as a single chunk")
            success = await interpreter.async_execute_code(all_code)
            if not success:
                print("Failed to execute -e code chunk", file=sys.stderr)
                sys.exit(1)

            # Complete fragments phase
            interpreter.execution_tracker.complete_fragments()

            if args.interactive:
                # Start interactive shell after executing the code
                interpreter.execution_tracker.start_interactive()
                interpreter.run_interactive()
            else:
                # For -e only (no file, no interactive), start tracking phase and wait for termination
                interpreter.execution_tracker.start_tracking()
                await interpreter.wait_for_active_operations()
                sys.exit(0)

        elif args.interactive:
            # Start interactive shell
            interpreter.execution_tracker.start_interactive()
            interpreter.run_interactive()

        else:
            # No arguments provided: start interactive shell
            interpreter.execution_tracker.start_interactive()
            interpreter.run_interactive()

    try:
        get_loop_manager().run_main(async_main(args))
    except KeyboardInterrupt:
        print("\n[PLua] Received Ctrl-C (SIGINT), shutting down gracefully...")
        sys.exit(0)


if __name__ == "__main__":
    main()
