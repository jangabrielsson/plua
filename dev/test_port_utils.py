#!/usr/bin/env python3
"""
Simple test of port cleanup functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from plua2.api_server import cleanup_port, is_port_free
import socket
import time

def test_port_functions():
    """Test the port utility functions"""
    port = 8890  # Use a test port
    
    print("=== Testing Port Utility Functions ===")
    print()
    
    # Test 1: Check if port is free when actually free
    print(f"1. Testing is_port_free() on unused port {port}...")
    free = is_port_free(port)
    print(f"   Result: {free} (should be True)")
    
    # Test 2: Block the port and check again
    print(f"2. Blocking port {port} and testing again...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('127.0.0.1', port))
        sock.listen(1)
        
        free = is_port_free(port, "127.0.0.1")
        print(f"   Result: {free} (should be False)")
        
        # Test 3: Try cleanup function
        print(f"3. Testing cleanup_port() on blocked port {port}...")
        cleanup_result = cleanup_port(port, "127.0.0.1")
        print(f"   Cleanup result: {cleanup_result}")
        
        # Test 4: Check if port is free after cleanup
        print(f"4. Checking if port {port} is free after cleanup...")
        free_after = is_port_free(port, "127.0.0.1")
        print(f"   Result: {free_after} (should be True)")
        
    except Exception as e:
        print(f"   Error: {e}")
    finally:
        try:
            sock.close()
        except:
            pass
    
    print()
    print("=== Port Utility Test Complete ===")

if __name__ == "__main__":
    test_port_functions()
