#!/usr/bin/env python3
"""
Test that only the specific Safari window comes to front, not all Safari windows.
"""

import subprocess
import time

def test_selective_window_focus():
    """Test that only the target window comes to front"""
    
    # Step 1: Create a regular Safari window first (to simulate existing browsing)
    print("1. Creating a regular Safari window (to simulate existing browsing)...")
    regular_script = '''
    tell application "Safari"
        if not (exists (first window)) then
            open location "https://httpbin.org/html"
        else
            make new document with properties {URL:"https://httpbin.org/html"}
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", regular_script])
    print("Regular Safari window created")
    
    # Wait
    time.sleep(2)
    
    # Step 2: Create a QuickApp window (should not bring regular window to front)
    print("2. Creating QuickApp window (should NOT bring regular window to front)...")
    qa_url = "http://localhost:8080/static/quickapp_ui.html?qa_id=7777&desktop=true"
    qa_script = f'''
    tell application "Safari"
        set foundWindow to false
        set targetURL to "{qa_url}"
        set qaId to "7777"
        
        -- Check if a window with this QA ID already exists
        if (exists (first window)) and qaId is not "" then
            repeat with w in windows
                if (exists (current tab of w)) then
                    set currentURL to URL of current tab of w
                    if currentURL contains ("qa_id=" & qaId) then
                        -- Found existing window with same QA ID, bring just this window to front
                        set index of w to 1
                        set bounds of w to {{100, 100, 500, 500}}
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
                    set bounds of first window to {{100, 100, 500, 500}}
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
                        set bounds of w to {{100, 100, 500, 500}}
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
    subprocess.run(["osascript", "-e", qa_script])
    print("QuickApp window created")
    
    # Wait
    time.sleep(2)
    
    # Step 3: Test reuse (should only affect the QuickApp window)
    print("3. Testing QuickApp window reuse (should only affect QA window)...")
    subprocess.run(["osascript", "-e", qa_script])
    print("QuickApp window reused")
    
    print("\nResult check:")
    print("- Only the QuickApp window should come to front")
    print("- The regular Safari window should stay in background")
    print("- Safari app should not steal focus from current app")

if __name__ == "__main__":
    test_selective_window_focus()
