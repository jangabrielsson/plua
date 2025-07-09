#!/usr/bin/env python3
"""
Python client for testing PLua synchronous TCP server
Runs in a separate thread and echoes back messages from the server
"""

import socket
import threading
import time
import sys


def echo_client(host="127.0.0.1", port=8768):
    """Echo client that connects to server and echoes back messages"""
    print(f"[PYTHON CLIENT] Starting echo client, connecting to {host}:{port}")
    
    try:
        # Create socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        sock.connect((host, port))
        print("[PYTHON CLIENT] ✓ Connected to server")
        
        # Echo loop
        while True:
            try:
                # Read message from server
                data = sock.recv(1024)
                if not data:
                    print("[PYTHON CLIENT] Server closed connection")
                    break
                
                message = data.decode('utf-8')
                print(f"[PYTHON CLIENT] ✓ Received: {message.strip()}")
                
                # Echo back the message
                echo_response = f"ECHO: {message.strip()}\n"
                sock.send(echo_response.encode('utf-8'))
                print(f"[PYTHON CLIENT] ✓ Echoed back: {echo_response.strip()}")
                
            except socket.timeout:
                print("[PYTHON CLIENT] Read timeout, continuing...")
                continue
            except Exception as e:
                print(f"[PYTHON CLIENT] Error in echo loop: {e}")
                break
                
    except Exception as e:
        print(f"[PYTHON CLIENT] ✗ Failed to connect: {e}")
    finally:
        try:
            sock.close()
            print("[PYTHON CLIENT] Connection closed")
        except Exception:
            pass


def start_echo_client_thread(host="127.0.0.1", port=8768, delay=1.0):
    """Start echo client in a separate thread"""
    print(f"[PYTHON CLIENT] Starting echo client thread in {delay} seconds...")
    
    def delayed_start():
        time.sleep(delay)
        echo_client(host, port)
    
    thread = threading.Thread(target=delayed_start, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    # If run directly, start the echo client
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8768
    
    echo_client("127.0.0.1", port) 