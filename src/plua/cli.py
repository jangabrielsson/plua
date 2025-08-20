#!/usr/binimport asyncio
import atexit
import sys
import argparse
import io
import os
import platform
import subprocess
import logging
import time 
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


def ensure_plua_directory():
    """Ensure ~/.plua directory exists for configuration and state files"""
    plua_dir = os.path.expanduser("~/.plua")
    os.makedirs(plua_dir, exist_ok=True)
    return plua_dir


def detect_environment():
    """Detect the environment PLua is running in based on command line arguments"""
    # Get the full command line as a string
    argv_str = " ".join(sys.argv)
    
    # Check for VS Code environment
    if "vscode" in argv_str and "lua-mobdebug" in argv_str:
        return "vscode"
    
    # Check for ZeroBrane Studio environment
    if "io.stdout:setvbuf('no')" in argv_str:
        return "zerobrane"
    
    # Default to terminal
    return "terminal"


def get_version():
    """Get PLua version from __init__.py or pyproject.toml"""
    try:
        # First try to get version from the installed package
        try:
            import plua
            if hasattr(plua, '__version__'):
                return plua.__version__
        except ImportError:
            pass
        
        # Fallback: try to get from development environment
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
    from .console import console
    from rich.panel import Panel
    from rich.text import Text
    
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
    
    # Create a rich greeting with panel
    greeting_text = Text()
    greeting_text.append("🚀 PLua version ", style="bright_white")
    greeting_text.append(plua_version, style="version")
    greeting_text.append("\n")
    greeting_text.append("Python:", style="python")
    greeting_text.append(python_version, style="python")
    greeting_text.append(", ", style="dim")
    greeting_text.append("Lua:", style="lua") 
    greeting_text.append(lua_version, style="lua")
    greeting_text.append("\n")
    greeting_text.append("API:", style="api")
    greeting_text.append(str(api_port), style="api")
    
    if config['telnet']:
        greeting_text.append(", ", style="dim")
        greeting_text.append("Telnet:", style="telnet")
        greeting_text.append(str(telnet_port), style="telnet")
    
    # Display in a subtle panel for better visual separation
    console.print(Panel(greeting_text, border_style="dim", padding=(0, 1)))


def safe_print(message, fallback_message=None):
    """Print with Unicode support using Rich, fallback if needed"""
    try:
        # Try to use Rich console first for better Unicode support
        from .console import console
        console.print(message)
    except Exception:
        # Fallback to basic print with Unicode handling
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
        "enginePath": str(Path(__file__).parent.parent).replace("\\", "/"),
        "luaLibPath": str(Path(__file__).parent.parent / "lua").replace("\\", "/"),
        "environment": detect_environment(),
        # Set temdir in lua
        # "tempdir": os.path.join(os.path.expanduser("~"), "tmp") if platform.system() != "Windows" else os.environ.get("TEMP", "C:\\temp"),
    }
    return config


