"""
Main entry point for plua application
"""

import asyncio
import argparse
import sys
import os
import signal
import atexit
from typing import Optional
import lupa

from .runtime import LuaAsyncRuntime
from .repl import run_repl


def cleanup_on_exit():
    """Cleanup function called on process termination"""
    try:
        from .luafuns_lib import close_all_quickapp_windows
        print("\nCleaning up on exit...")
        close_all_quickapp_windows()
    except Exception as e:
        # Don't print errors during shutdown unless debugging
        pass


def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down...")
        cleanup_on_exit()
        sys.exit(0)
    
    # Register signal handlers for common termination signals
    signals_to_handle = []
    
    # SIGTERM - standard termination signal (used by VS Code, Docker, etc.)
    if hasattr(signal, 'SIGTERM'):
        signals_to_handle.append(signal.SIGTERM)
    
    # SIGINT - interrupt signal (Ctrl+C) - though we also handle KeyboardInterrupt
    if hasattr(signal, 'SIGINT'):
        signals_to_handle.append(signal.SIGINT)
    
    # SIGHUP - hangup signal (terminal disconnection)
    if hasattr(signal, 'SIGHUP'):
        signals_to_handle.append(signal.SIGHUP)
    
    # Register handlers for available signals
    for sig in signals_to_handle:
        try:
            signal.signal(sig, signal_handler)
        except (OSError, ValueError):
            # Some signals may not be available on all platforms
            pass
    
    # Also register atexit handler as final fallback
    atexit.register(cleanup_on_exit)


def show_greeting() -> None:
    """Display greeting with plua and Lua versions"""
    from . import __version__

    # Get Lua version efficiently
    try:
        lua = lupa.LuaRuntime()
        lua_version = lua.eval('_VERSION')
    except Exception:
        lua_version = "Lua (version unknown)"

    print(f"Plua v{__version__} with {lua_version}")


async def run_interactive(
    runtime=None,
    script_fragments: list = None,
    main_script: str = None,
    main_file: str = None,
    duration: Optional[int] = None,
) -> None:
    """
    Run script content first (if any), then enter interactive REPL
    """
    # Name the main task
    current_task = asyncio.current_task()
    if current_task:
        current_task.set_name("interactive_runtime")

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
        print(f"WebUI on http://127.0.0.1:{api_config['port']}/web")
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
        # First, execute any script content if provided
        has_script_content = bool(script_fragments or main_script or main_file)
        if has_script_content:
            print("Executing script content...")
            await runtime.start_script_only(
                script_fragments=script_fragments,
                main_script=main_script,
                main_file=main_file,
                debugger_config=debugger_config,
                source_name=source_name,
                debug=debug,
                api_server=api_server
            )
            print("Script execution completed. Entering interactive mode...")
        else:
            # Initialize runtime for REPL only
            await runtime.initialize(
                debugger_config=debugger_config,
                debug=debug,
                api_server=api_server
            )

        # Now enter interactive REPL
        from .repl import PluaREPL
        repl = PluaREPL(runtime)
        await repl.start()

    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
    except Exception as e:
        print(f"Runtime error: {e}")
    finally:
        if api_server:
            try:
                await api_server.stop()
            except Exception:
                pass
        if api_task and not api_task.done():
            api_task.cancel()
            try:
                await asyncio.gather(api_task, return_exceptions=True)
            except Exception:
                pass


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
        print(f"WebUI on http://127.0.0.1:{api_config['port']}/web")
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
        if api_server:
            try:
                await api_server.stop()
            except Exception:
                pass
        if api_task and not api_task.done():
            api_task.cancel()
            try:
                await asyncio.gather(api_task, return_exceptions=True)
            except Exception:
                pass


