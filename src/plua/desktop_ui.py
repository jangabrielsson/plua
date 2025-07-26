"""
Desktop UI for QuickApp panels using pywebview to embed the existing web UI
"""

import threading
import time
import json
from typing import Dict, Optional, Any
import requests
from urllib.parse import urljoin
from pathlib import Path

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    webview = None


class DesktopUIManager:
    """Manages desktop windows for QuickApp UIs with reuse and position persistence"""
    
    def __init__(self, api_base_url: str = "http://localhost:8888"):
        self.api_base_url = api_base_url
        self.windows: Dict[str, Any] = {}  # window_id -> webview window
        self.window_threads: Dict[str, threading.Thread] = {}
        self.qa_windows: Dict[int, str] = {}  # qa_id -> window_id mapping for reuse
        self._running = False
        self._webview_started = False
        self.registry_file = Path.home() / ".plua" / "window_registry.json"
        
        # Detect if we're running from terminal (should close windows) vs VS Code (survive)
        import sys
        self._is_terminal = sys.stdin.isatty()
        
        self._ensure_registry()
    def _ensure_registry(self):
        """Ensure the window registry directory and file exist"""
        try:
            self.registry_file.parent.mkdir(exist_ok=True)
            if not self.registry_file.exists():
                self._save_registry({"windows": {}, "positions": {}})
        except Exception as e:
            print(f"Warning: Failed to create window registry: {e}")
    
    def _load_registry(self) -> dict:
        """Load window registry from disk with error recovery"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Warning: Registry JSON corrupted ({e}), creating fresh registry")
            # Backup corrupted file and create fresh one
            try:
                backup_file = self.registry_file.with_suffix('.json.backup')
                self.registry_file.rename(backup_file)
                print(f"Corrupted registry backed up to {backup_file}")
            except Exception:
                pass
        except Exception as e:
            print(f"Warning: Failed to load window registry: {e}")
        return {"windows": {}, "positions": {}}
    
    def _save_registry(self, registry: dict):
        """Save window registry to disk atomically with robust cross-platform file locking"""
        import sys
        import tempfile
        import time
        import random
        import os
        
        max_retries = 5
        base_delay = 0.01  # 10ms base delay
        
        for attempt in range(max_retries):
            try:
                # Use unique temp file names to avoid conflicts
                timestamp = int(time.time() * 1000000)  # microseconds
                random_suffix = random.randint(1000, 9999)
                temp_file = self.registry_file.with_suffix(f'.json.tmp.{timestamp}.{random_suffix}')
                
                # Direct file locking on the registry file itself
                lock_acquired = False
                lock_fd = None
                
                try:
                    # Try to acquire exclusive lock on registry file
                    lock_fd = open(self.registry_file.with_suffix('.lockfile'), 'w')
                    
                    # Cross-platform file locking with timeout
                    if sys.platform.startswith('win'):
                        # Windows: Use msvcrt for file locking
                        import msvcrt
                        for lock_attempt in range(10):  # 100ms timeout
                            try:
                                msvcrt.locking(lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
                                lock_acquired = True
                                break
                            except OSError:
                                time.sleep(0.01)  # Wait 10ms
                    else:
                        # Unix/Linux/macOS: Use fcntl with timeout
                        import fcntl
                        for lock_attempt in range(10):  # 100ms timeout
                            try:
                                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                                lock_acquired = True
                                break
                            except (OSError, IOError):
                                time.sleep(0.01)  # Wait 10ms
                    
                    if not lock_acquired:
                        raise Exception(f"Could not acquire lock after timeout (attempt {attempt + 1})")
                    
                    # Write to temporary file first
                    with open(temp_file, 'w') as f:
                        json.dump(registry, f, indent=2)
                        f.write('\n')  # Ensure newline at end
                        f.flush()  # Ensure data is written
                        os.fsync(f.fileno())  # Force to disk using os.fsync
                    
                    # Atomic rename (Windows requires removing target file first)
                    if sys.platform.startswith('win') and self.registry_file.exists():
                        self.registry_file.unlink()  # Remove existing file on Windows
                    temp_file.rename(self.registry_file)
                    
                    # Success - exit retry loop
                    return
                    
                finally:
                    # Always unlock and clean up
                    if lock_acquired and lock_fd:
                        try:
                            if sys.platform.startswith('win'):
                                import msvcrt
                                msvcrt.locking(lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                            # fcntl locks are automatically released when file is closed
                        except Exception:
                            pass
                    
                    if lock_fd:
                        try:
                            lock_fd.close()
                        except Exception:
                            pass
                    
                    # Clean up temp file if it exists
                    try:
                        if temp_file.exists():
                            temp_file.unlink()
                    except Exception:
                        pass
                    
                    # Clean up lock file
                    try:
                        lock_file = self.registry_file.with_suffix('.lockfile')
                        if lock_file.exists():
                            lock_file.unlink()
                    except Exception:
                        pass
                        
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Warning: Failed to save window registry after {max_retries} attempts: {e}")
                    return
                else:
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.01)
                    time.sleep(delay)
    
    def _get_qa_key(self, qa_id: int, title: str = None, qa_type: str = "quickapp") -> str:
        """Generate a stable key for QuickApp identification"""
        if title is None:
            title = f"QuickApp {qa_id}"
        return f"{qa_type}_{qa_id}_{title}"
    
    def _save_window_position(self, qa_key: str, x: int, y: int, width: int, height: int):
        """Save window position to registry"""
        registry = self._load_registry()
        registry["positions"][qa_key] = {
            "x": x, "y": y, "width": width, "height": height,
            "timestamp": time.time(),
            "updated": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        self._save_registry(registry)
    
    def _get_saved_position(self, qa_key: str) -> Optional[Dict[str, int]]:
        """Get saved window position from registry"""
        registry = self._load_registry()
        return registry.get("positions", {}).get(qa_key)
    
    def _find_existing_qa_window(self, qa_id: int) -> Optional[str]:
        """
        Find existing window for QA ID by checking registry and verifying process is alive
        This handles the VS Code kill -9 scenario where windows survive but in-memory state is lost
        """
        try:
            registry = self._load_registry()
            
            # Look through registry for windows matching this QA ID
            for window_id, window_info in registry.get("windows", {}).items():
                if isinstance(window_info, dict) and window_info.get("qa_id") == qa_id:
                    # Check if this window process is still alive
                    pid = window_info.get("pid")
                    if pid and self._is_process_alive(pid):
                        # Reconnect to this existing window
                        self.windows[window_id] = {
                            "qa_id": qa_id,
                            "title": window_info.get("title", f"QuickApp {qa_id}"),
                            "type": "webview_process",
                            "pid": pid,
                            "reconnected": True  # Mark as reconnected
                        }
                        self.qa_windows[qa_id] = window_id
                        return window_id
                        
            return None
        except Exception as e:
            print(f"Warning: Failed to find existing QA window: {e}")
            return None
    
    def _is_process_alive(self, pid: int) -> bool:
        """Check if a process with given PID is still running"""
        try:
            import os
            import signal
            # Send signal 0 to check if process exists (doesn't actually send a signal)
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
        
    def start(self):
        """Start the desktop UI manager"""
        if not WEBVIEW_AVAILABLE:
            raise RuntimeError("pywebview not available. Install with: pip install pywebview")
        
        self._running = True
        print("Desktop UI Manager started")
        
    def stop(self):
        """Stop the desktop UI manager and optionally close windows based on context"""
        self._running = False
        
        # Only close windows if we're running from terminal
        # VS Code scenarios should leave windows open for reuse
        if self._is_terminal:
            # Terminal usage - close all windows
            for window_id in list(self.windows.keys()):
                self.close_window(window_id)
            print("Desktop UI Manager stopped - closed all windows")
        else:
            # VS Code/non-terminal usage - leave windows open for reuse
            # Just mark them as orphaned in registry but don't kill processes
            for window_id, window_info in self.windows.items():
                if isinstance(window_info, dict):
                    window_info["orphaned"] = True
            print("Desktop UI Manager stopped - windows left open for reuse")
            
        print("Desktop UI Manager stopped")
    
    def create_quickapp_window(self, qa_id: int, title: str = None, width: int = 800, height: int = 600, x: int = None, y: int = None, force_new: bool = False) -> str:
        """
        Create a new desktop window for a QuickApp with reuse and position persistence
        
        Args:
            qa_id: QuickApp ID
            title: Window title (defaults to "QuickApp {qa_id}")
            width: Window width
            height: Window height
            x: Window x position (uses saved position if not specified)
            y: Window y position (uses saved position if not specified)
            force_new: If True, create new window even if one exists
            
        Returns:
            window_id: Unique identifier for the created window
        """
        if title is None:
            title = f"QuickApp {qa_id}"
            
        qa_key = self._get_qa_key(qa_id, title)
        
        # Check if we should reuse an existing window
        if not force_new:
            # First check in-memory mapping
            if qa_id in self.qa_windows:
                existing_window_id = self.qa_windows[qa_id]
                if existing_window_id in self.windows:
                    # Window still exists in memory, reuse it
                    print(f"Reusing existing window for QA {qa_id}: {existing_window_id}")
                    self._refresh_window_content(existing_window_id, qa_id)
                    return existing_window_id
                else:
                    # Window was closed, remove the mapping
                    del self.qa_windows[qa_id]
            
            # Check for surviving processes from previous sessions (VS Code kill -9 scenario)
            existing_window_id = self._find_existing_qa_window(qa_id)
            if existing_window_id:
                print(f"Reconnecting to existing window for QA {qa_id}: {existing_window_id}")
                return existing_window_id
        
        # Get saved position if x,y not specified
        saved_pos = self._get_saved_position(qa_key)
        if saved_pos and x is None and y is None:
            x, y = saved_pos["x"], saved_pos["y"] 
            width, height = saved_pos["width"], saved_pos["height"]
            print(f"Using saved position for QA {qa_id}: x={x}, y={y}, size={width}x{height}")
        
        # Provide defaults for x,y if still not specified
        if x is None:
            x = 100 + (qa_id % 10) * 30  # Offset by QA ID to avoid overlapping
        if y is None:
            y = 100 + (qa_id % 10) * 30
        
        if not WEBVIEW_AVAILABLE:
            print("Warning: pywebview not available. Install with: pip install pywebview")
            # Fallback to browser tab
            return self._fallback_browser_open(qa_id, title, width, height, x, y)
            
        window_id = f"qa_{qa_id}_{int(time.time())}"
            
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
            webview_script = f"""
