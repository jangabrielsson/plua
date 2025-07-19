#!/usr/bin/env python3
"""
Test script to demonstrate port cleanup functionality
"""

import socket
import time
import subprocess
import sys
import os

def test_port_cleanup():
    """Test the port cleanup functionality"""
    port = 8889  # Use a different port for testing
    
    print("=== Testing Port Cleanup Functionality ===")
    print()
    
    # Step 1: Start a simple server to block the port
    print(f"1. Starting a simple server on port {port}...")
    
    # Create a simple blocking server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('127.0.0.1', port))
        sock.listen(1)
        print(f"   Server is now listening on port {port}")
        
        # Fork a process to keep the server running
        if os.fork() == 0:
            # Child process - keep the server running
            try:
                print(f"   Child process blocking port {port}")
                time.sleep(5)  # Block for 5 seconds
            finally:
                sock.close()
                sys.exit(0)
        else:
            # Parent process
            sock.close()  # Parent doesn't need the socket
            time.sleep(1)  # Give child time to start
            
            print(f"2. Port {port} should now be in use...")
            
            # Verify port is in use
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(1)
            result = test_sock.connect_ex(('127.0.0.1', port))
            test_sock.close()
            
            if result == 0:
                print(f"   ✓ Port {port} is confirmed to be in use")
            else:
                print(f"   ✗ Port {port} appears to be free (unexpected)")
                return
            
            print(f"3. Starting plua2 with API on port {port} (should trigger cleanup)...")
            
            # Try to start plua2 with the same port
            cmd = [sys.executable, "-m", "plua2", "--api", str(port), "-e", "print('Port cleanup test')"]
            
            try:
                # Start plua2 - it should clean up the port and start successfully
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.getcwd()
                )
                
                # Give it time to start and potentially clean up the port
                time.sleep(3)
                
                # Check if plua2 is running
                if process.poll() is None:
                    print(f"   ✓ plua2 successfully started on port {port} (port cleanup worked!)")
                    
                    # Test that the API is working
                    test_api_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_api_sock.settimeout(1)
                    api_result = test_api_sock.connect_ex(('127.0.0.1', port))
                    test_api_sock.close()
                    
                    if api_result == 0:
                        print(f"   ✓ API server is responding on port {port}")
                    else:
                        print(f"   ✗ API server is not responding on port {port}")
                    
                    # Clean shutdown
                    process.terminate()
                    process.wait(timeout=5)
                else:
                    stdout, stderr = process.communicate()
                    print(f"   ✗ plua2 failed to start:")
                    print(f"      stdout: {stdout}")
                    print(f"      stderr: {stderr}")
                    
            except Exception as e:
                print(f"   ✗ Error starting plua2: {e}")
    
    except Exception as e:
        print(f"Error in test: {e}")
        sock.close()
    
    print()
    print("=== Port Cleanup Test Complete ===")

if __name__ == "__main__":
    test_port_cleanup()
