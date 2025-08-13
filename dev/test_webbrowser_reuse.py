#!/usr/bin/env python3
"""
Test to understand webbrowser behavior with same URLs
"""

import webbrowser
import time

def test_webbrowser_same_url():
    """Test what happens when we open the same URL multiple times."""
    
    print("Testing webbrowser behavior with same URL...")
    
    # Test URL
    test_url = "https://www.google.com"
    
    print(f"1. Opening URL: {test_url} (new=1)")
    success1 = webbrowser.open(test_url, new=1, autoraise=True)
    print(f"   Result: {success1}")
    
    time.sleep(3)
    
    print(f"2. Opening SAME URL again: {test_url} (new=1)")
    success2 = webbrowser.open(test_url, new=1, autoraise=True)
    print(f"   Result: {success2}")
    
    time.sleep(3)
    
    print(f"3. Opening SAME URL with new=0 (same window):")
    success3 = webbrowser.open(test_url, new=0, autoraise=True)
    print(f"   Result: {success3}")
    
    time.sleep(3)
    
    print(f"4. Opening SAME URL with new=2 (new tab):")
    success4 = webbrowser.open(test_url, new=2, autoraise=True)
    print(f"   Result: {success4}")
    
    print("\nObservations:")
    print("- Does webbrowser create new windows for same URL?")
    print("- Or does it reuse existing windows/tabs?")
    print("- Check your browser to see the actual behavior!")

if __name__ == "__main__":
    test_webbrowser_same_url()
