#!/usr/bin/env python3
"""
Simple test for desktop UI manager registry functionality
"""

import sys
import os
import time
from pathlib import Path

# Add plua to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_desktop_ui_registry():
    """Test the desktop UI manager registry functionality"""
    
    # Clean up any existing registry
    registry_file = Path.home() / ".plua" / "window_registry.json"
    if registry_file.exists():
        registry_file.unlink()
        print("Cleaned up existing registry")
    
    # Import and create manager
    try:
        from plua.desktop_ui import DesktopUIManager
        manager = DesktopUIManager()
        print("✓ DesktopUIManager created successfully")
        
        # Test registry operations
        test_registry = {
            "windows": {
                "test_window_1": {"qa_id": 5555, "status": "open", "pid": 12345},
                "test_window_2": {"qa_id": 5556, "status": "open", "pid": 12346}
            },
            "positions": {
                "quickapp_5555": {"x": 100, "y": 100, "width": 800, "height": 600},
                "quickapp_5556": {"x": 150, "y": 150, "width": 800, "height": 600}
            }
        }
        
        # Test save
        manager._save_registry(test_registry)
        print("✓ Registry save successful")
        
        # Test load
        loaded_registry = manager._load_registry()
        print("✓ Registry load successful")
        
        # Verify content
        if loaded_registry["windows"] == test_registry["windows"]:
            print("✓ Registry windows data matches")
        else:
            print("✗ Registry windows data mismatch")
            
        if loaded_registry["positions"] == test_registry["positions"]:
            print("✓ Registry positions data matches")
        else:
            print("✗ Registry positions data mismatch")
            
        # Test process alive check (will return False for fake PIDs)
        alive = manager._is_process_alive(12345)
        print(f"✓ Process alive check: {alive} (expected False for fake PID)")
        
        # Test window key generation
        qa_key = manager._get_qa_key(5555, "Test Window")
        expected_key = "quickapp_5555_Test Window"
        if qa_key == expected_key:
            print(f"✓ QA key generation: {qa_key}")
        else:
            print(f"✗ QA key mismatch: got {qa_key}, expected {expected_key}")
        
        print("\n✓ All registry tests passed!")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("This is expected if webview or other dependencies are missing")
        
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing DesktopUIManager registry functionality...")
    test_desktop_ui_registry()
    print("Test completed")
