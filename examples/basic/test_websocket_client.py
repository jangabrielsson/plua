#!/usr/bin/env python3
"""
Test WebSocket client to verify the server callbacks
"""
import websocket
import time
import sys


def test_websocket_server():
    print("Testing WebSocket server on localhost:8769...")
    
    try:
        # Connect to the server
        ws = websocket.create_connection("ws://localhost:8769")
        print("✓ Connected to WebSocket server")
        
        # Send a test message
        test_message = "Hello from Python client!"
        print(f"Sending message: {test_message}")
        ws.send(test_message)
        
        # Wait for response
        response = ws.recv()
        print(f"✓ Received response: {response}")
        
        # Send another message
        test_message2 = "Second message!"
        print(f"Sending second message: {test_message2}")
        ws.send(test_message2)
        
        # Wait for response
        response2 = ws.recv()
        print(f"✓ Received second response: {response2}")
        
        # Close connection
        ws.close()
        print("✓ Connection closed")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Wait a moment for the server to start
    print("Waiting 2 seconds for server to start...")
    time.sleep(2)
    
    success = test_websocket_server()
    if success:
        print("✓ WebSocket test completed successfully")
    else:
        print("✗ WebSocket test failed")
        sys.exit(1) 