#!/usr/bin/env python3
"""
EPLua GUI-First Launcher

This launcher runs tkinter in the main thread (required on macOS) and EPLua engine
in a worker thread, with thread-safe communication for window operations.
"""

import sys
import os
import asyncio
import threading
import queue
import time
from typing import Any, Dict, Optional
import logging

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Check if GUI is available
try:
    import tkinter as tk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

logger = logging.getLogger(__name__)


class ThreadSafeGUIBridge:
    """Bridge for thread-safe communication between EPLua engine and GUI"""
    
    def __init__(self):
        self.command_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.gui_thread = None
        self.engine_thread = None
        self.running = False
        
    def send_gui_command(self, command: str, **kwargs) -> Any:
        """Send a command to the GUI thread and wait for result"""
        if not self.running:
            return "ERROR: GUI bridge not running"
        
        # Create a unique command ID
        cmd_id = f"cmd_{time.time()}"
        cmd_data = {
            'id': cmd_id,
            'command': command,
            'args': kwargs
        }
        
        # Send command to GUI thread
        self.command_queue.put(cmd_data)
        
        # Wait for result (with timeout)
        timeout = 10  # 10 second timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = self.result_queue.get(timeout=0.1)
                if result.get('id') == cmd_id:
                    return result.get('result', 'No result')
            except queue.Empty:
                continue
        
        return "ERROR: GUI command timeout"
    
    def start(self):
        """Start the bridge"""
        self.running = True
    
    def stop(self):
        """Stop the bridge"""
        self.running = False


# Global bridge instance
gui_bridge = ThreadSafeGUIBridge()


class GUIManager:
    """Manages the GUI in the main thread"""
    
    def __init__(self, bridge: ThreadSafeGUIBridge):
        self.bridge = bridge
        self.root = None
        self.windows = {}
        
    def start_gui_loop(self):
        """Start the GUI event loop in main thread"""
        if not GUI_AVAILABLE:
            print("❌ GUI not available - running in CLI mode")
            return
        
        print("🖥️  Starting GUI in main thread...")
        
        # Initialize tkinter
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
        self.root.title("EPLua GUI Manager")
        
        # Process GUI commands
        self.root.after(100, self._process_commands)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("🧹 GUI shutting down...")
        finally:
            self.bridge.stop()
    
    def _process_commands(self):
        """Process commands from the engine thread"""
        if not self.bridge.running:
            return
        
        try:
            # Process all pending commands
            while True:
                try:
                    cmd_data = self.bridge.command_queue.get_nowait()
                    result = self._execute_command(cmd_data)
                    
                    # Send result back
                    self.bridge.result_queue.put({
                        'id': cmd_data['id'],
                        'result': result
                    })
                except queue.Empty:
                    break
        except Exception as e:
            logger.error(f"Error processing GUI commands: {e}")
        
        # Schedule next check
        if self.bridge.running:
            self.root.after(50, self._process_commands)
    
    def _execute_command(self, cmd_data: Dict[str, Any]) -> Any:
        """Execute a GUI command"""
        command = cmd_data['command']
        args = cmd_data['args']
        
        try:
            if command == 'create_window':
                return self._create_window(**args)
            elif command == 'set_window_html':
                return self._set_window_html(**args)
            elif command == 'show_window':
                return self._show_window(**args)
            elif command == 'hide_window':
                return self._hide_window(**args)
            elif command == 'close_window':
                return self._close_window(**args)
            elif command == 'list_windows':
                return self._list_windows()
            elif command == 'gui_available':
                return True
            elif command == 'html_rendering_available':
                return self._html_rendering_available()
            elif command == 'get_html_engine':
                return self._get_html_engine()
            else:
                return f"ERROR: Unknown command: {command}"
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return f"ERROR: {e}"
    
    def _create_window(self, title: str, width: int = 800, height: int = 600) -> str:
        """Create a new window"""
        try:
            from plua.gui import HTMLWindow
            import uuid
            
            window_id = str(uuid.uuid4())
            window = HTMLWindow(window_id, title, width, height)
            window.create()
            
            self.windows[window_id] = window
            logger.info(f"Created window '{title}' with ID {window_id}")
            return window_id
        except Exception as e:
            error_msg = f"ERROR: Failed to create window: {e}"
            logger.error(error_msg)
            return error_msg
    
    def _set_window_html(self, window_id: str, html_content: str) -> str:
        """Set HTML content for a window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.set_html(html_content)
            return "SUCCESS: HTML content set"
        except Exception as e:
            error_msg = f"ERROR: Failed to set HTML content: {e}"
            logger.error(error_msg)
            return error_msg
    
    def _show_window(self, window_id: str) -> str:
        """Show a window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.show()
            return "SUCCESS: Window shown"
        except Exception as e:
            error_msg = f"ERROR: Failed to show window: {e}"
            logger.error(error_msg)
            return error_msg
    
    def _hide_window(self, window_id: str) -> str:
        """Hide a window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.hide()
            return "SUCCESS: Window hidden"
        except Exception as e:
            error_msg = f"ERROR: Failed to hide window: {e}"
            logger.error(error_msg)
            return error_msg
    
    def _close_window(self, window_id: str) -> str:
        """Close and destroy a window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.close()
            del self.windows[window_id]
            return "SUCCESS: Window closed"
        except Exception as e:
            error_msg = f"ERROR: Failed to close window: {e}"
            logger.error(error_msg)
            return error_msg
    
    def _list_windows(self) -> str:
        """List all open windows"""
        if not self.windows:
            return "No windows open"
        
        windows_info = []
        for window_id, window in self.windows.items():
            status = "created" if window.created else "not created"
            windows_info.append(f"  {window_id}: '{window.title}' ({status})")
        
        return f"Open windows ({len(self.windows)}):\n" + "\n".join(windows_info)
    
    def _html_rendering_available(self) -> bool:
        """Check if HTML rendering is available"""
        try:
            from plua.gui import HTML_RENDERING_AVAILABLE
            return HTML_RENDERING_AVAILABLE
        except:
            return False
    
    def _get_html_engine(self) -> str:
        """Get HTML engine name"""
        try:
            from plua.gui import HTML_ENGINE
            return HTML_ENGINE
        except:
            return "none"


