#!/usr/bin/env python3
"""
Simple test of Python's webbrowser module to verify it works correctly on macOS.
"""

import webbrowser
import time

def test_webbrowser():
    """Test the webbrowser module with different options."""
    
    print("Testing Python webbrowser module...")
    
    # Test 1: Open a new window (new=1)
    print("1. Opening new window with new=1...")
    success1 = webbrowser.open("https://www.google.com", new=1, autoraise=True)
    print(f"   Result: {success1}")
    
    time.sleep(2)
    
    # Test 2: Open another new window with different URL
    print("2. Opening another new window with different URL...")
    success2 = webbrowser.open("https://www.github.com", new=1, autoraise=True)
    print(f"   Result: {success2}")
    
    time.sleep(2)
    
    # Test 3: Open a new tab (new=2)
    print("3. Opening new tab with new=2...")
    success3 = webbrowser.open("https://www.stackoverflow.com", new=2, autoraise=True)
    print(f"   Result: {success3}")
    
    print("\nTest completed!")
    print("You should see:")
    print("- Two separate browser windows (Google and GitHub)")
    print("- One new tab (StackOverflow) in one of the windows")

if __name__ == "__main__":
    test_webbrowser()
