#!/usr/bin/env python3
"""
Test the window cleanup functionality by creating artificial stale entries
"""

import json
import os
from datetime import datetime, timedelta

def create_test_state():
    """Create a test state file with both fresh and stale entries."""
    
    state_file = os.path.expanduser("~/.plua/windows.json")
    
    # Create timestamps
    now = datetime.now()
    old_time = now - timedelta(minutes=15)  # 15 minutes ago (stale)
    recent_time = now - timedelta(minutes=5)  # 5 minutes ago (fresh)
    
    test_state = {
        "stale_window_1": {
            "window_id": "stale_window_1",
            "url": "http://localhost:8080/stale1",
            "width": 400,
            "height": 300,
            "x": 100,
            "y": 100,
            "created_at": old_time.isoformat()
        },
        "stale_window_2": {
            "window_id": "stale_window_2", 
            "url": "http://localhost:8080/stale2",
            "width": 400,
            "height": 300,
            "x": 200,
            "y": 200,
            "created_at": old_time.isoformat()
        },
        "fresh_window": {
            "window_id": "fresh_window",
            "url": "http://localhost:8080/fresh", 
            "width": 400,
            "height": 300,
            "x": 300,
            "y": 300,
            "created_at": recent_time.isoformat()
        },
        "no_timestamp_window": {
            "window_id": "no_timestamp_window",
            "url": "http://localhost:8080/no_timestamp",
            "width": 400,
            "height": 300,
            "x": 400,
            "y": 400
            # No created_at field - should be treated as stale
        }
    }
    
    # Save test state
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump(test_state, f, indent=2)
    
    print(f"Created test state file with:")
    print(f"- 2 stale windows (15 minutes old)")
    print(f"- 1 fresh window (5 minutes old)")
    print(f"- 1 window without timestamp")
    print(f"\nState file: {state_file}")

if __name__ == "__main__":
    create_test_state()
