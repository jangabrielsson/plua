#!/usr/binimport asyncio
import sys
import argparse
import io
import os
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Handle tomllib import for different Python versions
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python versions
    except ImportError:
        tomllib = Nonen3
"""
PLua CLI - Python Lua Engine with Web UI

Simplified single-threaded architecture for running Lua scripts.
- Single thread architecture (main=lua engine)
- Interactive REPL mode with command history
- Focused on web UI without tkinter complexity
"""

import asyncio
import sys
import argparse
import io
import os
import subprocess
import logging
import tomllib
from pathlib import Path
from typing import Optional, Dict, Any

# Set up logger
logger = logging.getLogger(__name__)


# Fix Windows Unicode output issues
def setup_unicode_output():
    """Setup proper Unicode output for Windows console"""
    if sys.platform == "win32":
        try:
            # Try to set console to UTF-8 mode (Windows 10 1903+)
            os.system("chcp 65001 >nul 2>&1")

            # Wrap stdout/stderr with UTF-8 encoding
            if hasattr(sys.stdout, "buffer"):
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding="utf-8", errors="replace"
                )
            if hasattr(sys.stderr, "buffer"):
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer, encoding="utf-8", errors="replace"
                )
        except Exception:
            # If anything fails, we'll fall back to ASCII-safe output
            pass


# Call this early
setup_unicode_output()


def get_version():
    """Get PLua version from pyproject.toml"""
    try:
        if tomllib is None:
            # Fallback: try to parse manually if tomllib is not available
            current_dir = Path(__file__).parent
            pyproject_path = current_dir.parent.parent / "pyproject.toml"
            
            if pyproject_path.exists():
                with open(pyproject_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("version ="):
                            # Extract version from line like: version = "0.1.0"
                            version_part = line.split("=", 1)[1].strip()
                            return version_part.strip('"\'')
            return "unknown"
        
        # Use tomllib if available
        current_dir = Path(__file__).parent
        pyproject_path = current_dir.parent.parent / "pyproject.toml"
        
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "unknown")
        else:
            return "unknown"
    except Exception:
        return "unknown"


def display_startup_greeting(config: Dict[str, Any]):
    """Display a proper startup greeting with version information"""
    import sys
    try:
        import lupa
        lua_runtime = lupa.LuaRuntime()
        lua_version = lua_runtime.execute("return _VERSION")
        if lua_version:
            lua_version = lua_version.replace("Lua ", "")
        else:
            lua_version = "Unknown"
    except Exception:
        lua_version = "Unknown"
    
    api_port = config.get("api_port", 8080)
    telnet_port = config.get("telnet_port", 8023)
    plua_version = get_version()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # ANSI color codes
    CYAN = "\033[96m"
    GREEN = "\033[92m" 
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Use colored print for startup greeting
    print(f"{CYAN}{BOLD}🚀 PLua version {plua_version}{RESET}")
    print(f"{GREEN}Python:{python_version}{RESET}, {BLUE}Lua:{lua_version}{RESET}")
    print(f"{YELLOW}API:{api_port}{RESET}, {MAGENTA}Telnet:{telnet_port}{RESET}")


def safe_print(message, fallback_message=None):
    """Print with Unicode support, fallback to ASCII if needed"""
    try:
        # Try to use logger if available, otherwise fall back to print
        try:
            logger.info(message)
            return
        except NameError:
            # Logger not available yet, use print
            pass
        
        print(message)
    except UnicodeEncodeError:
        if fallback_message:
            ascii_message = fallback_message
        else:
            # Convert Unicode characters to ASCII equivalents
            ascii_message = (
                message.encode("ascii", errors="replace").decode("ascii")
            )
        try:
            logger.info(ascii_message)
        except NameError:
            print(ascii_message)


