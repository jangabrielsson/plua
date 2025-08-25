"""
Example module showing how to extend PLua with custom functions using decorators.
"""

import os
import json
import logging
import importlib
import importlib.util
import time
from typing import Dict, Any
from .lua_bindings import export_to_lua, python_to_lua_table, lua_to_python_table, get_exported_functions, get_global_engine

# Import window manager for browser-based UI
try:
    from . import window_manager
    logging.info("Window manager loaded successfully")
except ImportError as e:
    logging.warning(f"Window manager not available: {e}")

# Import remaining extension modules (FFI libraries are now in pylib/)
# Use try/except to make imports safer
try:
    from . import web_server  # noqa: F401
except ImportError as e:
    logging.debug(f"web_server not available: {e}")

try:
    from . import sync_socket  # noqa: F401
except ImportError as e:
    logging.debug(f"sync_socket not available: {e}")

# Import pylib to register FFI libraries
try:
    import pylib  # noqa: F401
    logging.info("PyLib FFI libraries loaded successfully")
except ImportError as e:
    logging.warning(f"PyLib not available: {e}")


@export_to_lua("loadPythonModule")
def load_python_module(module_name: str) -> Dict[str, Any]:
    """
    Dynamically load a Python module and make its exported functions available to Lua.

    This function provides a FFI-like interface where Lua can load Python modules
    on demand. The module is imported (or reloaded) and all functions decorated
    with @export_to_lua are returned to Lua for immediate use.

    Search order:
    1. src/pylib/ directory (bundled FFI libraries)
    2. plua package modules
    3. Standard Python modules

    Args:
        module_name: Name of the module to load (e.g., "filesystem", "http_client")

    Returns:
        Dict containing all exported functions from the module

    Example in Lua:
        local fs_funcs = _PY.loadPythonModule("filesystem")
        local attrs = fs_funcs.fs_attributes("/path/to/file")
    """
    try:
        logging.info(f"Loading Python module: {module_name}")

        # Store current exported functions count
        before_count = len(get_exported_functions())  # noqa: F841

        module = None
        full_module_name = None

        # Try different import strategies
        import_attempts = [
            # 1. Try pylib directory first (bundled FFI libraries)
            f"pylib.{module_name}",
            # 2. Try plua package modules
            f"plua.{module_name}",
            # 3. Try as direct module name
            module_name
        ]

        for attempt in import_attempts:
            try:
                # Check if module is already loaded
                if attempt in importlib.sys.modules:
                    logging.info(f"Reloading existing module: {attempt}")
                    module = importlib.reload(importlib.sys.modules[attempt])
                    full_module_name = attempt
                    break
                else:
                    logging.info(f"Trying to import: {attempt}")
                    module = importlib.import_module(attempt)
                    full_module_name = attempt
                    break
            except ImportError as e:
                logging.debug(f"Import attempt failed for {attempt}: {e}")
                continue

        if module is None:
            raise ImportError(f"Could not import module '{module_name}' from any location")

        logging.info(f"Successfully imported: {full_module_name}")

        # Get all exported functions after import
        all_exported = get_exported_functions()
        after_count = len(all_exported)  # noqa: F841

        # Find functions that were added by this module
        # (This is a simple heuristic - in practice, modules should prefix their functions)
        new_functions = {}
        if hasattr(module, '__name__'):
            # Look for functions that might belong to this module
            module_prefix = module.__name__.split('.')[-1]  # e.g., "filesystem" from "pylib.filesystem"
            for name, func in all_exported.items():
                # Include functions that start with module prefix or are likely from this module
                if (name.startswith(module_prefix.replace('_', '')) or
                    name.startswith(f"{module_prefix}_") or
                    hasattr(func, '__module__') and
                    module.__name__ in str(func.__module__)):
                    new_functions[name] = func

        # If we can't determine which functions are new, return all functions
        # This is safer and mimics the behavior of loading all available functions
        if not new_functions:
            new_functions = all_exported

        logging.info(f"Module {full_module_name} loaded successfully. "
                     f"Available functions: {list(new_functions.keys())}")

        return python_to_lua_table(new_functions)

    except ImportError as e:
        logging.error(f"Failed to import module {module_name}: {e}")
        return python_to_lua_table({"error": f"Module not found: {module_name}"})
    except Exception as e:
        logging.error(f"Error loading module {module_name}: {e}")
        return python_to_lua_table({"error": f"Failed to load module: {e}"})