def run_engine(
    script_paths: list = None,
    fragments: list = None,
    config: Dict[str, Any] = None,
    interactive: bool = False,
    telnet_mode: bool = False,
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
                
                # Start telnet server if telnet mode is requested
                if telnet_mode:
                    telnet_port = config.get("telnet_port", 8023)
                    await engine.run_script(f'_PY.start_telnet_server({telnet_port})', "telnet_server_start")
                    logger.info(f"Telnet server started on localhost:{telnet_port}")
                    logger.info("You can connect with: telnet localhost 8023")
                
                # Start FastAPI server process if enabled
                if config.get("api_enabled", True):
                    try:
                        # Kill any existing process using the API port
                        api_port = config.get("api_port", 8080)
                        
                        def cleanup_port_windows(port):
                            """Windows-specific port cleanup with minimal delays"""
                            import time
                            max_retries = 2
                            
                            for attempt in range(max_retries):
                                try:
                                    # Use netstat to find processes using the specific port
                                    result = subprocess.run(
                                        ["netstat", "-ano", "-p", "TCP"], 
                                        capture_output=True, 
                                        text=True, 
                                        check=False
                                    )
                                    
                                    if result.returncode == 0 and result.stdout:
                                        killed_any = False
                                        lines = result.stdout.split('\n')
                                        
                                        for line in lines:
                                            # Look for lines with our specific port in LISTENING state
                                            if "LISTENING" in line and f":{port} " in line:
                                                parts = line.split()
                                                if len(parts) >= 5:
                                                    pid = parts[-1]
                                                    if pid.isdigit() and pid != "0":
                                                        logger.info(f"Killing process {pid} using port {port}")
                                                        kill_result = subprocess.run(
                                                            ["taskkill", "/F", "/PID", pid], 
                                                            capture_output=True,
                                                            check=False
                                                        )
                                                        if kill_result.returncode == 0:
                                                            killed_any = True
                                        
                                        if killed_any:
                                            # Minimal wait for port release - just 100ms
                                            time.sleep(0.1)
                                            
                                            # Quick check if port is still in use
                                            check_result = subprocess.run(
                                                ["netstat", "-ano", "-p", "TCP"], 
                                                capture_output=True, 
                                                text=True, 
                                                check=False
                                            )
                                            
                                            if check_result.returncode == 0:
                                                still_used = any(
                                                    "LISTENING" in line and f":{port} " in line 
                                                    for line in check_result.stdout.split('\n')
                                                )
                                                if not still_used:
                                                    logger.info(f"Port {port} successfully cleaned up")
                                                    return True
                                        else:
                                            # No processes found using the port
                                            return True
                                            
                                except Exception as e:
                                    logger.debug(f"Port cleanup attempt {attempt + 1} failed: {e}")
                                    
                                if attempt < max_retries - 1:
                                    # Very short retry delay - just 200ms
                                    time.sleep(0.2)
                            
                            return False
                        
                        def cleanup_port_unix(port):
                            """Unix/Linux/macOS port cleanup"""
                            try:
                                result = subprocess.run(
                                    ["lsof", "-ti", f":{port}"], 
                                    capture_output=True, 
                                    text=True, 
                                    check=False
                                )
                                if result.stdout.strip():
                                    pids = result.stdout.strip().split('\n')
                                    for pid in pids:
                                        if pid:
                                            subprocess.run(["kill", "-9", pid], check=False)
                                    return True
                                return True
                            except Exception:
                                return False
                        
                        try:
                            # Platform-specific port cleanup
                            if platform.system() == "Windows":
                                success = cleanup_port_windows(api_port)
                                if not success:
                                    logger.warning(f"Could not fully clean up port {api_port}, but continuing...")
                            else:
                                success = cleanup_port_unix(api_port)
                                if not success:
                                    logger.warning(f"Could not clean up port {api_port}, but continuing...")
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
                        
                        # Register cleanup handler for proper process termination
                        def cleanup_fastapi():
                            try:
                                if api_manager and api_manager.is_running():
                                    logger.info("Cleaning up FastAPI process on exit")
                                    api_manager.stop()
                            except Exception as e:
                                logger.debug(f"Error during FastAPI cleanup: {e}")
                        
                        atexit.register(cleanup_fastapi)
                        
                        # Set up IPC connections immediately (no blocking wait)
                        # FastAPI process will queue requests until it's ready
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

                # Run scripts or fragments if specified
                if script_paths:
                    logger.info(f"Running {len(script_paths)} Lua script(s)...")
                    # Create Lua array syntax for all script paths (normalize paths for Lua)
                    normalized_paths = [path.replace("\\", "/") for path in script_paths]
                    lua_array = "{" + ", ".join(f'"{path}"' for path in normalized_paths) + "}"
                    await engine.run_script(
                        f'_PY.mainLuaFile({lua_array})', "scripts_execution"
                    )
                if fragments:
                    logger.info("Running Lua fragments...")
                    for i, fragment in enumerate(fragments):
                        await engine.run_script(
                            f"_PY.luaFragment({repr(fragment)})", f"fragment_{i}"
                        )

                # If interactive mode requested, start REPL
                if interactive:
                    logger.info("Async REPL started. Type 'exit' or press Ctrl+C to quit.")
                    # Start the asyncio REPL using the existing engine
                    await engine.run_script('_PY.start_repl()', "async_repl_start")
                    
                    # Keep the engine running while REPL is active
                    while True:
                        # Check if REPL is still running
                        try:
                            result = await engine.run_script('return _PY.get_repl_status()', "repl_status_check")
                            if "not running" in str(result).lower():
                                break
                        except Exception:
                            # If we can't check status, assume REPL is still running
                            pass
                        await asyncio.sleep(0.5)  # Check every 500ms
                    
                    logger.info("Interactive REPL ended")
                    return  # Exit after REPL ends
                
                # Keep the engine running if there are active operations (timers, callbacks, etc.)
                if engine.has_active_operations():
                    logger.info("Keeping engine alive due to active operations")
                    while engine.has_active_operations():
                        await asyncio.sleep(1)
                    logger.info("All operations completed, shutting down")
                elif not script_paths and not fragments and not interactive and not telnet_mode:
                    # No scripts, no fragments, no interactive, no telnet - keep running indefinitely
                    logger.info("No script specified, starting idle mode")
                    while True:
                        await asyncio.sleep(1)
                elif telnet_mode:
                    # Telnet mode - keep running indefinitely for remote access
                    logger.info("Telnet mode active. Engine will run until terminated.")
                    while True:
                        await asyncio.sleep(1)
                else:
                    # Scripts completed - check for active operations with timeout
                    logger.debug("Scripts completed, checking for active operations")
                    await asyncio.sleep(0.5)  # Brief grace period for cleanup
                    
                    if not engine.has_active_operations():
                        logger.info("No active operations detected - shutting down")
                    else:
                        logger.info("Active operations detected, will keep running")
                        while engine.has_active_operations():
                            await asyncio.sleep(1)
                        logger.info("All operations completed - shutting down")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                logger.info("Interrupted by user")
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
            print("\n👋 Goodbye!")
            logger.info("Interrupted by user")

    except ImportError as e:
        logger.error(f"Import error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def run_telnet_server(config: Dict[str, Any]):
    """Start telnet server mode using the main engine architecture"""
    # Use the main engine architecture but start telnet server
    logger.info("Starting PLua with telnet server mode")
    run_engine(
        script_paths=None,
        fragments=None,
        config=config,
        interactive=False,  # We don't want stdin/stdout REPL
        telnet_mode=True    # We want telnet server
    )


def run_async_repl(engine):
    """Start async REPL mode using the existing engine"""
    import asyncio
    
    async def repl_main():
        """Start the REPL using the existing engine"""
        try:
            # Start the asyncio REPL using the existing engine
            await engine.run_script('_PY.start_repl()', "async_repl_start")
            
            # Keep the engine running while REPL is active
            # The REPL will handle all interaction directly on stdin/stdout
            while True:
                # Check if REPL is still running
                result = await engine.run_script('return _PY.get_repl_status()', "repl_status_check")
                if "not running" in str(result).lower():
                    break
                await asyncio.sleep(0.5)  # Check every 500ms
                
        except KeyboardInterrupt:
            # Stop the REPL gracefully
            await engine.run_script('_PY.stop_repl()', "async_repl_stop")
            logger.info("REPL stopped")
    
    # Run the REPL
    try:
        asyncio.run(repl_main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        logger.info("REPL interrupted")
    except Exception as e:
        logger.error(f"REPL error: {e}")


def main():
    """Main CLI entry point"""
    startTime = time.time()
    # Suppress multiprocessing resource tracker warnings (only if warnings module is available)
    import os
    try:
        import warnings
        os.environ["PYTHONWARNINGS"] = "ignore::UserWarning:multiprocessing.resource_tracker"
    except ImportError:
        # warnings module not available (e.g., in Nuitka build), skip warning suppression
        pass
    
    # Ensure ~/.plua directory exists early
    ensure_plua_directory()
    
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
        "scripts", nargs="*", help="Lua script files to run (optional, multiple files allowed)"
    )
    parser.add_argument(
        "-e", "--eval", action="append", help="Execute Lua code fragments"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Start interactive REPL mode (stdin/stdout with prompt_toolkit)"
    )
    parser.add_argument(
        "--telnet", action="store_true", help="Start telnet server for remote REPL access"
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
        "-t", "--tool",
        action="store_true",
        help="Run tool, [help, downloadQA, uploadQA, updateFile, updateQA]"
    )
    parser.add_argument(
        "--nodebugger",
        action="store_true",
        help="Disable Lua debugger support",
    )
    parser.add_argument(
        "--nogreet",
        action="store_true",
        help="Suppress startup greeting message",
    )
    parser.add_argument(
        "--fibaro",
        action="store_true",
        help="Enable Fibaro HC3 emulation mode",
    )
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="Run diagnostic tests",
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
    config["nogreet"] = args.nogreet
    config["fibaro"] = args.fibaro
    config["headers"] = args.header or []
    config["api_enabled"] = not args.no_api
    config["api_host"] = args.api_host
    config["api_port"] = args.api_port
    config["telnet"] = args.telnet
    config["telnet_port"] = args.telnet_port
    config["runFor"] = args.run_for
    config["scripts"] = args.scripts or []
    config["tool"] = args.tool
    config["startTime"] = startTime
    config["diagnostic"] = args.diagnostic or False
    config["environment"] = detect_environment()
    # Store the full CLI command line as a string
    config["argv"] = " ".join([repr(arg) if " " in arg else arg for arg in sys.argv])

    # Configure Rich console based on detected environment
    try:
        from .console import configure_console_for_environment
        configure_console_for_environment(config["environment"])
    except ImportError:
        pass  # Rich not available, continue without styling

    # Display startup greeting for all modes (unless suppressed)
    if not args.nogreet:
        display_startup_greeting(config)

    implicit_interactive = args.scripts == [] and args.telnet == False and args.eval is None
    if args.interactive or implicit_interactive:
        # Interactive mode with main engine
        logger.info("Starting PLua with interactive mode")
        run_engine(
            script_paths=args.scripts,
            fragments=args.eval,
            config=config,
            interactive=True
        )
    elif args.telnet:
        run_telnet_server(config)
    else:
        run_engine(
            script_paths=args.scripts,
            fragments=args.eval,
            config=config,
            interactive=False
        )


if __name__ == "__main__":
    main()