def run_eplua_engine(script_path: str, bridge: ThreadSafeGUIBridge):
    """Run EPLua engine in worker thread"""
    async def engine_main():
        from plua.engine import LuaEngine
        
        print(f"🚀 Starting EPLua engine in worker thread...")
        print(f"📄 Script: {script_path}")
        
        try:
            async with LuaEngine() as engine:
                # Replace GUI functions with bridge versions
                _replace_gui_functions_with_bridge(engine, bridge)
                
                print(f"⚙️  Running script: {script_path}")
                await engine.run_script(f'_PY.mainLuaFile("{script_path}")', script_path)
                
                # Keep running while there are active operations
                print("⏳ Monitoring for active operations...")
                while engine.has_active_operations() and engine.is_running():
                    await asyncio.sleep(0.1)
                
                print("✅ EPLua engine completed")
                
        except Exception as e:
            print(f"❌ EPLua engine error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Signal GUI to close
            if bridge.running:
                bridge.stop()
    
    # Run the async engine
    asyncio.run(engine_main())


def _replace_gui_functions_with_bridge(engine, bridge: ThreadSafeGUIBridge):
    """Replace GUI functions in the engine with bridge versions"""
    
    # Thread-safe GUI function wrappers
    def gui_available() -> bool:
        if not GUI_AVAILABLE:
            return False
        return bridge.send_gui_command('gui_available')
    
    def html_rendering_available() -> bool:
        if not GUI_AVAILABLE:
            return False
        return bridge.send_gui_command('html_rendering_available')
    
    def get_html_engine() -> str:
        if not GUI_AVAILABLE:
            return "none"
        return bridge.send_gui_command('get_html_engine')
    
    def create_window(title: str, width: int = 800, height: int = 600) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('create_window', title=title, width=width, height=height)
    
    def set_window_html(window_id: str, html_content: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('set_window_html', window_id=window_id, html_content=html_content)
    
    def show_window(window_id: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('show_window', window_id=window_id)
    
    def hide_window(window_id: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('hide_window', window_id=window_id)
    
    def close_window(window_id: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('close_window', window_id=window_id)
    
    def list_windows() -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('list_windows')
    
    # Replace the exported functions directly in the Lua environment
    # Access the _PY table through the engine's Lua globals
    py_table = engine.get_lua_global("_PY")
    py_table.gui_available = gui_available
    py_table.html_rendering_available = html_rendering_available
    py_table.get_html_engine = get_html_engine
    py_table.create_window = create_window
    py_table.set_window_html = set_window_html
    py_table.show_window = show_window
    py_table.hide_window = hide_window
    py_table.close_window = close_window
    py_table.list_windows = list_windows


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python eplua_gui_launcher.py <script.lua>")
        return 1
    
    script_path = sys.argv[1]
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return 1
    
    print("🎮 EPLua GUI-First Launcher")
    print("=" * 40)
    print(f"GUI Available: {GUI_AVAILABLE}")
    
    if GUI_AVAILABLE:
        print("🔧 Architecture: GUI in main thread, EPLua in worker thread")
        
        # Start the bridge
        gui_bridge.start()
        
        # Start EPLua engine in worker thread
        engine_thread = threading.Thread(
            target=run_eplua_engine,
            args=(script_path, gui_bridge),
            daemon=True
        )
        engine_thread.start()
        
        # Run GUI in main thread
        gui_manager = GUIManager(gui_bridge)
        gui_manager.start_gui_loop()
        
        # Wait for engine thread to complete
        engine_thread.join(timeout=1.0)
        
    else:
        print("🔧 Architecture: EPLua in main thread (no GUI)")
        
        # Run without GUI in main thread
        async def main_no_gui():
            from plua.engine import LuaEngine
            
            async with LuaEngine() as engine:
                await engine.run_script(f'_PY.mainLuaFile("{script_path}")', script_path)
                
                while engine.has_active_operations() and engine.is_running():
                    await asyncio.sleep(0.1)
        
        asyncio.run(main_no_gui())
    
    print("✅ EPLua GUI launcher completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