@export_to_lua("read_file")
def read_file(filename: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


@export_to_lua("write_file")
def write_file(filename: str, content: str) -> bool:
    """Write content to a file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False


@export_to_lua("list_directory")
def list_directory(path: str = ".") -> Any:
    """List directory contents (returns Lua table)."""
    try:
        entries = []
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            entries.append({
                "name": entry,
                "is_file": os.path.isfile(full_path),
                "is_directory": os.path.isdir(full_path),
                "size": os.path.getsize(full_path) if os.path.isfile(full_path) else 0
            })
        result = {"entries": entries, "count": len(entries)}
        return python_to_lua_table(result)
    except Exception as e:
        error_result = {"error": str(e), "entries": [], "count": 0}
        return python_to_lua_table(error_result)


@export_to_lua("parse_json")
def parse_json(json_string: str) -> Any:
    """Parse a JSON string and return as Lua table."""
    try:
        data = json.loads(json_string)
        return python_to_lua_table(data)
    except Exception as e:
        error_result = {"error": f"JSON parse error: {e}"}
        return python_to_lua_table(error_result)


@export_to_lua("to_json")
def to_json(lua_data: Any) -> str:
    """Convert data to flat JSON string."""
    try:
        # Convert Lua data to Python data structures first
        python_data = lua_to_python_table(lua_data)
        return json.dumps(python_data, ensure_ascii=False, separators=(",", ":"))
    except Exception as e:
        return f'{{"error": "JSON encode error: {e}"}}'


@export_to_lua("to_json_formatted")
def to_json_formatted(lua_data: Any) -> str:
    """Convert data to JSON string."""
    try:
        # Convert Lua data to Python data structures first
        python_data = lua_to_python_table(lua_data)
        return json.dumps(python_data, ensure_ascii=False, indent=2)
    except Exception as e:
        return f'{{"error": "JSON encode error: {e}"}}'


@export_to_lua("get_env")
def get_env(var_name: str, default: str = "") -> str:
    """Get environment variable."""
    return os.environ.get(var_name, default)


@export_to_lua("set_env")
def set_env(var_name: str, value: str) -> bool:
    """Set environment variable."""
    try:
        os.environ[var_name] = value
        return True
    except Exception:
        return False


# =============================================================================
# BROWSER WINDOW MANAGEMENT
# External browser-based UI system replacing old Tkinter GUI
# =============================================================================

@export_to_lua("get_html_engine")
def get_html_engine() -> str:
    """Get the name of the HTML rendering engine."""
    return "browser"


# Primary Browser Window Functions
@export_to_lua("create_browser_window")
def create_browser_window(window_id: str, url: str, width: int = 800, height: int = 600,
                          x: int = 100, y: int = 100) -> bool:
    """Create a new browser window with full control over position and size."""
    try:
        return window_manager.create_window(window_id, url, width, height, x, y)
    except Exception as e:
        logging.error(f"Error creating browser window: {e}")
        return False


@export_to_lua("close_browser_window")
def close_browser_window(window_id: str) -> bool:
    """Close a browser window."""
    try:
        return window_manager.close_window(window_id)
    except Exception as e:
        logging.error(f"Error closing browser window: {e}")
        return False


@export_to_lua("set_browser_window_url")
def set_browser_window_url(window_id: str, url: str) -> bool:
    """Set the URL of a browser window."""
    try:
        return window_manager.set_window_url(window_id, url)
    except Exception as e:
        logging.error(f"Error setting browser window URL: {e}")
        return False


@export_to_lua("set_window_background")
def set_window_background(window_id: str, color: str) -> bool:
    """
    Set the background color of a QuickApp window's UI tab.
    
    Args:
        window_id: Window ID (e.g., "quickapp_5555")
        color: CSS color value - web color name ("red", "blue") or RGB string ("255,100,50")
        
    Returns:
        True if the background was set successfully, False otherwise
    """
    try:
        # Parse color input
        css_color = color.strip()
        
        # If it's an RGB string like "100,100,100", convert to rgb() format
        if ',' in css_color and css_color.replace(',', '').replace(' ', '').isdigit():
            rgb_parts = [part.strip() for part in css_color.split(',')]
            if len(rgb_parts) == 3:
                css_color = f"rgb({rgb_parts[0]}, {rgb_parts[1]}, {rgb_parts[2]})"
        
        # Use the window manager instance to inject CSS into the window
        # Strategy: Set the tab background and make UI elements semi-transparent
        # so the background color shows through
        manager = window_manager.get_window_manager()
        return manager.inject_css(window_id, f"""
            .tab-content.ui-tab {{
                background-color: {css_color} !important;
            }}
            .ui-element {{
                background-color: rgba(255,255,255,0.7) !important;
                border: 1px solid rgba(0,0,0,0.15) !important;
                backdrop-filter: blur(1px) !important;
            }}
            /* Also ensure the entire UI content area shows the background */
            #ui-content {{
                background-color: {css_color} !important;
            }}
        """)
    except Exception as e:
        logging.error(f"Error setting window background: {e}")
        return False


@export_to_lua("get_browser_window_info")
def get_browser_window_info(window_id: str) -> Any:
    """Get information about a browser window."""
    try:
        info = window_manager.get_window_info(window_id)
        return python_to_lua_table(info) if info else None
    except Exception as e:
        logging.error(f"Error getting browser window info: {e}")
        return None


@export_to_lua("list_browser_windows")
def list_browser_windows() -> Any:
    """List all browser windows."""
    try:
        windows = window_manager.list_windows()
        return python_to_lua_table(windows)
    except Exception as e:
        logging.error(f"Error listing browser windows: {e}")
        return python_to_lua_table({"error": str(e)})


@export_to_lua("close_all_browser_windows")
def close_all_browser_windows() -> bool:
    """Close all browser windows."""
    try:
        window_manager.close_all_windows()
        return True
    except Exception as e:
        logging.error(f"Error closing all browser windows: {e}")
        return False


# =============================================================================
# QUICKAPP-SPECIFIC FUNCTIONS
# Screen dimension, QuickApp window management, and WebSocket broadcasting
# =============================================================================

@export_to_lua("get_screen_dimensions")
def get_screen_dimensions() -> Any:
    """Get screen dimensions for window placement."""
    try:
        import platform
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            try:
                import subprocess
                result = subprocess.run([
                    "system_profiler", "SPDisplaysDataType", "-json"
                ], capture_output=True, text=True, check=True)
                
                import json
                displays = json.loads(result.stdout)
                
                # Get primary display info
                primary_display = displays.get("SPDisplaysDataType", [{}])[0]
                resolution = primary_display.get("_spdisplays_resolution", "1920 x 1080")
                width, height = resolution.split(" x ")
                
                return python_to_lua_table({
                    "width": int(width),
                    "height": int(height),
                    "primary": True
                })
            except Exception:
                # Fallback for macOS
                return python_to_lua_table({"width": 1920, "height": 1080, "primary": True})
                
        elif system == "linux":
            try:
                import subprocess
                result = subprocess.run([
                    "xrandr", "--query"
                ], capture_output=True, text=True, check=True)
                
                for line in result.stdout.split('\n'):
                    if " connected primary " in line and " x " in line:
                        parts = line.split()
                        for part in parts:
                            if "x" in part and part.replace("x", "").replace("+", "").replace("-", "").isdigit():
                                resolution = part.split("+")[0]  # Remove position info
                                width, height = resolution.split("x")
                                return python_to_lua_table({
                                    "width": int(width),
                                    "height": int(height),
                                    "primary": True
                                })
                # Fallback for Linux
                return python_to_lua_table({"width": 1920, "height": 1080, "primary": True})
            except Exception:
                return python_to_lua_table({"width": 1920, "height": 1080, "primary": True})
                
        elif system == "windows":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                width = user32.GetSystemMetrics(0)
                height = user32.GetSystemMetrics(1)
                
                return python_to_lua_table({
                    "width": width,
                    "height": height,
                    "primary": True
                })
            except Exception:
                # Fallback for Windows
                return python_to_lua_table({"width": 1920, "height": 1080, "primary": True})
        else:
            # Unknown system fallback
            return python_to_lua_table({"width": 1920, "height": 1080, "primary": True})
            
    except Exception as e:
        logging.error(f"Error getting screen dimensions: {e}")
        return python_to_lua_table({"width": 1920, "height": 1080, "primary": True})


@export_to_lua("open_quickapp_window")
def open_quickapp_window(qa_id: int, title: str, width: int = 800, height: int = 600, 
                        pos_x: int = 100, pos_y: int = 100, background_color: str = "") -> bool:
    """
    Open a QuickApp window using the /plua/quickApp/<id>/info endpoint.
    
    Args:
        qa_id: QuickApp ID
        title: Window title
        width: Window width in pixels (default: 800)
        height: Window height in pixels (default: 600)
        pos_x: Window x position (default: 100)
        pos_y: Window y position (default: 100)
        background_color: Background color for the UI tab (default: "")
        
    Returns:
        True if window was created successfully, False otherwise
    """
    try:
        # Get the engine to determine the web server port
        engine = get_global_engine()
        if not engine:
            logging.error("PLua engine not available for QuickApp window")
            return False
            
        # Try to get the server port from the engine config
        api_server = getattr(engine, 'api_server', None)
        if api_server and hasattr(api_server, 'port'):
            server_port = api_server.port
        else:
            # Fallback to default port used by FastAPI
            server_port = 8080
            
        # Construct the URL for the QuickApp UI
        base_url = f"http://localhost:{server_port}"
        static_url = f"{base_url}/static/quickapp_ui.html?qa_id={qa_id}&desktop=true"
        
        # Add background color parameter if provided
        if background_color:
            # URL encode the color parameter
            import urllib.parse
            encoded_color = urllib.parse.quote(background_color)
            static_url += f"&bg_color={encoded_color}"
        
        # Use the existing window manager to create the browser window
        window_id = f"quickapp_{qa_id}"
        
        success = window_manager.create_window(
            window_id=window_id,
            url=static_url,
            width=width,
            height=height,
            x=pos_x,
            y=pos_y
        )
        
        if success:
            logging.info(f"Created QuickApp window for QA {qa_id}: {title}")
            
            # Schedule a UI refresh after the window has had time to load
            # This ensures the window shows the latest UI state even if it opened in the background
            import asyncio
            async def refresh_window_ui():
                await asyncio.sleep(1.5)  # Wait for window to load and WebSocket to connect
                try:
                    # Method 1: Try to get QuickApp data from Fibaro manager
                    qa_data = None
                    if hasattr(engine, 'fibaro_manager') and engine.fibaro_manager:
                        qa_data = engine.fibaro_manager.get_quickapp_info(qa_id)
                    
                    # Method 2: Try to get data via the FastAPI process manager
                    if not qa_data:
                        from . import fastapi_process
                        process_manager = fastapi_process.get_process_manager()
                        if process_manager and process_manager.quickapp_callback:
                            try:
                                # DISABLED: This direct callback was causing 30-second delays in UI callbacks
                                # by blocking the IPC message processing thread
                                # qa_data = process_manager.quickapp_callback("get_quickapp", qa_id)
                                logging.debug("Skipping direct quickapp_callback to avoid IPC blocking")
                            except Exception as e:
                                logging.debug(f"FastAPI process manager quickapp callback failed: {e}")
                    
                    if qa_data and 'UI' in qa_data:
                        # Broadcast a refresh for each UI element to force update
                        refresh_count = 0
                        for ui_row in qa_data['UI']:
                            if isinstance(ui_row, list):
                                # Multiple elements in one row
                                for element in ui_row:
                                    if isinstance(element, dict) and 'id' in element:
                                        element_id = element['id']
                                        # Broadcast current values for key properties
                                        for prop_name in ['text', 'value', 'visible']:
                                            if prop_name in element:
                                                broadcast_view_update(qa_id, element_id, prop_name, element[prop_name])
                                                refresh_count += 1
                            elif isinstance(ui_row, dict) and 'id' in ui_row:
                                # Single element
                                element_id = ui_row['id']
                                # Broadcast current values for key properties
                                for prop_name in ['text', 'value', 'visible']:
                                    if prop_name in ui_row:
                                        broadcast_view_update(qa_id, element_id, prop_name, ui_row[prop_name])
                                        refresh_count += 1
                        
                        logging.info(f"Triggered {refresh_count} UI property refreshes for newly opened QuickApp {qa_id}")
                    else:
                        # Fallback: Send a generic refresh signal
                        logging.debug(f"No UI data found for QuickApp {qa_id}, sending generic refresh")
                        # Send a dummy update to trigger WebSocket activity
                        broadcast_view_update(qa_id, "refresh_trigger", "timestamp", str(int(time.time())))
                        
                except Exception as e:
                    logging.warning(f"Failed to refresh UI for QuickApp {qa_id}: {e}")
            
            # Schedule the refresh
            asyncio.create_task(refresh_window_ui())
        else:
            logging.error(f"Failed to create QuickApp window for QA {qa_id}")
            
        return success
        
    except Exception as e:
        logging.error(f"Error opening QuickApp window for QA {qa_id}: {e}")
        return False


@export_to_lua("broadcast_view_update")
def broadcast_view_update(qa_id: int, element_id: str, property_name: str, value: Any) -> bool:
    """
    Broadcast a view update to all connected WebSocket clients.
    
    Args:
        qa_id: QuickApp ID
        element_id: UI element ID that was updated
        property_name: Property that changed (e.g., "text", "value")
        value: The new value for the property
        
    Returns:
        True if broadcast was successful, False otherwise
    """
    try:
        # Get the engine
        engine = get_global_engine()
        if not engine:
            logging.debug("PLua engine not available for broadcast")
            return True  # Don't fail, just skip broadcasting
        
        # Convert LuaTable values to Python objects to avoid multiprocessing pickle errors
        if hasattr(value, '__class__') and 'LuaTable' in str(value.__class__):
            # Convert LuaTable to Python dict
            from .lua_bindings import lua_to_python_table
            value = lua_to_python_table(value)
        
        # Check if API manager is available (multi-process mode)
        api_manager = getattr(engine, '_api_manager', None)
        if api_manager:
            # Use the API manager to send broadcast request to FastAPI process
            try:
                logging.info(f"🔄 Using API manager for broadcast: QA {qa_id}, {element_id}.{property_name} = {value}")
                result = api_manager.broadcast_view_update(qa_id, element_id, property_name, value)
                logging.info(f"📡 API manager broadcast result: {result}")
                return result
            except Exception as e:
                logging.warning(f"API manager broadcast failed: {e}")
                return True  # Don't fail QuickApp logic
        
        # Fallback: try direct API server access (single-process mode)
        api_server = getattr(engine, 'api_server', None)
        if api_server and hasattr(api_server, 'broadcast_view_update'):
            try:
                import asyncio
                
                async def do_broadcast():
                    await api_server.broadcast_view_update(qa_id, element_id, property_name, value)
                
                # Try to run the async broadcast
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(do_broadcast())
                    else:
                        loop.run_until_complete(do_broadcast())
                except RuntimeError:
                    asyncio.run(do_broadcast())
                
                logging.debug(f"Direct WebSocket broadcast successful: QA {qa_id}, element {element_id}")
                return True
                
            except Exception as e:
                logging.debug(f"Direct broadcast failed: {e}")
                return True  # Don't fail QuickApp logic
        
        # No broadcast mechanism available - log and continue
        logging.debug(f"No WebSocket broadcast available, skipping: QA {qa_id}, element {element_id}")
        return True
        
    except Exception as e:
        logging.debug(f"Error in broadcast_view_update: {e}")
        return True  # Don't fail the QuickApp logic due to broadcast issues