def get_config():
    """Get platform and runtime configuration"""
    config = {
        "platform": sys.platform,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "architecture": "single-threaded",
        "ui_mode": "web",
        "fileSeparator": "\\\\" if sys.platform == "win32" else "/",
        "pathSeparator": ";" if sys.platform == "win32" else ":",
        "isWindows": sys.platform == "win32",
        "isMacOS": sys.platform == "darwin",
        "isLinux": sys.platform.startswith("linux"),
        "enginePath": str(Path(__file__).parent.parent).replace("\\", "\\\\"),
        "luaLibPath": str(Path(__file__).parent.parent / "lua").replace("\\", "\\\\"),
    }
    return config


def run_engine(
    script_path: Optional[str] = None,
    fragments: list = None,
    config: Dict[str, Any] = None,
):
    """Run Lua engine in main thread"""
    try:
        from plua.engine import LuaEngine

        async def engine_main():
            try:
                # Create and configure engine
                engine = LuaEngine(config=config)

                # Setup logging level from config
                if config and "loglevel" in config:
                    import logging
                    level_name = config["loglevel"].upper()
                    if hasattr(logging, level_name):
                        level = getattr(logging, level_name)
                        logging.getLogger().setLevel(level)
                        logging.getLogger().info(f"Set logging level to {level_name}")

                # Start Lua environment and bindings
                await engine.start()
                
                # Start telnet server for REPL access
                telnet_port = config.get("telnet_port", 8023)
                await engine.run_script(f'_PY.start_telnet_server({telnet_port})', "telnet_server_start")
                
                # Start FastAPI server process if enabled
                if config.get("api_enabled", True):
                    try:
                        # Kill any existing process using the API port
                        api_port = config.get("api_port", 8080)
                        try:
                            import subprocess
                            # Find processes using the port
                            result = subprocess.run(
                                ["lsof", "-ti", f":{api_port}"], 
                                capture_output=True, 
                                text=True, 
                                check=False
                            )
                            if result.stdout.strip():
                                pids = result.stdout.strip().split('\n')
                                for pid in pids:
                                    if pid:
                                        subprocess.run(["kill", "-9", pid], check=False)
                        except Exception as e:
                            # Port cleanup failed, but continue anyway
                            logger.warning(f"Port cleanup failed: {e}")
                        
                        from plua.fastapi_process import start_fastapi_process
                        
                        # Start FastAPI in separate process
                        api_manager = start_fastapi_process(
                            host=config.get("api_host", "localhost"),
                            port=api_port,
                            config=config
                        )
                        
                        # Give process a moment to start
                        await asyncio.sleep(1.0)
                        
                        # Connect process to engine via IPC
                        def lua_executor(code: str, timeout: float = 30.0):
                            """Thread-safe Lua executor for FastAPI process"""
                            try:
                                result = engine.execute_script_from_thread(code, timeout, is_json=False)
                                return result
                            except Exception as e:
                                return {"success": False, "error": str(e)}
                                
                        api_manager.set_lua_executor(lua_executor)
                        
                        # Always set up Fibaro callback - hook will determine availability
                        def fibaro_callback(method: str, path: str, data: str = None):
                            """Thread-safe Fibaro API callback - receives JSON string, passes to Lua"""
                            try:
                                logger.debug(f"Fibaro callback: {method} {path}")
                                
                                # Parse JSON data if provided
                                data_obj = None
                                if data:
                                    try:
                                        import json
                                        data_obj = json.loads(data)
                                    except json.JSONDecodeError:
                                        logger.warning(f"Invalid JSON data: {data}")
                                        data_obj = None
                                
                                # Use the existing thread-safe IPC mechanism correctly
                                try:
                                    # The key insight: pass data as JSON string to Lua and let Lua parse it
                                    # This avoids all the syntax issues with embedding data in Lua code
                                    
                                    data_str = data if data else "nil"
                                    
                                    # Simple Lua script that calls the hook with string data
                                    lua_script = f'''
                                        local method = "{method}"
                                        local path = "{path}"
                                        local data_str = {repr(data_str)}
                                        
                                        local hook_data, hook_status = _PY.fibaroApiHook(method, path, data_str)
                                        return {{data = hook_data, status = hook_status or 200}}
                                    '''
                                    
                                    result = engine.execute_script_from_thread(lua_script, 30.0, is_json=False)
                                    logger.debug(f"Thread execution result: {result}")
                                    
                                    if result.get("success", False):
                                        lua_result = result.get("result", {})
                                        if isinstance(lua_result, dict):
                                            hook_data = lua_result.get("data")
                                            hook_status = lua_result.get("status", 200)
                                            logger.debug(f"Hook returned: {hook_data}, {hook_status}")
                                            return hook_data, hook_status
                                        else:
                                            logger.debug(f"Fallback return: {lua_result}, 200")
                                            return lua_result, 200
                                    else:
                                        logger.error(f"Thread execution failed: {result.get('error')}")
                                        return f"Thread execution error: {result.get('error')}", 500
                                    
                                except Exception as e:
                                    logger.error(f"Thread execution exception: {str(e)}")
                                    return f"Thread execution error: {str(e)}", 500
                                    
                            except Exception as e:
                                logger.error(f"Callback exception: {str(e)}")
                                return f"Callback error: {str(e)}", 500
                                
                        api_manager.set_fibaro_callback(fibaro_callback)
                        
                        # QuickApp data callback
                        def quickapp_callback(action: str, qa_id: int = None):
                            """Handle QuickApp data requests"""
                            try:
                                if action == "get_quickapp" and qa_id is not None:
                                    # Get specific QuickApp via Lua
                                    lua_script = f'''
                                        local qa_id = {qa_id}
                                        
                                        -- Try fibaro.plua first (this is the working path)
                                        if fibaro and fibaro.plua and fibaro.plua.getQuickApp then
                                            local qa_info = fibaro.plua:getQuickApp(qa_id)
                                            if qa_info then
                                                return json.encode(qa_info)
                                            end
                                        end
                                        
                                        -- Fallback to Emu if available
                                        if Emu and Emu.getQuickApp then
                                            local qa_info = Emu:getQuickApp(qa_id)
                                            if qa_info then
                                                return json.encode(qa_info)
                                            end
                                        end
                                        
                                        return "null"
                                    '''
                                    result = engine.execute_script_from_thread(lua_script, 30.0, is_json=False)
                                    if result.get("success") and result.get("result") != "null":
                                        import json
                                        return json.loads(result.get("result", "null"))
                                    return None
                                    
                                elif action == "get_all_quickapps":
                                    # Get all QuickApps via Lua
                                    lua_script = '''
                                        -- Try fibaro.plua first (this is the working path)
                                        if fibaro and fibaro.plua and fibaro.plua.getQuickApps then
                                            local all_qas = fibaro.plua:getQuickApps()
                                            return json.encode(all_qas)
                                        end
                                        
                                        -- Fallback to Emu if available
                                        if Emu and Emu.getQuickApps then
                                            local all_qas = Emu:getQuickApps()
                                            return json.encode(all_qas)
                                        end
                                        
                                        return "[]"
                                    '''
                                    result = engine.execute_script_from_thread(lua_script, 30.0, is_json=False)
                                    if result.get("success"):
                                        import json
                                        return json.loads(result.get("result", "[]"))
                                    return []
                                else:
                                    return None
                            except Exception as e:
                                logger.error(f"QuickApp callback error: {e}")
                                return None
                                
                        api_manager.set_quickapp_callback(quickapp_callback)
                        
                        # Store reference to api_manager for WebSocket broadcasting
                        engine._api_manager = api_manager
                            
                    except Exception as e:
                        logger.warning(f"Failed to start FastAPI server process: {e}")
                        logger.info("Continuing without API server...")

                if script_path:
                    await engine.run_script(
                        f'_PY.mainLuaFile("{script_path}")', script_path
                    )
                elif fragments:
                    logger.info("Running Lua fragments...")
                    for i, fragment in enumerate(fragments):
                        await engine.run_script(
                            f"_PY.luaFragment({repr(fragment)})", f"fragment_{i}"
                        )
                else:
                    logger.info("Starting interactive mode")
                
                # Keep the engine running if there are active operations (timers, callbacks, etc.)
                if engine.has_active_operations():
                    logger.info("Keeping engine alive due to active operations")
                    while engine.has_active_operations():
                        await asyncio.sleep(1)
                    logger.info("All operations completed, shutting down")
                elif not script_path and not fragments:
                    # Interactive mode - keep running indefinitely
                    while True:
                        await asyncio.sleep(1)
                else:
                    # Script completed - check for active operations with timeout
                    logger.debug("Script completed, checking for active operations")
                    await asyncio.sleep(0.5)  # Brief grace period for cleanup
                    
                    if not engine.has_active_operations():
                        logger.info("No active operations detected - forcing clean shutdown")
                        # Force immediate termination - bypass any hanging background processes
                        import os
                        import sys
                        sys.stdout.flush()
                        sys.stderr.flush()
                        os._exit(0)
                    else:
                        logger.info("Active operations detected, will keep running")
                        while engine.has_active_operations():
                            await asyncio.sleep(1)
                        logger.info("All operations completed - forcing shutdown")
                        import os
                        import sys
                        sys.stdout.flush()
                        sys.stderr.flush()
                        os._exit(0)

            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                # Force clean exit without asyncio traceback
                import os
                import sys
                sys.stdout.flush()
                sys.stderr.flush()
                os._exit(0)
            except Exception as e:
                logger.error(f"Engine error: {e}")
            finally:
                # Clean up FastAPI server process
                try:
                    from plua.fastapi_process import stop_fastapi_process
                    stop_fastapi_process()
                except Exception:
                    pass

        # Run the async engine
        try:
            asyncio.run(engine_main())
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            # Force clean exit without asyncio traceback
            import os
            import sys
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(0)

    except ImportError as e:
        logger.error(f"Import error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def run_script_with_config(
    script_path: Optional[str] = None, 
    fragments: list = None, 
    config: Dict[str, Any] = None,
    force_no_gui: bool = False
):
    """Main entry point for running scripts"""
    
    config = config or get_config()
    
    # Display startup greeting with version information
    display_startup_greeting(config)

    # Setup basic stub UI functions (for compatibility)
    def setup_stub_functions():
        """Setup stub UI functions when web UI is not yet implemented"""
        from plua.lua_bindings import export_to_lua

        @export_to_lua("gui_available")
        def gui_available() -> bool:
            return False

        @export_to_lua("isNativeUIAvailable") 
        def is_native_ui_available() -> bool:
            return False

        @export_to_lua("createNativeWindow")
        def create_native_window(
            title: str, width: int = 400, height: int = 300
        ) -> str:
            return "ERROR: Web UI not yet implemented"

    setup_stub_functions()

    # Run engine in main thread
    run_engine(script_path, fragments, config)


