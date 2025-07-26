"""
Desktop UI for QuickApp panels using pywebview to embed the existing web UI
"""

import threading
import time
import json
from typing import Dict, Optional, Any
import requests
from urllib.parse import urljoin

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    webview = None


class DesktopUIManager:
    """Manages desktop windows for QuickApp UIs"""
    
    def __init__(self, api_base_url: str = "http://localhost:8888"):
        self.api_base_url = api_base_url
        self.windows: Dict[str, Any] = {}  # window_id -> webview window
        self.window_threads: Dict[str, threading.Thread] = {}
        self._running = False
        self._webview_started = False
        
    def start(self):
        """Start the desktop UI manager"""
        if not WEBVIEW_AVAILABLE:
            raise RuntimeError("pywebview not available. Install with: pip install pywebview")
        
        self._running = True
        print("Desktop UI Manager started")
        
    def stop(self):
        """Stop the desktop UI manager and close all windows"""
        self._running = False
        
        # Close all windows
        for window_id in list(self.windows.keys()):
            self.close_window(window_id)
            
        print("Desktop UI Manager stopped")
    
    def create_quickapp_window(self, qa_id: int, title: str = None, width: int = 800, height: int = 600) -> str:
        """
        Create a new desktop window for a QuickApp
        
        Args:
            qa_id: QuickApp ID
            title: Window title (defaults to "QuickApp {qa_id}")
            width: Window width
            height: Window height
            
        Returns:
            window_id: Unique identifier for the created window
        """
        if not WEBVIEW_AVAILABLE:
            print("Warning: pywebview not available. Install with: pip install pywebview")
            # Fallback to browser tab
            return self._fallback_browser_open(qa_id, title, width, height)
            
        window_id = f"qa_{qa_id}_{int(time.time())}"
        if title is None:
            title = f"QuickApp {qa_id}"
            
        # Construct URL for the QuickApp UI
        browser_url = self.api_base_url.replace("0.0.0.0", "localhost")
        url = f"{browser_url}/static/quickapp_ui.html?qa_id={qa_id}&desktop=true"
        
        # Try to create a desktop window using a subprocess approach
        # This avoids the main thread requirement by running webview in a separate process
        try:
            import subprocess
            import sys
            import tempfile
            import os
            
            # Create a simple webview script
            webview_script = f'''
import webview
import sys
import signal

def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    # Create and start the webview window
    window = webview.create_window(
        title="{title}",
        url="{url}",
        width={width},
        height={height},
        resizable=True,
        on_top=False
    )
    
    print("Webview window created: {window_id}")
    webview.start(debug=False)
    
except Exception as e:
    print(f"Webview error: {{e}}")
    sys.exit(1)
'''
            
            # Write the script to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(webview_script)
                temp_script = f.name
            
            # Start the webview process
            process = subprocess.Popen(
                [sys.executable, temp_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0
            )
            
            # Store the window info
            self.windows[window_id] = {
                "process": process,
                "temp_script": temp_script,
                "url": url,
                "qa_id": qa_id,
                "title": title,
                "type": "webview_process",
                "pid": process.pid  # Store PID for external closure
            }
            
            print(f"Created QuickApp desktop window: {window_id} for QA {qa_id}")
            print(f"Window process PID: {process.pid}")
            
            # Clean up the temp file after a delay
            def cleanup_temp_file():
                try:
                    if os.path.exists(temp_script):
                        os.unlink(temp_script)
                except:
                    pass
            
            threading.Timer(10.0, cleanup_temp_file).start()
            
            return window_id
            
        except Exception as e:
            print(f"Error creating desktop window {window_id}: {e}")
            # Fallback to browser tab
            return self._fallback_browser_open(qa_id, title, width, height)
    
    def _fallback_browser_open(self, qa_id: int, title: str = None, width: int = 800, height: int = 600) -> str:
        """Fallback method to open in browser tab if webview fails"""
        window_id = f"qa_{qa_id}_{int(time.time())}_browser"
        if title is None:
            title = f"QuickApp {qa_id}"
            
        browser_url = self.api_base_url.replace("0.0.0.0", "localhost")
        url = f"{browser_url}/static/quickapp_ui.html?qa_id={qa_id}&desktop=true"
        
        try:
            import webbrowser
            webbrowser.open_new_tab(url)
            
            # Store a placeholder for the window
            self.windows[window_id] = {"url": url, "qa_id": qa_id, "title": title, "type": "browser"}
            
            print(f"Fallback: Opened QuickApp {qa_id} in browser tab: {url}")
            print(f"Created window reference: {window_id}")
            
        except Exception as e:
            print(f"Error opening QuickApp window {window_id}: {e}")
            return None
            
        return window_id
    
    def close_window(self, window_id: str) -> bool:
        """
        Close a specific QuickApp window
        
        Args:
            window_id: Window identifier returned by create_quickapp_window
            
        Returns:
            True if window was closed, False if not found
        """
        if window_id not in self.windows:
            return False
            
        try:
            window_info = self.windows[window_id]
            
            # Handle different window types
            if isinstance(window_info, dict):
                if window_info.get("type") == "webview_process":
                    # Close process-based webview window
                    process = window_info.get("process")
                    if process and process.poll() is None:  # Process is still running
                        try:
                            process.terminate()
                            # Give it a moment to terminate gracefully
                            import time
                            time.sleep(0.5)
                            if process.poll() is None:
                                process.kill()  # Force kill if still running
                        except:
                            pass
                    
                    # Clean up temp script
                    temp_script = window_info.get("temp_script")
                    if temp_script:
                        try:
                            import os
                            if os.path.exists(temp_script):
                                os.unlink(temp_script)
                        except:
                            pass
                            
                elif window_info.get("type") == "browser":
                    # Browser windows can't be closed programmatically
                    print(f"Browser window {window_id} noted as closed (browser manages actual closure)")
                    
                # Remove from registry and log closure
                del self.windows[window_id]
                self._log_window_closure(window_id)
                return True
                
            else:
                # Old-style webview object
                window_info.destroy()
                del self.windows[window_id]
                self._log_window_closure(window_id)
                return True
                
        except Exception as e:
            print(f"Error closing window {window_id}: {e}")
            return False
        
        return False
    
    def _log_window_closure(self, window_id: str):
        """Log window closure to registry"""
        try:
            import json
            import time
            from pathlib import Path
            
            registry_dir = Path.home() / ".plua"
            registry_file = registry_dir / "registry.json"
            
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    registry = json.load(f)
                
                if "windows" in registry and window_id in registry["windows"]:
                    registry["windows"][window_id]["status"] = "closed"
                    registry["windows"][window_id]["closed"] = time.time()
                    registry["windows"][window_id]["closed_iso"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    
                    with open(registry_file, 'w') as f:
                        json.dump(registry, f, indent=2)
                    
                    print(f"Window {window_id} marked as closed in registry")
        except Exception as e:
            print(f"Warning: Failed to log window closure: {e}")
    
    def list_windows(self) -> Dict[str, Dict[str, Any]]:
        """List all open QuickApp windows"""
        result = {}
        for window_id, window in self.windows.items():
            result[window_id] = {
                'title': getattr(window, 'title', 'Unknown'),
                'url': getattr(window, 'url', 'Unknown')
            }
        return result
    
    def send_to_window(self, window_id: str, event_type: str, data: Any) -> bool:
        """
        Send data to a specific QuickApp window
        
        Args:
            window_id: Target window
            event_type: Type of event (e.g., 'ui_update', 'device_event')
            data: Event data
            
        Returns:
            True if message was sent, False if window not found
        """
        if window_id not in self.windows:
            return False
            
        try:
            window = self.windows[window_id]
            # Send JavaScript to the embedded web page
            js_code = f"""
            if (window.handleDesktopEvent) {{
                window.handleDesktopEvent({json.dumps(event_type)}, {json.dumps(data)});
            }}
            """
            window.evaluate_js(js_code)
            return True
        except Exception as e:
            print(f"Error sending to window {window_id}: {e}")
            return False
    
    def broadcast_to_all(self, event_type: str, data: Any):
        """Broadcast an event to all open QuickApp windows"""
        for window_id in list(self.windows.keys()):
            self.send_to_window(window_id, event_type, data)
    
    def broadcast_qa_update(self, qa_id: int, component_name: str, property_name: str, value: Any):
        """
        Broadcast QuickApp UI update to relevant desktop windows
        This integrates with the existing _PY.broadcast_view_update mechanism
        """
        # Find windows for this specific QuickApp
        qa_windows = []
        for window_id, window in self.windows.items():
            # Extract QA ID from window_id (format: qa_{qa_id}_{timestamp})
            if window_id.startswith(f"qa_{qa_id}_"):
                qa_windows.append(window_id)
        
        if not qa_windows:
            return  # No desktop windows for this QuickApp
        
        # Send update to all windows for this QuickApp
        update_data = {
            "element_id": component_name,
            "property": property_name,
            "value": value
        }
        
        for window_id in qa_windows:
            self.send_to_window(window_id, "ui_update", update_data)
        
        print(f"Desktop UI: Updated {len(qa_windows)} windows for QA {qa_id}: {component_name}.{property_name} = {value}")

    def create_quickapp_window_direct(self, qa_id: int, title: str = None, width: int = 800, height: int = 600) -> str:
        """
        Direct method to create QuickApp window (called from Lua via _PY table)
        This replaces the HTTP endpoint approach
        """
        try:
            return self.create_quickapp_window(qa_id, title, width, height)
        except Exception as e:
            print(f"Failed to create desktop window for QA {qa_id}: {e}")
            return None


# Global instance (will be created by CLI when needed)
desktop_manager: Optional[DesktopUIManager] = None


def get_desktop_manager() -> Optional[DesktopUIManager]:
    """Get the global desktop UI manager instance"""
    return desktop_manager


def initialize_desktop_ui(api_base_url: str = "http://localhost:8888") -> DesktopUIManager:
    """Initialize the global desktop UI manager"""
    global desktop_manager
    if desktop_manager is None:
        desktop_manager = DesktopUIManager(api_base_url)
        desktop_manager.start()
    return desktop_manager


def shutdown_desktop_ui():
    """Shutdown the global desktop UI manager"""
    global desktop_manager
    if desktop_manager:
        desktop_manager.stop()
        desktop_manager = None


# API integration functions for the REST server
def create_quickapp_window_api(qa_id: int, title: str = None, width: int = 800, height: int = 600) -> dict:
    """API function to create a QuickApp window"""
    manager = get_desktop_manager()
    if not manager:
        return {"error": "Desktop UI not initialized"}
    
    try:
        window_id = manager.create_quickapp_window(qa_id, title, width, height)
        return {
            "success": True,
            "window_id": window_id,
            "qa_id": qa_id,
            "title": title or f"QuickApp {qa_id}"
        }
    except Exception as e:
        return {"error": str(e)}


def close_quickapp_window_api(window_id: str) -> dict:
    """API function to close a QuickApp window"""
    manager = get_desktop_manager()
    if not manager:
        return {"error": "Desktop UI not initialized"}
    
    success = manager.close_window(window_id)
    return {"success": success}


def list_quickapp_windows_api() -> dict:
    """API function to list all QuickApp windows"""
    manager = get_desktop_manager()
    if not manager:
        return {"error": "Desktop UI not initialized"}
    
    windows = manager.list_windows()
    return {"windows": windows}


def send_to_quickapp_window_api(window_id: str, event_type: str, data: Any) -> dict:
    """API function to send data to a QuickApp window"""
    manager = get_desktop_manager()
    if not manager:
        return {"error": "Desktop UI not initialized"}
    
    success = manager.send_to_window(window_id, event_type, data)
    return {"success": success}
