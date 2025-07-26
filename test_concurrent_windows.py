#!/usr/bin/env python3
"""
Test concurrent window creation to simulate the Windows issue
"""

import sys
import os
import time
import threading
from pathlib import Path

# Add plua to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from plua.desktop_ui import DesktopUIManager

def create_windows_concurrently():
    """Test creating multiple windows concurrently"""
    
    # Clean up any existing registry
    registry_file = Path.home() / ".plua" / "window_registry.json"
    if registry_file.exists():
        registry_file.unlink()
        print("Cleaned up existing registry")
    
    manager = DesktopUIManager()
    
    def create_window_worker(qa_id):
        """Worker function to create a window"""
        try:
            print(f"Thread {qa_id}: Starting window creation")
            window_id = manager.create_quickapp_window(
                qa_id=qa_id, 
                title=f"Test Window {qa_id}",
                width=400, 
                height=300,
                x=100 + qa_id * 50,
                y=100 + qa_id * 50
            )
            print(f"Thread {qa_id}: Created window {window_id}")
            return window_id
        except Exception as e:
            print(f"Thread {qa_id}: Error creating window: {e}")
            return None
    
    # Create multiple threads to simulate concurrent window creation
    threads = []
    qa_ids = [5555, 5556, 5557, 5558, 5559, 5560]
    
    print(f"Starting {len(qa_ids)} concurrent window creation threads...")
    
    for qa_id in qa_ids:
        thread = threading.Thread(target=create_window_worker, args=(qa_id,))
        threads.append(thread)
        thread.start()
        # Small delay between thread starts to stagger them slightly
        time.sleep(0.01)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("\nAll threads completed")
    
    # Check the registry
    try:
        registry = manager._load_registry()
        print(f"\nRegistry contents:")
        print(f"Windows: {len(registry.get('windows', {}))}")
        print(f"Positions: {len(registry.get('positions', {}))}")
        
        for window_id, window_info in registry.get('windows', {}).items():
            qa_id = window_info.get('qa_id', 'unknown')
            print(f"  {window_id}: QA {qa_id}")
            
    except Exception as e:
        print(f"Error reading registry: {e}")

if __name__ == "__main__":
    print("Testing concurrent window creation...")
    create_windows_concurrently()
    print("Test completed")
