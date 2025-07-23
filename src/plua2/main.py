"""
Main entry point for plua2 application
"""

import asyncio
import argparse
import sys
import os
from typing import Optional
import lupa

from .runtime import LuaAsyncRuntime
from .repl import run_repl


def show_greeting() -> None:
    """Display greeting with plua2 and Lua versions"""
    from . import __version__

    # Get Lua version efficiently
    try:
        lua = lupa.LuaRuntime()
        lua_version = lua.eval('_VERSION')
    except Exception:
        lua_version = "Lua (version unknown)"

    print(f"Plua2 v{__version__} with {lua_version}")


async def run_script(
    runtime=None,
    script_fragments: list = None,
    main_script: str = None,
    main_file: str = None,
    duration: Optional[int] = None,
) -> None:
    """
    Run Lua script fragments and main script with the async runtime, optionally with REST API server
    """
    # Name the main task
    current_task = asyncio.current_task()
    if current_task:
        current_task.set_name("main_runtime")

    if runtime is None:
        from .runtime import LuaAsyncRuntime
        runtime = LuaAsyncRuntime()
    api_task = None
    api_server = None

    api_config = runtime.config.get('api_config')
    debug = runtime.config.get('debug', False)
    debugger_config = runtime.config.get('debugger_config')
    source_name = runtime.config.get('source_name')
    if api_config:
        from .api_server import PlUA2APIServer
        print(f"API server on {api_config['host']}:{api_config['port']}")
        api_server = PlUA2APIServer(runtime, api_config['host'], api_config['port'])

        def broadcast_view_hook(qa_id, component_name, property_name, data_json):
            if api_server:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(api_server.broadcast_view_update(qa_id, component_name, property_name, data_json))
                except Exception as e:
                    print(f"Error creating view broadcast task for QA {qa_id}: {e}")

        runtime.interpreter.set_broadcast_view_update_hook(broadcast_view_hook)
        api_task = asyncio.create_task(api_server.start_server(), name="api_server")

    try:
        await runtime.start(
            script_fragments=script_fragments,
            main_script=main_script,
            main_file=main_file,
            duration=duration,
            debugger_config=debugger_config,
            source_name=source_name,
            debug=debug,
            api_server=api_server
        )
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
    except Exception as e:
        print(f"Runtime error: {e}")
    finally:
        if api_task and not api_task.done():
            api_task.cancel()
            try:
                await asyncio.gather(api_task, return_exceptions=True)
            except Exception:
                pass


