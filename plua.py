#!/usr/bin/env python3
"""
PLua - A Lua interpreter in Python using Lupa library
Supports Lua 5.4 environment with custom Python-extended functions for timer management.
"""

import sys
import argparse
import asyncio
from plua import PLuaInterpreter
import extensions.network_extensions

loop_manager = extensions.network_extensions.loop_manager


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
  plua --debugger script.lua                        # Run with MobDebug server on default port 8818
  plua --debugger --debugger-port 8820 script.lua   # Run with MobDebug server on port 8820
  plua --debugger -e "require('lua.fibaro')" script.lua  # Run with debugger and fibaro module
  plua --debugger --debugger-port 8820 -e "require('lua.fibaro')" script.lua  # Run with debugger on port 8820 and fibaro module
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
    parser.add_argument('-v', '--version', action='version', version='PLua 1.0.0')

    args = parser.parse_args()

    async def async_main(args):
        interpreter = PLuaInterpreter(debug=args.debug, debugger_enabled=args.debugger_port if args.debugger else False)

        # Start MobDebug if requested
        if args.debugger:
            debugger_port = args.debugger_port
            try:
                # Load and start MobDebug
                mobdebug_code = f"""
local mobdebug = require("mobdebug")
mobdebug.start('0.0.0.0', {debugger_port})
print("MobDebug server started on 0.0.0.0:{debugger_port}")
"""
                interpreter.execute_code(mobdebug_code)
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
        if args.execute_list and args.file:
            # Multiple -e flags with file: execute all code strings first, then the file
            interpreter.debug_print(f"Executing {len(args.execute_list)} code strings then file")

            # Start fragments phase
            interpreter.execution_tracker.start_fragments()

            # Execute all -e code strings first (these don't have filenames)
            all_code = "\n".join(args.execute_list)
            interpreter.debug_print("Executing all -e code as a single chunk")

            # Complete fragments phase
            interpreter.execution_tracker.complete_fragments()

            # Start main phase
            interpreter.execution_tracker.start_main()

            # Execute all Lua code (fragments + main) in a single task
            interpreter.debug_print(f"Executing all Lua code (fragments + main file '{args.file}')")
            success = await interpreter.async_execute_all(all_code, args.file)
            if not success:
                print("Failed to execute Lua code", file=sys.stderr)
                sys.exit(1)

            # Complete main phase and start tracking
            interpreter.execution_tracker.complete_main()

            # Wait for termination
            await interpreter.wait_for_active_operations()
            sys.exit(0)

        elif args.execute_list and args.interactive:
            # Execute code strings then start interactive shell
            print(f"Executing {len(args.execute_list)} code strings, then starting interactive shell", file=sys.stderr)

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

            # Start interactive shell after executing the code
            interpreter.execution_tracker.start_interactive()
            interpreter.run_interactive()

        elif args.execute_list:
            # Execute multiple code strings from -e flags
            print(f"Executing {len(args.execute_list)} code strings", file=sys.stderr)

            # Start fragments phase
            interpreter.execution_tracker.start_fragments()

            # Concatenate all code strings into one chunk
            all_code = "\n".join(args.execute_list)
            interpreter.debug_print("Executing all -e code as a single chunk")
            success = await interpreter.async_execute_code(all_code)
            if not success:
                print("Failed to execute -e code chunk", file=sys.stderr)
                sys.exit(1)

            # Complete fragments phase and start tracking
            interpreter.execution_tracker.complete_fragments()

            # Wait for termination
            await interpreter.wait_for_active_operations()
            sys.exit(0)

        elif args.interactive:
            # Start interactive shell
            interpreter.execution_tracker.start_interactive()
            interpreter.run_interactive()

        elif args.file:
            # Execute Lua file
            interpreter.execution_tracker.start_main()
            success = await interpreter.async_execute_file(args.file)
            if not success:
                sys.exit(1)

            # Allow event loop to process pending tasks (like setTimeout with 0 delay)
            await asyncio.sleep(0.1)

            # Complete main phase and start tracking
            interpreter.execution_tracker.complete_main()

            # Wait for termination
            await interpreter.wait_for_active_operations()
            sys.exit(0)

        else:
            # No arguments provided, start interactive shell
            interpreter.execution_tracker.start_interactive()
            interpreter.run_interactive()

    loop_manager.run_main(async_main(args))


if __name__ == "__main__":
    main()
