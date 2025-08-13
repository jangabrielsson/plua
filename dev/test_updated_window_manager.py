#!/usr/bin/env python3
"""
Test the updated EPLua window manager with new Safari window creation.
"""

import sys
import os

# Add src to path so we can import eplua modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from plua.window_manager import get_window_manager
import time

def test_new_window_behavior():
    """Test if the updated window manager creates actual new windows"""
    
    print("=== Testing Updated EPLua Window Manager ===")
    
    window_manager = get_window_manager()
    
    # Test 1: Create first window
    print("\n1. Creating first QuickApp window...")
    success1 = window_manager.create_window(
        window_id="test_qa_1001",
        url="http://localhost:8080/static/quickapp_ui.html?qa_id=1001&desktop=true",
        width=600,
        height=400,
        x=100,
        y=100
    )
    print(f"Window 1 creation result: {success1}")
    
    # Wait for window to open
    time.sleep(3)
    
    # Test 2: Create second window with different QA ID (should be new window)
    print("\n2. Creating second QuickApp window (different QA)...")
    success2 = window_manager.create_window(
        window_id="test_qa_1002",
        url="http://localhost:8080/static/quickapp_ui.html?qa_id=1002&desktop=true",
        width=600,
        height=400,
        x=200,
        y=200
    )
    print(f"Window 2 creation result: {success2}")
    
    # Wait for window to open
    time.sleep(3)
    
    # Test 3: Try to create another window with same QA ID (should reuse)
    print("\n3. Creating window with same QA ID (should reuse)...")
    success3 = window_manager.create_window(
        window_id="test_qa_1001",
        url="http://localhost:8080/static/quickapp_ui.html?qa_id=1001&desktop=true",
        width=700,
        height=500,
        x=300,
        y=300
    )
    print(f"Window 3 creation result (should reuse): {success3}")
    
    # List all windows
    print("\n4. Listing all managed windows:")
    windows = window_manager.list_windows()
    for window_id, info in windows.items():
        print(f"  {window_id}: {info['url']} ({info['width']}x{info['height']})")
    
    print("\n=== Test Results ===")
    print("Check Safari:")
    print("- Are there 2 separate Safari windows open?")
    print("- Each window should show a different QuickApp (1001 vs 1002)")
    print("- The third call should have reused the first window")
    
    # Keep windows open for observation
    print("\nWindows will stay open for 15 seconds for observation...")
    time.sleep(15)
    
    # Cleanup
    print("\nCleaning up...")
    window_manager.close_all_windows()
    print("Test complete!")

if __name__ == "__main__":
    test_new_window_behavior()