def main() -> None:
    """Main entry point for the plua command line tool"""

    parser = argparse.ArgumentParser(
        description="plua - Python-Lua async runtime with timer support",
        epilog="Examples:\n"
               "  plua                               # Interactive REPL mode\n"
               "  plua script.lua                    # Run script.lua with API server\n"
               "  plua -i script.lua                 # Run script.lua then enter REPL\n"
               "  plua --noapi script.lua            # Run script.lua without API server\n"
               "  plua --api-port 9000 script.lua    # Run with API on port 9000\n"
               "  plua --duration 10 script.lua      # Run for 10 seconds\n"
               "  plua -e 'print(\"hello\")'           # Run inline script\n"
               "  plua -e 'x=1' -e 'print(x)'        # Multiple -e fragments\n"
               "  plua -e 'print(\"start\")' script.lua # Combine -e and file\n"
               "  plua -i -e 'x=1' script.lua        # Run fragments + file, then REPL\n"
               "  plua -a 'extra args' script.lua    # Pass extra arguments to runtime\n"
               "  plua --fibaro script.lua           # Run with Fibaro API support\n"
               "  plua --debugger script.lua         # Run with MobDebug\n"
               "  plua --debugger --debug script.lua # Run with verbose debug logging\n"
               "  plua --cleanup-port                # Clean up stuck API port\n"
               "  plua --close-windows               # Close all QuickApp windows\n"
               "  plua --desktop script.lua          # Force desktop UI (override QA)\n"
               "  plua --desktop=false script.lua    # Force no desktop UI (override QA)\n"
               "  plua --debugger --debugger-host 192.168.1.100 script.lua",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # log command line given to plua
    #  print(f"Command line: {' '.join(sys.argv)}")

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
        help="Enable MobDebug debugger (handled in init.lua)",
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
        help="Enable debug logging for MobDebug and plua internals",
        action="store_true"
    )

    parser.add_argument(
        "--ignore-lua",
        help="Busted compatibility",
        action="store_true"
    )

    parser.add_argument(
        "--lua",
        help="Enable debug logging for MobDebug and plua internals",
        type=str,
        default="lua"  # Default to 'lua' if not specified
    )

    parser.add_argument(
        "--fibaro",
        help="Load Fibaro API support (equivalent to -e \"require('fibaro')\")",
        action="store_true"
    )

    parser.add_argument(
        "-i", "--interactive",
        help="Enter interactive REPL after running script fragments and main file",
        action="store_true"
    )

    parser.add_argument(
        "-a", "--args",
        help="Extra arguments to pass to the Lua runtime",
        type=str,
        default=None
    )

    parser.add_argument(
        "-l", "--library",
        help="EIgnored for now...",
        type=str,
        default=None
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

    parser.add_argument(
        "--close-windows",
        help="Close all open QuickApp windows and exit",
        action="store_true"
    )

    parser.add_argument(
        "--desktop",
        help="Override desktop UI mode for QuickApp windows (true/false). If not specified, QA decides based on --%%desktop header",
        nargs="?",
        const="true",
        type=str,
        default=None
    )

    args = parser.parse_args()

    # Set up signal handlers for graceful shutdown (especially for VS Code termination)
    setup_signal_handlers()

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

    # Handle window closure if requested
    if args.close_windows:
        try:
            from .luafuns_lib import close_all_quickapp_windows
            result = close_all_quickapp_windows()
            print(f"QuickApp window closure: {result['message']}")
            # Use os._exit() to bypass atexit handlers since we've already done the cleanup
            os._exit(0 if result['success'] else 1)
        except Exception as e:
            print(f"Error closing QuickApp windows: {e}")
            os._exit(1)

    # Prepare debugger config if requested
    debugger_config = None
    if args.debugger:
        debugger_config = {
            'host': args.debugger_host,
            'port': args.debugger_port,
            'debug': args.debug
        }
    
    # Parse desktop argument: None means QA decides, True/False means CLI override
    desktop_override = None
    if args.desktop is not None:
        desktop_str = args.desktop.lower()
        if desktop_str in ('true', '1', 'yes', 'on'):
            desktop_override = True
        elif desktop_str in ('false', '0', 'no', 'off'):
            desktop_override = False
        else:
            print(f"Warning: Invalid --desktop value '{args.desktop}'. Use true/false. Ignoring.")
            desktop_override = None
    
    # Collect all config into a single dictionary
    config = {
        'debugger_config': debugger_config,
        'debug': args.debug,
        'api_config': None if args.noapi else {'host': args.api_host, 'port': args.api_port},
        'source_name': None,  # source_name will be set based on args.lua_file
        'args': args.args,  # Extra arguments passed via -a/--args
        'desktop': desktop_override,  # Desktop UI mode override (None = QA decides, True/False = CLI override)
        # Add more CLI flags here as needed
    }
    runtime = LuaAsyncRuntime(config=config)
    
    # Initialize desktop UI if explicitly requested via CLI (desktop_override = True)
    # Note: If desktop_override is None, the QA will decide based on --%%desktop header
    if desktop_override is True:
        try:
            from .desktop_ui import initialize_desktop_ui
            api_base_url = f"http://{args.api_host}:{args.api_port}" if not args.noapi else "http://localhost:8888"
            initialize_desktop_ui(api_base_url)
            print(f"Desktop UI initialized via CLI override. API available at {api_base_url}")
        except ImportError:
            print("Warning: Desktop UI not available. Install with: pip install pywebview")
        except Exception as e:
            print(f"Warning: Could not initialize desktop UI: {e}")
    
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

    # Determine if we should enter interactive mode
    has_script_content = bool(script_fragments or main_script or main_file)
    interactive_mode = args.interactive or not has_script_content

    if has_script_content and not interactive_mode:
        # Run script and exit
        try:
            asyncio.run(run_script(runtime=runtime, script_fragments=script_fragments, main_script=main_script, main_file=main_file, duration=args.duration))
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            # Cleanup QuickApp windows on interruption
            try:
                from .luafuns_lib import close_all_quickapp_windows
                close_all_quickapp_windows()
            except Exception as e:
                print(f"Window cleanup error: {e}")
            sys.exit(0)
        except asyncio.CancelledError:
            # Handle cancellation during shutdown (e.g., from _PY.isRunning termination)
            # This is expected behavior, exit cleanly without showing error
            try:
                from .luafuns_lib import close_all_quickapp_windows
                close_all_quickapp_windows()
            except:
                pass
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            try:
                from .luafuns_lib import close_all_quickapp_windows
                close_all_quickapp_windows()
            except:
                pass
            sys.exit(1)
    else:
        # Either no script content (implicit interactive) or explicit -i flag
        # Run script content first (if any), then enter REPL
        try:
            asyncio.run(run_interactive(runtime=runtime, script_fragments=script_fragments, main_script=main_script, main_file=main_file, duration=args.duration))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            # Cleanup QuickApp windows on interruption
            try:
                from .luafuns_lib import close_all_quickapp_windows
                close_all_quickapp_windows()
            except Exception as e:
                print(f"Window cleanup error: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()