import webview
import sys
import signal
import json
import time
import os

# Detect if we're running from terminal (should close on Ctrl+C) vs VS Code (should survive)
SURVIVE_PARENT_DEATH = not sys.stdin.isatty()  # Survive if not in terminal (VS Code scenario)

def signal_handler(sig, frame):
    # Only exit on SIGINT (Ctrl+C) if we're running from terminal
    if sig == signal.SIGINT and not SURVIVE_PARENT_DEATH:
        print("Received Ctrl+C, closing window...")
        sys.exit(0)
    elif sig == signal.SIGTERM and not SURVIVE_PARENT_DEATH:
        # SIGTERM means explicit termination request - only honor if from terminal
        print("Received SIGTERM, closing window...")
        sys.exit(0)
    else:
        print(f"Received signal {{sig}}, ignoring to survive parent process death")

# Set up signal handlers to survive VS Code kill -9 (cross-platform)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Ignore SIGHUP (parent process death) to survive VS Code kill -9 (Unix only)
try:
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
except AttributeError:
    pass  # SIGHUP not available on Windows

# Also ignore SIGPIPE in case parent process dies (Unix only)  
try:
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
except AttributeError:
    pass  # SIGPIPE not available on Windows

# Windows-specific signal handling
if sys.platform.startswith('win'):
    try:
        # Handle Windows-specific signals
        signal.signal(signal.SIGBREAK, signal_handler)  # Ctrl+Break
    except AttributeError:
        pass

