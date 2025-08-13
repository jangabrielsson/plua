#!/usr/bin/env python3
"""
Simple test of Safari window reuse using the updated AppleScript logic.
"""

import subprocess
import time

def test_safari_reuse():
    """Test Safari window reuse directly with AppleScript"""
    
    # Test URLs
    url1 = "http://localhost:8080/static/quickapp_ui.html?qa_id=5555&desktop=true"
    url2 = "http://localhost:8080/static/quickapp_ui.html?qa_id=6666&desktop=true"
    
    # First AppleScript - create window for QA 5555
    print("1. Creating window for QA 5555...")
    applescript1 = f'''
    tell application "Safari"
        set foundWindow to false
        set targetURL to "{url1}"
        set qaId to "5555"
        
        -- Check if a window with this QA ID already exists
        if (exists (first window)) and qaId is not "" then
            repeat with w in windows
                if (exists (current tab of w)) then
                    set currentURL to URL of current tab of w
                    if currentURL contains ("qa_id=" & qaId) then
                        -- Found existing window with same QA ID, bring it to front
                        set index of w to 1
                        set foundWindow to true
                        exit repeat
                    end if
                end if
            end repeat
        end if
        
        -- If no existing window found, create a new one
        if not foundWindow then
            if not (exists (first window)) then
                open location targetURL
            else
                make new document with properties {{URL:targetURL}}
            end if
        end if
        activate
    end tell
    '''
    
    subprocess.run(["osascript", "-e", applescript1])
    print("Window for QA 5555 created/opened")
    
    # Wait
    time.sleep(3)
    
    # Second AppleScript - try to reuse window for QA 5555
    print("2. Trying to reuse window for QA 5555...")
    subprocess.run(["osascript", "-e", applescript1])
    print("Window for QA 5555 reused (should not create new window)")
    
    # Wait
    time.sleep(3)
    
    # Third AppleScript - create window for QA 6666 (should be new)
    print("3. Creating window for QA 6666 (should be new)...")
    applescript2 = applescript1.replace('targetURL to "{url1}"', f'targetURL to "{url2}"').replace('qaId to "5555"', 'qaId to "6666"')
    subprocess.run(["osascript", "-e", applescript2])
    print("Window for QA 6666 created")
    
    print("\nResult check:")
    print("- You should see exactly 2 Safari windows")
    print("- One for QA 5555, one for QA 6666") 
    print("- Step 2 should NOT have created a new window")

if __name__ == "__main__":
    test_safari_reuse()
