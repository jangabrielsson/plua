#!/usr/bin/env python3
"""
Simple test server for blocking timeout tests
Accepts connections but doesn't send data
"""

import socket
import time
import sys


def test_server(port=8888):
    """Start a test server that accepts connections but doesn't send data"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', port))
    server.listen(5)  # Allow multiple pending connections
    print(f"Test server listening on localhost:{port}")

    try:
        while True:
            conn, addr = server.accept()
            print(f"Client connected from {addr}")
            # Don't send any data, just keep connection open
            time.sleep(10)  # Keep connection open for 10 seconds
            conn.close()
            print("Connection closed")
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    test_server(port)