def run_interactive_repl(config: Dict[str, Any]):
    """Start interactive REPL mode by spawning a REPL client process"""
    try:
        # Start the engine in interactive mode (similar to regular script execution)
        async def start_repl_engine():
            from plua.engine import LuaEngine
            
            engine = LuaEngine(config=config)
            
            try:
                # Display startup greeting
                display_startup_greeting(config)
                
                # Start engine
                await engine.start()
                
                # Start telnet server for REPL access
                telnet_port = config.get("telnet_port", 8023)
                await engine.run_script(f'_PY.start_telnet_server({telnet_port})', "telnet_server_start")
                
                # Give telnet server a moment to start
                await asyncio.sleep(0.5)
                
                # Now spawn the REPL client process
                logger.info("Starting REPL client...")
                logger.info(f"Connecting to telnet server on localhost:{telnet_port}...")

                # Find the repl.py file
                repl_path = Path(__file__).parent / "repl.py"
                if not repl_path.exists():
                    logger.error("REPL client not found")
                    return

                # Spawn the REPL client process with the configured port
                import subprocess
                # Start REPL client in background 
                subprocess.Popen([sys.executable, str(repl_path), "--port", str(telnet_port)])
                
                # Keep the engine running indefinitely for REPL access
                logger.info("REPL mode active. Engine will run until terminated.")
                while True:
                    await asyncio.sleep(1)
                    
            except KeyboardInterrupt:
                logger.info("REPL interrupted by user")
            finally:
                await engine.stop()
                
        # Run the async engine
        asyncio.run(start_repl_engine())

    except KeyboardInterrupt:
        logger.info("REPL interrupted")
    except Exception as e:
        logger.error(f"REPL error: {e}")