def main() -> None:
    """Main entry point for the plua2 command line tool"""

    parser = argparse.ArgumentParser(
        description="plua2 - Python-Lua async runtime with timer support",
        epilog="Examples:\n"
               "  plua2 script.lua                    # Run script.lua with API server\n"
               "  plua2 --noapi script.lua            # Run script.lua without API server\n"
               "  plua2 --api-port 9000 script.lua    # Run with API on port 9000\n"
               "  plua2 --duration 10 script.lua      # Run for 10 seconds\n"
               "  plua2 -e 'print(\"hello\")'           # Run inline script\n"
               "  plua2 -e 'x=1' -e 'print(x)'        # Multiple -e fragments\n"
               "  plua2 -e 'print(\"start\")' script.lua # Combine -e and file\n"
               "  plua2 --fibaro script.lua           # Run with Fibaro API support\n"
               "  plua2 --debugger script.lua         # Run with MobDebug\n"
               "  plua2 --debugger --debug script.lua # Run with verbose debug logging\n"
               "  plua2 --cleanup-port                # Clean up stuck API port\n"
               "  plua2 --debugger --debugger-host 192.168.1.100 script.lua",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-e",
        help="Execute inline Lua code (like lua -e). Can be used multiple times.",
        action="append",
        type=str,
        dest="script_fragments"
    )

    parser.add_argument(
        "--duration", "-d",
        help="Duration in seconds to run (default: run forever)",
        type=int,
        default=None
    )

    parser.add_argument(
        "--debugger",
        help="Load and start MobDebug debugger before executing script",
        action="store_true"
    )

    parser.add_argument(
        "--debugger-host",
        help="Host for MobDebug connection (default: localhost)",
        type=str,
        default="localhost"
    )

    parser.add_argument(
        "--debugger-port",
        help="Port for MobDebug connection (default: 8172)",
        type=int,
        default=8172
    )

    parser.add_argument(
        "--debug",
        help="Enable debug logging for MobDebug and plua2 internals",
        action="store_true"
    )

    parser.add_argument(
        "--fibaro",
        help="Load Fibaro API support (equivalent to -e \"require('fibaro')\")",
        action="store_true"
    )

    parser.add_argument(
        "--version", "-v",
        help="Show version and exit",
        action="store_true"
    )

    parser.add_argument(
        "lua_file",
        help="Lua file to execute",
        nargs="?",  # Optional positional argument
        type=str
    )

    parser.add_argument(
        "--noapi",
        help="Disable the REST API server (API is enabled by default on port 8888)",
        action="store_true"
    )

    parser.add_argument(
        "--api-port",
        help="Port for REST API server (default: 8888)",
        type=int,
        default=8888
    )

    parser.add_argument(
        "--api-host",
        help="Host for REST API server (default: 0.0.0.0)",
        type=str,
        default="0.0.0.0"
    )

    parser.add_argument(
        "--cleanup-port",
        help="Clean up the API port and exit (useful when port is stuck)",
        action="store_true"
    )

    args = parser.parse_args()

    # Show greeting with version information first
    show_greeting()

    if args.version:
        sys.exit(0)

    # Handle port cleanup if requested
    if args.cleanup_port:
        from .api_server import cleanup_port_cli
        # Use the API port for cleanup
        cleanup_port = args.api_port
        success = cleanup_port_cli(cleanup_port, args.api_host)
        print(f"Port cleanup completed for {args.api_host}:{cleanup_port}")
        sys.exit(0 if success else 1)

    # Prepare debugger config if requested
    debugger_config = None
    if args.debugger:
        debugger_config = {
            'host': args.debugger_host,
            'port': args.debugger_port,
            'debug': args.debug
        }
    # Collect all config into a single dictionary
    config = {
        'debugger_config': debugger_config,
        'debug': args.debug,
        'api_config': None if args.noapi else {'host': args.api_host, 'port': args.api_port},
        'source_name': None,  # source_name will be set based on args.lua_file
        # Add more CLI flags here as needed
    }
    runtime = LuaAsyncRuntime(config=config)
    # Determine which script to run
    script_fragments = args.script_fragments or []

    # Add Fibaro support if requested
    if args.fibaro:
        script_fragments = ["require('fibaro')"] + script_fragments

    main_script = None
    main_file = None
    source_file_name = None  # Track the file name for debugging

    # Check if Lua file exists if provided
    if args.lua_file:
        if not os.path.exists(args.lua_file):
            print(f"Error: File '{args.lua_file}' not found")
            sys.exit(1)
        # Store the file path instead of reading content
        main_file = args.lua_file
        # Use the file name for debugging (preserve relative path for VS Code)
        source_file_name = args.lua_file
        config['source_name'] = source_file_name
    if not script_fragments and not main_script and not main_file:
        try:
            asyncio.run(run_repl(runtime=runtime))
        except KeyboardInterrupt:
            print("\nGoodbye!")
        sys.exit(0)
    # Otherwise, run script (with or without API)
    try:
        asyncio.run(run_script(runtime=runtime, script_fragments=script_fragments, main_script=main_script, main_file=main_file, duration=args.duration))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except asyncio.CancelledError:
        # Handle cancellation during shutdown (e.g., from _PY.isRunning termination)
        # This is expected behavior, exit cleanly without showing error
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
