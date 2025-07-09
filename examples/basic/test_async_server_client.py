#!/usr/bin/env python3
"""
Simple Python client to test the async TCP server
"""

import socket
import time
import sys


def test_async_server(host="127.0.0.1", port=8769):
    print(f"[PYTHON CLIENT] Testing async server on {host}:{port}")
    
    try:
        # Connect to the server
        print(f"[PYTHON CLIENT] Connecting to {host}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((host, port))
        print("[PYTHON CLIENT] ✓ Connected successfully")
        
        # Read welcome message
        welcome = sock.recv(1024).decode('utf-8')
        print(f"[PYTHON CLIENT] Received welcome: {welcome.strip()}")
        
        # Send some test messages
        test_messages = ["Hello", "World", "Test message", "Goodbye"]
        
        for msg in test_messages:
            print(f"[PYTHON CLIENT] Sending: {msg}")
            sock.send((msg + "\n").encode('utf-8'))
            
            # Read echo response
            response = sock.recv(1024).decode('utf-8')
            print(f"[PYTHON CLIENT] Received echo: {response.strip()}")
            
            time.sleep(0.5)
        
        # Close connection
        sock.close()
        print("[PYTHON CLIENT] ✓ Connection closed")
        
    except socket.timeout:
        print("[PYTHON CLIENT] ✗ Connection timeout")
    except ConnectionRefusedError:
        print("[PYTHON CLIENT] ✗ Connection refused - server not running")
    except Exception as e:
        print(f"[PYTHON CLIENT] ✗ Error: {e}")


if __name__ == "__main__":
    port = 8769
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    test_async_server(port=port) 