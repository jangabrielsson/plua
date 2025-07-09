#!/usr/bin/env python3
"""
External System Client Example
This demonstrates how an external system would connect to the PLua synchronous API server
"""

import socket
import time
import threading


class ExternalSystemClient:
    def __init__(self, host="127.0.0.1", port=8767):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = False
        
    def connect(self):
        """Connect to the PLua synchronous API server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"[EXTERNAL] Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[EXTERNAL] Failed to connect: {e}")
            return False
    
    def send_response(self, message):
        """Send a response to PLua"""
        if not self.connected:
            print("[EXTERNAL] Not connected")
            return False
        
        try:
            self.socket.send(message.encode('utf-8'))
            print(f"[EXTERNAL] Sent: {message.strip()}")
            return True
        except Exception as e:
            print(f"[EXTERNAL] Failed to send: {e}")
            self.connected = False
            return False
    
    def read_loop(self):
        """Read messages from PLua and respond"""
        while self.running and self.connected:
            try:
                # Read a line from PLua
                data = self.socket.recv(1024)
                if not data:
                    print("[EXTERNAL] Connection closed by server")
                    break
                
                message = data.decode('utf-8').strip()
                print(f"[EXTERNAL] Received: {message}")
                
                # Send appropriate response based on message
                if "Hello" in message:
                    response = "Hello back from external system!\n"
                elif "How are you" in message:
                    response = "I'm doing great, thanks for asking!\n"
                elif "STATUS" in message:
                    response = "STATUS: OK, all systems operational\n"
                else:
                    response = f"Unknown command: {message}\n"
                
                self.send_response(response)
                
            except Exception as e:
                print(f"[EXTERNAL] Read error: {e}")
                break
        
        self.connected = False
    
    def start(self):
        """Start the external system client"""
        if not self.connect():
            return False
        
        self.running = True
        
        # Start read loop in a separate thread
        read_thread = threading.Thread(target=self.read_loop)
        read_thread.daemon = True
        read_thread.start()
        
        print("[EXTERNAL] External system client started")
        return True
    
    def stop(self):
        """Stop the external system client"""
        self.running = False
        if self.socket:
            self.socket.close()
        self.connected = False
        print("[EXTERNAL] External system client stopped")


def main():
    """Main function to run the external system client"""
    print("[EXTERNAL] Starting External System Client")
    print("[EXTERNAL] This simulates an external system connecting to PLua")
    
    client = ExternalSystemClient()
    
    try:
        if client.start():
            print("[EXTERNAL] Client running. Press Ctrl+C to stop.")
            
            # Keep running until interrupted
            while client.connected:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n[EXTERNAL] Interrupted by user")
    finally:
        client.stop()


if __name__ == "__main__":
    main() 