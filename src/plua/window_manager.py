"""
Window Manager for PLua - External Browser Window Management

This module provides window management functionality specifically designed
for the PLua UI system. It replaces the previous Tkinter-based UI with browser windows
"""

import platform
import logging
import time
import os
import json
import webbrowser
import subprocess
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BrowserWindow:
    """Represents a single browser window instance."""
    
    def __init__(self, window_id: str, url: str, width: int = 800, height: int = 600,
                 x: int = 100, y: int = 100):
        self.window_id = window_id
        self.url = url
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.process = None
        self.is_open = False
        self.created_in_session = False  # Track if window was created in this session
        self.created_at = datetime.now().isoformat()  # Track creation time
        
    def __str__(self):
        return f"BrowserWindow({self.window_id}, {self.url}, {self.width}x{self.height})"


class WindowManager:
    """Manages external browser windows for PLua UI."""
    
    def __init__(self):
        self.windows: Dict[str, BrowserWindow] = {}
        self.system = platform.system().lower()
        
        # Use ~/.plua/ directory for state file
        plua_dir = os.path.expanduser("~/.plua")
        os.makedirs(plua_dir, exist_ok=True)
        self.state_file = os.path.join(plua_dir, "windows.json")
        
        self._load_window_state()
        logger.info(f"WindowManager initialized for {self.system}, state file: {self.state_file}")

    def _load_window_state(self):
        """Load window state from persistent storage and clean up stale entries"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                # Clean up entries older than 10 minutes
                cutoff_time = datetime.now() - timedelta(minutes=10)
                valid_windows = {}
                stale_count = 0
                
                for window_id, window_data in state.items():
                    # Check if window has created_at timestamp
                    if 'created_at' in window_data:
                        try:
                            created_at = datetime.fromisoformat(window_data['created_at'])
                            if created_at > cutoff_time:
                                # Window is recent enough to keep
                                window = BrowserWindow(
                                    window_id=window_data['window_id'],
                                    url=window_data['url'],
                                    width=window_data['width'],
                                    height=window_data['height'],
                                    x=window_data['x'],
                                    y=window_data['y']
                                )
                                window.is_open = True
                                window.created_in_session = False
                                window.created_at = window_data['created_at']
                                valid_windows[window_id] = window
                            else:
                                stale_count += 1
                        except (ValueError, KeyError):
                            # Invalid timestamp, treat as stale
                            stale_count += 1
                    else:
                        # Old entry without timestamp, treat as stale
                        stale_count += 1
                
                self.windows = valid_windows
                
                if stale_count > 0:
                    logger.debug(f"Cleaned up {stale_count} stale window entries (older than 10 minutes)")
                    # Save the cleaned state immediately
                    self._save_window_state()
                    
                logger.debug(f"Loaded {len(self.windows)} valid window states from {self.state_file}")
        except Exception as e:
            logger.debug(f"Could not load window state: {e}")

    def _save_window_state(self):
        """Save window state to persistent storage"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            
            # Only save windows that were created in this session and are still open
            state_to_save = {}
            for window_id, window in self.windows.items():
                if window.is_open and getattr(window, 'created_in_session', True):
                    state_to_save[window_id] = {
                        'window_id': window.window_id,
                        'url': window.url,
                        'width': window.width,
                        'height': window.height,
                        'x': window.x,
                        'y': window.y,
                        'created_at': getattr(window, 'created_at', datetime.now().isoformat())
                    }
            
            with open(self.state_file, 'w') as f:
                json.dump(state_to_save, f, indent=2)
                
            logger.debug(f"Saved {len(state_to_save)} window states to {self.state_file}")
        except Exception as e:
            logger.debug(f"Could not save window state: {e}")

    def create_window(self, window_id: str, url: str, width: int = 800, height: int = 600,
                      x: int = 100, y: int = 100) -> bool:
        """
        Create a new browser window.
        
        Args:
            window_id: Unique identifier for the window
            url: URL to display in the window
            width: Window width in pixels
            height: Window height in pixels
            x: Window x position
            y: Window y position
            
        Returns:
            True if window was created successfully, False otherwise
        """
        logger.debug(f"Creating window {window_id} for URL: {url}")
        
        # Check if we already have a window with the same window_id
        if window_id in self.windows:
            existing_window = self.windows[window_id]
            # Check if the existing window is still open and has the same URL
            if self._is_window_still_open(existing_window):
                if existing_window.url == url:
                    # For QuickApp windows, we're not sure if the browser window is actually open
                    # So we'll attempt to open it again, which should reuse if it exists
                    if "quickapp_ui.html" in url and "qa_id=" in url:
                        logger.info(f"QuickApp window {window_id} exists in state, attempting to open/reuse")
                        # Update the window properties in case they changed
                        existing_window.width = width
                        existing_window.height = height
                        existing_window.x = x
                        existing_window.y = y
                        # Try to launch the browser - this will reuse if window is open, or create new if closed
                        if self._launch_browser(existing_window):
                            # Mark as created in this session so it gets saved
                            existing_window.created_in_session = True
                            self._save_window_state()
                            logger.info(f"Successfully opened/reused QuickApp window {window_id}")
                            return True
                        else:
                            logger.warning(f"Failed to open QuickApp window {window_id}, removing from state")
                            self._remove_window_reference(existing_window)
                            # Continue to create a new window below
                    else:
                        logger.info(f"Reusing existing non-QuickApp window {window_id} (same URL)")
                        return True
                else:
                    logger.info(f"Existing window {window_id} has different URL, updating and reusing")
                    # Update the URL in the existing window
                    existing_window.url = url
                    existing_window.width = width
                    existing_window.height = height
                    existing_window.x = x
                    existing_window.y = y
                    # For QuickApp windows, try to open with new URL
                    if "quickapp_ui.html" in url and "qa_id=" in url:
                        if self._launch_browser(existing_window):
                            # Mark as created in this session so it gets saved
                            existing_window.created_in_session = True
                            self._save_window_state()
                            return True
                        else:
                            logger.warning(f"Failed to update QuickApp window {window_id}, removing from state")
                            self._remove_window_reference(existing_window)
                            # Continue to create a new window below
                    else:
                        # The window is already open, just update our records
                        self._save_window_state()
                        return True
            else:
                logger.debug(f"Existing window {window_id} no longer open, will create new one")
                # Remove the stale window reference
                self._remove_window_reference(existing_window)
        
        # Check if we already have a window with the same URL (different window_id)
        existing_window = self._find_window_by_url(url)
        if existing_window and existing_window.window_id != window_id:
            # Verify the window is still actually open by trying to check if the browser process exists
            if self._is_window_still_open(existing_window):
                logger.info(f"Reusing existing window {existing_window.window_id} for URL: {url}")
                # Update the window_id mapping to point to the existing window
                self.windows[window_id] = existing_window
                self._save_window_state()
                return True
            else:
                logger.debug(f"Existing window {existing_window.window_id} no longer open, creating new one")
                # Remove the stale window reference
                self._remove_window_reference(existing_window)
            
        window = BrowserWindow(window_id, url, width, height, x, y)
        window.created_in_session = True  # Mark as created in current session
        
        try:
            if self._launch_browser(window):
                self.windows[window_id] = window
                window.is_open = True
                self._save_window_state()
                logger.info(f"Created new window {window_id}: {url}")
                return True
            else:
                logger.error(f"Failed to launch browser for window {window_id}")
                return False
        except Exception as e:
            logger.error(f"Error creating window {window_id}: {e}")
            return False
    
    def _find_window_by_url(self, url: str) -> Optional[BrowserWindow]:
        """
        Find an existing window that displays the same URL.
        
        Args:
            url: URL to search for
            
        Returns:
            BrowserWindow instance if found, None otherwise
        """
        for window in self.windows.values():
            if window.url == url and window.is_open:
                # Only reuse windows created in current session, or if we can verify they're still open
                if getattr(window, 'created_in_session', False) or self._is_window_still_open(window):
                    logger.debug(f"Reusing existing window for URL: {url}")
                    return window
        return None

    def _is_window_still_open(self, window: BrowserWindow) -> bool:
        """
        Check if a window is still actually open.
        For QuickApp windows, we assume they might still be open across sessions.
        For other windows, only trust those created in this session.
        
        Args:
            window: BrowserWindow to check
            
        Returns:
            True if window should be considered open, False otherwise
        """
        # For QuickApp windows (identified by the URL pattern), be more optimistic about reuse
        if "quickapp_ui.html" in window.url and "qa_id=" in window.url:
            logger.debug(f"QuickApp window {window.window_id} - assuming may still be open for reuse")
            return True
        
        # For windows created in this session, assume they're still open
        if getattr(window, 'created_in_session', False):
            logger.debug(f"Window {window.window_id} was created in this session, assuming still open")
            return True
        else:
            logger.debug(f"Non-QuickApp window {window.window_id} from previous session, assuming closed")
            return False

    def _remove_window_reference(self, window: BrowserWindow):
        """Remove all references to a window that's no longer open"""
        windows_to_remove = []
        for window_id, win in self.windows.items():
            if win == window:
                windows_to_remove.append(window_id)
        
        for window_id in windows_to_remove:
            del self.windows[window_id]
        
        self._save_window_state()
            
    def close_window(self, window_id: str) -> bool:
        """
        Close a browser window.
        
        Args:
            window_id: ID of the window to close
            
        Returns:
            True if window was closed successfully, False otherwise
        """
        if window_id not in self.windows:
            logger.warning(f"Window {window_id} not found")
            return False
            
        window = self.windows[window_id]
        
        try:
            if window.process and window.process.poll() is None:
                window.process.terminate()
                # Give it a moment to terminate gracefully
                time.sleep(0.5)
                if window.process.poll() is None:
                    window.process.kill()
                    
            window.is_open = False
            del self.windows[window_id]
            self._save_window_state()
            logger.info(f"Closed window {window_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing window {window_id}: {e}")
            return False
            
    def set_window_url(self, window_id: str, url: str) -> bool:
        """
        Update the URL of an existing window.
        
        Args:
            window_id: ID of the window to update
            url: New URL to display
            
        Returns:
            True if URL was updated successfully, False otherwise
        """
        if window_id not in self.windows:
            logger.warning(f"Window {window_id} not found")
            return False
            
        window = self.windows[window_id]
        old_url = window.url
        window.url = url
        
        # For now, we'll close and reopen the window with the new URL
        # In the future, we could use browser automation to navigate
        try:
            width, height = window.width, window.height
            x, y = window.x, window.y
            
            self.close_window(window_id)
            success = self.create_window(window_id, url, width, height, x, y)
            
            if success:
                logger.info(f"Updated window {window_id} URL: {old_url} -> {url}")
            else:
                logger.error(f"Failed to update window {window_id} URL")
                
            return success
            
        except Exception as e:
            logger.error(f"Error updating window {window_id} URL: {e}")
            return False
            
    def get_window_info(self, window_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a window.
        
        Args:
            window_id: ID of the window
            
        Returns:
            Dictionary with window information, or None if window not found
        """
        if window_id not in self.windows:
            return None
            
        window = self.windows[window_id]
        return {
            "id": window.window_id,
            "url": window.url,
            "width": window.width,
            "height": window.height,
            "x": window.x,
            "y": window.y,
            "is_open": window.is_open
        }
        
    def inject_css(self, window_id: str, css_code: str) -> bool:
        """
        Inject CSS code into a browser window.
        
        Args:
            window_id: ID of the window
            css_code: CSS code to inject
            
        Returns:
            True if CSS was injected successfully, False otherwise
        """
        if window_id not in self.windows:
            logger.warning(f"Window {window_id} not found for CSS injection")
            return False
            
        try:
            import platform
            
            if platform.system() == "Darwin":  # macOS
                # Use AppleScript to inject CSS via JavaScript
                # We'll inject the CSS by creating a style element
                escaped_css = css_code.replace('"', '\\"').replace('\n', ' ').replace('\t', ' ').replace('!', '\\!')
                
                # More specific targeting for QuickApp windows
                applescript = f'''
                tell application "Safari"
                    set windowFound to false
                    repeat with w in every window
                        repeat with t in every tab of w
                            set tabURL to URL of t
                            if tabURL contains "quickapp_ui.html" and tabURL contains "qa_id=" then
                                try
                                    do JavaScript "
                                        console.log('PLua: Injecting CSS for window {window_id}');
                                        var styleElement = document.getElementById('plua-dynamic-style');
                                        if (!styleElement) {{
                                            styleElement = document.createElement('style');
                                            styleElement.id = 'plua-dynamic-style';
                                            styleElement.type = 'text/css';
                                            document.head.appendChild(styleElement);
                                            console.log('PLua: Created new style element');
                                        }}
                                        styleElement.textContent = '{escaped_css}';
                                        console.log('PLua: CSS injected successfully');
                                        console.log('PLua: Injected CSS content: {escaped_css}');
                                    " in t
                                    set windowFound to true
                                    exit repeat
                                on error errorMessage
                                    log "JavaScript error: " & errorMessage
                                end try
                            end if
                        end repeat
                        if windowFound then exit repeat
                    end repeat
                    
                    if not windowFound then
                        log "No matching QuickApp window found for CSS injection"
                    end if
                end tell
                '''
                
                result = subprocess.run(
                    ["osascript", "-e", applescript],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    logger.info(f"Successfully injected CSS into window {window_id}")
                    return True
                else:
                    logger.warning(f"Failed to inject CSS into window {window_id}: {result.stderr}")
                    return False
                    
            else:
                # For other platforms, we could implement browser automation
                # For now, log that it's not supported
                logger.warning(f"CSS injection not yet supported on {platform.system()}")
                return False
                
        except Exception as e:
            logger.error(f"Error injecting CSS into window {window_id}: {e}")
            return False
        
    def list_windows(self) -> Dict[str, Dict[str, Any]]:
        """
        List all managed windows.
        
        Returns:
            Dictionary mapping window IDs to window information
        """
        return {wid: self.get_window_info(wid) for wid in self.windows.keys()}
        
    def close_all_windows(self):
        """Close all managed windows."""
        window_ids = list(self.windows.keys())
        for window_id in window_ids:
            self.close_window(window_id)
        logger.info("All windows closed")
        
    def _launch_browser(self, window: BrowserWindow) -> bool:
        """
        Launch a browser window using the most reliable method for new windows.
        
        Args:
            window: BrowserWindow instance to launch
            
        Returns:
            True if browser was launched successfully, False otherwise
        """
        try:
            logger.debug(f"Launching browser for URL: {window.url}")
            
            # macOS-specific approach for reliable new window creation
            if self.system == 'darwin':
                success = self._launch_browser_macos(window)
            else:
                # For other platforms, use webbrowser module
                success = webbrowser.open(window.url, new=1, autoraise=True)
            
            if success:
                logger.info(f"Successfully launched browser window for {window.url}")
                return True
            else:
                logger.error(f"Failed to launch browser for {window.url}")
                return False
                
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            return False
    
    def _launch_browser_macos(self, window: BrowserWindow) -> bool:
        """
        Launch a browser window on macOS using AppleScript to create a proper new window.
        
        Args:
            window: BrowserWindow instance to launch
            
        Returns:
            True if browser was launched successfully, False otherwise
        """
        import subprocess
        import urllib.parse
        
        try:
            # Extract QA ID from URL for matching
            qa_id = ""
            if "qa_id=" in window.url:
                qa_id = window.url.split("qa_id=")[1].split("&")[0]
            
            # Use AppleScript to find existing window or create new one with proper size and position
            applescript = f'''
            tell application "Safari"
                set foundWindow to false
                set targetURL to "{window.url}"
                set qaId to "{qa_id}"
                
                -- Check if a window with this QA ID already exists
                if (exists (first window)) and qaId is not "" then
                    repeat with w in windows
                        if (exists (current tab of w)) then
                            set currentURL to URL of current tab of w
                            if currentURL contains ("qa_id=" & qaId) then
                                -- Found existing window with same QA ID, bring just this window to front
                                set index of w to 1
                                set bounds of w to {{{window.x}, {window.y}, {window.x + window.width}, {window.y + window.height}}}
                                set foundWindow to true
                                exit repeat
                            end if
                        end if
                    end repeat
                end if
                
                -- If no existing window found, create a new one
                if not foundWindow then
                    if not (exists (first window)) then
                        -- If no Safari windows exist, just open the URL normally
                        open location targetURL
                        delay 0.5
                        -- Set bounds for the first window
                        if (exists (first window)) then
                            set bounds of first window to {{{window.x}, {window.y}, {window.x + window.width}, {window.y + window.height}}}
                            -- Only bring this window to front, don't activate entire Safari
                            set index of first window to 1
                        end if
                    else
                        -- Create a new window with the URL
                        set newDoc to make new document with properties {{URL:targetURL}}
                        delay 0.5
                        -- Find the window containing the new document and set its bounds
                        repeat with w in windows
                            if (exists (current tab of w)) and (URL of current tab of w contains targetURL) then
                                set bounds of w to {{{window.x}, {window.y}, {window.x + window.width}, {window.y + window.height}}}
                                -- Only bring this specific window to front
                                set index of w to 1
                                exit repeat
                            end if
                        end repeat
                    end if
                end if
                -- Don't activate Safari - this would bring all windows to front
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                logger.debug(f"macOS AppleScript command succeeded for {window.url} ({window.width}x{window.height} at {window.x},{window.y})")
                return True
            else:
                logger.warning(f"macOS AppleScript failed (code {result.returncode}), falling back to webbrowser")
                logger.debug(f"stderr: {result.stderr}")
                # Fallback to webbrowser module
                return webbrowser.open(window.url, new=1, autoraise=True)
                
        except subprocess.TimeoutExpired:
            logger.warning("macOS AppleScript command timed out, falling back to webbrowser")
            return webbrowser.open(window.url, new=1, autoraise=True)
        except Exception as e:
            logger.warning(f"macOS AppleScript command failed: {e}, falling back to webbrowser")
            return webbrowser.open(window.url, new=1, autoraise=True)


# Global window manager instance
_window_manager = None

def get_window_manager() -> WindowManager:
    """Get the global window manager instance."""
    global _window_manager
    if _window_manager is None:
        _window_manager = WindowManager()
    return _window_manager


# _PY functions for Lua integration
def create_window(window_id: str, url: str, width: int = 800, height: int = 600,
                 x: int = 100, y: int = 100) -> bool:
    """
    Create a new browser window (Lua callable).
    
    Args:
        window_id: Unique identifier for the window
        url: URL to display in the window
        width: Window width in pixels (default: 800)
        height: Window height in pixels (default: 600)
        x: Window x position (default: 100)
        y: Window y position (default: 100)
        
    Returns:
        True if window was created successfully, False otherwise
    """
    return get_window_manager().create_window(window_id, url, width, height, x, y)


def close_window(window_id: str) -> bool:
    """
    Close a browser window (Lua callable).
    
    Args:
        window_id: ID of the window to close
        
    Returns:
        True if window was closed successfully, False otherwise
    """
    return get_window_manager().close_window(window_id)


def set_window_url(window_id: str, url: str) -> bool:
    """
    Update the URL of an existing window (Lua callable).
    
    Args:
        window_id: ID of the window to update
        url: New URL to display
        
    Returns:
        True if URL was updated successfully, False otherwise
    """
    return get_window_manager().set_window_url(window_id, url)


def get_window_info(window_id: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a window (Lua callable).
    
    Args:
        window_id: ID of the window
        
    Returns:
        Dictionary with window information, or None if window not found
    """
    return get_window_manager().get_window_info(window_id)


def list_windows() -> Dict[str, Dict[str, Any]]:
    """
    List all managed windows (Lua callable).
    
    Returns:
        Dictionary mapping window IDs to window information
    """
    return get_window_manager().list_windows()


def close_all_windows():
    """Close all managed windows (Lua callable)."""
    get_window_manager().close_all_windows()