def save_position(window):
    try:
        import json
        import sys
        import tempfile
        import time
        import random
        from pathlib import Path
        
        registry_file = Path.home() / ".plua" / "window_registry.json"
        max_retries = 3
        base_delay = 0.01
        
        for attempt in range(max_retries):
            try:
                # Use unique temp file names to avoid conflicts
                timestamp = int(time.time() * 1000000)
                random_suffix = random.randint(1000, 9999)
                temp_file = registry_file.with_suffix(f'.json.tmp.{{timestamp}}.{{random_suffix}}')
                
                lock_acquired = False
                lock_fd = None
                
                try:
                    lock_fd = open(registry_file.with_suffix('.lockfile'), 'w')
                    
                    # Cross-platform file locking with timeout
                    if sys.platform.startswith('win'):
                        import msvcrt
                        for lock_attempt in range(10):
                            try:
                                msvcrt.locking(lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
                                lock_acquired = True
                                break
                            except OSError:
                                time.sleep(0.01)
                    else:
                        import fcntl
                        for lock_attempt in range(10):
                            try:
                                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                                lock_acquired = True
                                break
                            except (OSError, IOError):
                                time.sleep(0.01)
                    
                    if not lock_acquired:
                        raise Exception(f"Could not acquire lock (attempt {{attempt + 1}})")
                    
                    # Read current registry
                    if registry_file.exists():
                        with open(registry_file, 'r') as f:
                            registry = json.load(f)
                    else:
                        registry = {{"windows": {{}}, "positions": {{}}}}
                    
                    qa_key = "{qa_key}"
                    registry["positions"][qa_key] = {{
                        "x": window.x,
                        "y": window.y, 
                        "width": window.width,
                        "height": window.height,
                        "timestamp": time.time(),
                        "updated": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    }}
                    
                    # Write atomically
                    with open(temp_file, 'w') as f:
                        json.dump(registry, f, indent=2)
                        f.write('\\n')
                        f.flush()
                        import os
                        os.fsync(f.fileno())
                    
                    # Atomic rename (Windows requires removing target file first)
                    if sys.platform.startswith('win') and registry_file.exists():
                        registry_file.unlink()
                    temp_file.rename(registry_file)
                    
                    return  # Success
                    
                finally:
                    if lock_acquired and lock_fd:
                        try:
                            if sys.platform.startswith('win'):
                                import msvcrt
                                msvcrt.locking(lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                        except Exception:
                            pass
                    
                    if lock_fd:
                        try:
                            lock_fd.close()
                        except Exception:
                            pass
                    
                    try:
                        if temp_file.exists():
                            temp_file.unlink()
                    except Exception:
                        pass
                    
                    try:
                        lock_file = registry_file.with_suffix('.lockfile')
                        if lock_file.exists():
                            lock_file.unlink()
                    except Exception:
                        pass
                        
            except Exception as e:
                if attempt == max_retries - 1:
                    print("Failed to save window position after retries:", e)
                    return
                else:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.01)
                    time.sleep(delay)
            
    except Exception as e:
        print("Failed to save window position:", e)

try:
    window = webview.create_window(
        title="{title}",
        url="{url}",
        width={width},
        height={height},
        x={x},
        y={y},
        resizable=True,
        on_top=False
    )
    
    window.events.moved += lambda: save_position(window)
    window.events.resized += lambda: save_position(window) 
    
    print(f"Webview window created: {window_id}")
    webview.start(debug=False)
    
except Exception as e:
    print("Webview error:", e)
    sys.exit(1)
"""
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(webview_script)
                temp_script = f.name
            
            # Start the webview process with cross-platform detachment
            try:
                # Cross-platform process detachment
                if sys.platform.startswith('win'):
                    # Windows: Use CREATE_NEW_PROCESS_GROUP to detach
                    process = subprocess.Popen([sys.executable, temp_script], 
                                             stdout=subprocess.DEVNULL, 
                                             stderr=subprocess.DEVNULL,
                                             stdin=subprocess.DEVNULL,
                                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                                             )
                else:
                    # Unix/Linux/macOS: Use setsid for full detachment
                    process = subprocess.Popen([sys.executable, temp_script], 
                                             stdout=subprocess.DEVNULL, 
                                             stderr=subprocess.DEVNULL,
                                             stdin=subprocess.DEVNULL,
                                             start_new_session=True,  # Detach from parent process group
                                             preexec_fn=os.setsid if hasattr(os, 'setsid') else None  # Create new session
                                             )
            except Exception as e:
                print(f"Failed with full detachment, trying basic: {e}")
                # Fallback with basic detachment
                try:
                    if sys.platform.startswith('win'):
                        process = subprocess.Popen([sys.executable, temp_script], 
                                                 stdout=subprocess.DEVNULL, 
                                                 stderr=subprocess.DEVNULL,
                                                 stdin=subprocess.DEVNULL,
                                                 creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                                                 )
                    else:
                        process = subprocess.Popen([sys.executable, temp_script], 
                                                 stdout=subprocess.DEVNULL, 
                                                 stderr=subprocess.DEVNULL,
                                                 stdin=subprocess.DEVNULL,
                                                 start_new_session=True  # Still detach from parent process group
                                                 )
                except Exception as e2:
                    print(f"Failed with basic detachment: {e2}")
                    # Final fallback - no detachment
                    process = subprocess.Popen([sys.executable, temp_script], 
                                             stdout=subprocess.DEVNULL, 
                                             stderr=subprocess.DEVNULL,
                                             stdin=subprocess.DEVNULL
                                             )
            
            self.windows[window_id] = {
                "process": process,
                "temp_script": temp_script,
                "qa_id": qa_id,
                "title": title,
                "url": url,
                "type": "webview_process",
                "pid": process.pid,  # Store PID for process tracking
                "x": x, "y": y, "width": width, "height": height
            }
            
            # Map QA ID to window for reuse
            self.qa_windows[qa_id] = window_id
            
            # Log window to registry with PID for reconnection
            self._log_window_to_registry(window_id, qa_id, title, process.pid)
            
            print(f"Created QuickApp desktop window: {window_id} for QA {qa_id}")
            
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
            return self._fallback_browser_open(qa_id, title, width, height, x, y)
    
    def _refresh_window_content(self, window_id: str, qa_id: int):
        """Refresh the content of an existing window"""
        try:
            # For process-based windows, we can't easily refresh content
            # For now, just log that we're reusing the window
            print(f"Window {window_id} will show updated content for QA {qa_id}")
            # The QuickApp UI will automatically refresh when it detects changes
        except Exception as e:
            print(f"Error refreshing window {window_id}: {e}")
            
            # Write script to temporary file
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
            return self._fallback_browser_open(qa_id, title, width, height, x, y)
    
    def _fallback_browser_open(self, qa_id: int, title: str = None, width: int = 800, height: int = 600, x: int = None, y: int = None) -> str:
        """Fallback method to open in browser tab if webview fails"""
        window_id = f"qa_{qa_id}_{int(time.time())}_browser"
        if title is None:
            title = f"QuickApp {qa_id}"
            
        browser_url = self.api_base_url.replace("0.0.0.0", "localhost")
        url = f"{browser_url}/static/quickapp_ui.html?qa_id={qa_id}&desktop=true"
        
        try:
            import webbrowser
            webbrowser.open_new_tab(url)
            
            # Store a placeholder for the window (note: browser windows can't be positioned)
            self.windows[window_id] = {"url": url, "qa_id": qa_id, "title": title, "type": "browser"}
            
            # Map QA ID to window for reuse  
            self.qa_windows[qa_id] = window_id
            
            print(f"Fallback: Opened QuickApp {qa_id} in browser tab: {url}")
            print(f"Created window reference: {window_id}")
            if x is not None and y is not None:
                print(f"Note: Browser tabs cannot be positioned at x={x}, y={y}")
            
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
            qa_id = window_info.get("qa_id") if isinstance(window_info, dict) else None
            
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
                    
                # Remove from QA mapping if this window was mapped
                if qa_id and qa_id in self.qa_windows and self.qa_windows[qa_id] == window_id:
                    del self.qa_windows[qa_id]
                    
                # Remove from registry and log closure
                del self.windows[window_id]
                self._log_window_closure(window_id)
                return True
                
            else:
                # Old-style webview object
                window_info.destroy()
                
                # Remove from QA mapping if this window was mapped
                if qa_id and qa_id in self.qa_windows and self.qa_windows[qa_id] == window_id:
                    del self.qa_windows[qa_id]
                    
                del self.windows[window_id]
                self._log_window_closure(window_id)
                return True
                
        except Exception as e:
            print(f"Error closing window {window_id}: {e}")
            return False
        
        return False
    
    def close_qa_window(self, qa_id: int) -> bool:
        """
        Close the window for a specific QuickApp by QA ID
        
        Args:
            qa_id: QuickApp ID
            
        Returns:
            True if window was found and closed, False otherwise
        """
        if qa_id in self.qa_windows:
            window_id = self.qa_windows[qa_id]
            return self.close_window(window_id)
        return False
    
    def close_all_qa_windows(self) -> int:
        """
        Close all QuickApp windows
        
        Returns:
            Number of windows closed
        """
        window_ids = list(self.windows.keys())
        closed_count = 0
        
        for window_id in window_ids:
            if self.close_window(window_id):
                closed_count += 1
                
        return closed_count
    
    def _log_window_closure(self, window_id: str):
        """Log window closure to registry"""
        try:
            registry = self._load_registry()
            
            if "windows" not in registry:
                registry["windows"] = {}
                
            if window_id in registry["windows"]:
                registry["windows"][window_id]["status"] = "closed"
                registry["windows"][window_id]["closed"] = time.time()
                registry["windows"][window_id]["closed_iso"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            else:
                # Create a basic closure record
                registry["windows"][window_id] = {
                    "status": "closed",
                    "closed": time.time(),
                    "closed_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
                
            self._save_registry(registry)
            print(f"Window {window_id} marked as closed in registry")
        except Exception as e:
            print(f"Warning: Failed to log window closure: {e}")
    
    def _log_window_to_registry(self, window_id: str, qa_id: int, title: str, pid: int):
        """Log window creation to registry with PID for reconnection"""
        try:
            registry = self._load_registry()
            
            if "windows" not in registry:
                registry["windows"] = {}
                
            registry["windows"][window_id] = {
                "qa_id": qa_id,
                "title": title,
                "pid": pid,
                "status": "open",
                "created": time.time(),
                "created_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }
                
            self._save_registry(registry)
        except Exception as e:
            print(f"Warning: Failed to log window to registry: {e}")
    
    def list_windows(self) -> Dict[str, Dict[str, Any]]:
        """List all open QuickApp windows (legacy method)"""
        return self.list_qa_windows()
    
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

    def create_quickapp_window_direct(self, qa_id: int, title: str = None, width: int = 800, height: int = 600, x: int = None, y: int = None, force_new: bool = False) -> str:
        """
        Direct method to create QuickApp window (called from Lua via _PY table)
        This replaces the HTTP endpoint approach
        """
        try:
            return self.create_quickapp_window(qa_id, title, width, height, x, y, force_new)
        except Exception as e:
            print(f"Failed to create desktop window for QA {qa_id}: {e}")
            return None
    
    def close_qa_window_direct(self, qa_id: int) -> bool:
        """
        Direct method to close QuickApp window by QA ID (called from Lua via _PY table)
        """
        try:
            return self.close_qa_window(qa_id)
        except Exception as e:
            print(f"Failed to close window for QA {qa_id}: {e}")
            return False
    
    def close_all_qa_windows_direct(self) -> int:
        """
        Direct method to close all QuickApp windows (called from Lua via _PY table)
        """
        try:
            return self.close_all_qa_windows()
        except Exception as e:
            print(f"Failed to close all windows: {e}")
            return 0
    
    def list_qa_windows(self) -> Dict[str, Dict[str, Any]]:
        """List all QuickApp windows with their QA IDs and status"""
        result = {}
        for window_id, window_info in self.windows.items():
            if isinstance(window_info, dict):
                qa_id = window_info.get("qa_id", "unknown")
                result[window_id] = {
                    'qa_id': qa_id,
                    'title': window_info.get("title", "Unknown"),
                    'type': window_info.get("type", "unknown"),
                    'url': window_info.get("url", "Unknown")
                }
            else:
                result[window_id] = {
                    'qa_id': "unknown",
                    'title': getattr(window_info, 'title', 'Unknown'),
                    'type': "webview_object",
                    'url': getattr(window_info, 'url', 'Unknown')
                }
        return result


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
def create_quickapp_window_api(qa_id: int, title: str = None, width: int = 800, height: int = 600, x: int = None, y: int = None, force_new: bool = False) -> dict:
    """API function to create a QuickApp window"""
    manager = get_desktop_manager()
    if not manager:
        return {"error": "Desktop UI not initialized"}
    
    try:
        window_id = manager.create_quickapp_window(qa_id, title, width, height, x, y, force_new)
        return {
            "success": True,
            "window_id": window_id,
            "qa_id": qa_id,
            "title": title or f"QuickApp {qa_id}"
        }
    except Exception as e:
        return {"error": str(e)}


def close_quickapp_window_api(window_id: str) -> dict:
    """API function to close a QuickApp window by window ID"""
    manager = get_desktop_manager()
    if not manager:
        return {"error": "Desktop UI not initialized"}
    
    success = manager.close_window(window_id)
    return {"success": success}


def close_qa_window_api(qa_id: int) -> dict:
    """API function to close a QuickApp window by QA ID"""
    manager = get_desktop_manager()
    if not manager:
        return {"error": "Desktop UI not initialized"}
    
    success = manager.close_qa_window(qa_id)
    return {"success": success}


def close_all_qa_windows_api() -> dict:
    """API function to close all QuickApp windows"""
    manager = get_desktop_manager()
    if not manager:
        return {"error": "Desktop UI not initialized"}
    
    closed_count = manager.close_all_qa_windows()
    return {"success": True, "closed_count": closed_count}


def list_quickapp_windows_api() -> dict:
    """API function to list all QuickApp windows"""
    manager = get_desktop_manager()
    if not manager:
        return {"error": "Desktop UI not initialized"}
    
    windows = manager.list_qa_windows()
    return {"windows": windows}


def send_to_quickapp_window_api(window_id: str, event_type: str, data: Any) -> dict:
    """API function to send data to a QuickApp window"""
    manager = get_desktop_manager()
    if not manager:
        return {"error": "Desktop UI not initialized"}
    
    success = manager.send_to_window(window_id, event_type, data)
    return {"success": success}
