#!/usr/bin/env python3
"""
Test script to verify browser window behavior on macOS.
"""

import webbrowser
import time
import subprocess

def test_webbrowser_new_values():
    """Test different 'new' parameter values with webbrowser.open"""
    
    urls = [
        "http://httpbin.org/html?test=window1",
        "http://httpbin.org/html?test=window2", 
        "http://httpbin.org/html?test=window3"
    ]
    
    print("=== Testing webbrowser.open with different 'new' values ===")
    
    # Test new=0 (same window)
    print(f"\n1. Opening with new=0 (same window): {urls[0]}")
    webbrowser.open(urls[0], new=0)
    time.sleep(3)
    
    # Test new=1 (new window)
    print(f"\n2. Opening with new=1 (new window): {urls[1]}")
    webbrowser.open(urls[1], new=1)
    time.sleep(3)
    
    # Test new=2 (new tab)
    print(f"\n3. Opening with new=2 (new tab): {urls[2]}")
    webbrowser.open(urls[2], new=2)
    time.sleep(3)
    
    print("\nObserve the Safari behavior:")
    print("- Did each URL open in a separate window?")
    print("- Or did they open as tabs in the same window?")

def test_explicit_safari_command():
    """Test using explicit Safari command via subprocess"""
    print("\n=== Testing explicit Safari command ===")
    
    url = "http://httpbin.org/html?test=explicit_safari"
    
    # Use 'open -n' to force a new Safari instance
    cmd = ["open", "-n", "-a", "Safari", url]
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
    except Exception as e:
        print(f"Error: {e}")

def test_safari_applescript():
    """Test using AppleScript to create new Safari window"""
    print("\n=== Testing Safari AppleScript ===")
    
    url = "http://httpbin.org/html?test=applescript"
    
    # AppleScript to create a new Safari window
    applescript = f'''
    tell application "Safari"
        make new document with properties {{URL:"{url}"}}
        activate
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True
        )
        print(f"AppleScript return code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
    except Exception as e:
        print(f"AppleScript error: {e}")

if __name__ == "__main__":
    print("Browser Behavior Test")
    print("====================")
    print("This script will test different methods of opening Safari windows.")
    print("Please observe Safari's behavior during the test.")
    
    test_webbrowser_new_values()
    test_explicit_safari_command()
    test_safari_applescript()
    
    print("\n=== Test Complete ===")
    print("Did the AppleScript method create separate windows?")