def main():
    """Main CLI entry point"""
    # Suppress multiprocessing resource tracker warnings
    import os
    os.environ["PYTHONWARNINGS"] = "ignore::UserWarning:multiprocessing.resource_tracker"
    
    # Set up basic logging first (will be updated with user preference later)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(
        description="PLua - Python Lua Engine with Web UI"
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="Show version information"
    )
    parser.add_argument(
        "--init-qa", action="store_true", help="Initialize a new QuickApp project"
    )
    parser.add_argument(
        "script", nargs="?", help="Lua script file to run (optional)"
    )
    parser.add_argument(
        "-e", "--eval", action="append", help="Execute Lua code fragments"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Start REPL mode"
    )
    parser.add_argument(
        "--loglevel",
        choices=["debug", "info", "warning", "error"],
        default="warning",
        help="Set logging level",
    )
    parser.add_argument(
        "-o",
        "--offline",
        action="store_true",
        help="Run in offline mode (disable HC3 connections)",
    )
    parser.add_argument(
       "--desktop",
        help="Override desktop UI mode for QuickApp windows (true/false). If not specified, QA decides based on --%%desktop header",
        nargs="?",
        const="true",
        type=str,
        default=None
    )
    parser.add_argument(
        "--nodebugger",
        action="store_true",
        help="Disable Lua debugger support",
    )
    parser.add_argument(
        "--fibaro",
        action="store_true",
        help="Enable Fibaro HC3 emulation mode",
    )
    parser.add_argument(
        "-l",
        help="Ignored, for Lua CLI compatibility",
    )
    parser.add_argument(
        "--header",
        action="append",
        help="Add header string (can be used multiple times)",
    )
    parser.add_argument(
        "-a", "--args",
        help="Add argument string to pass to the script",
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=8080,
        help="Port for FastAPI server (default: 8080)",
    )
    parser.add_argument(
        "--api-host",
        default="localhost", 
        help="Host for FastAPI server (default: localhost)",
    )
    parser.add_argument(
        "--telnet-port",
        type=int,
        default=8023,
        help="Port for telnet server (default: 8023)",
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Disable FastAPI server",
    )
    parser.add_argument(
        "--run-for",
        type=int,
        help="Run script for specified seconds then terminate",
    )

    args = parser.parse_args()

    # Handle version command
    if args.version:
        version = get_version()
        print(f"PLua {version}")
        return

    # Handle QuickApp project initialization
    if args.init_qa:
        from plua.scaffolding import init_quickapp_project
        init_quickapp_project()
        return

    # Prepare config
    config = get_config()
    config["loglevel"] = args.loglevel
    config["offline"] = args.offline
    config["desktop"] = args.desktop
    config["debugger"] = not args.nodebugger
    config["fibaro"] = args.fibaro
    config["headers"] = args.header or []
    config["api_enabled"] = not args.no_api
    config["api_host"] = args.api_host
    config["api_port"] = args.api_port
    config["telnet_port"] = args.telnet_port
    config["runFor"] = args.run_for
    config["args"] = args.args

    if args.interactive:
        run_interactive_repl(config)
    else:
        run_script_with_config(
            script_path=args.script,
            fragments=args.eval,
            config=config,
        )


if __name__ == "__main__":
    main()