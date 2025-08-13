#!/usr/bin/env python3
"""
EPLua GUI Launcher

This script starts both the EPLua server and GUI in a coordinated way.
On macOS, this ensures the GUI runs on the main thread while the server 
runs in a background thread.
"""

import sys
import os
import threading
import time
import subprocess
import signal

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def start_eplua_server(script_path="examples/gui_demo.lua"):
    """Start the EPLua server in a background process."""
    try:
        # Start EPLua server as a subprocess
        cmd = [sys.executable, "-m", "eplua.cli", script_path]
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"🚀 EPLua server starting (PID: {process.pid})...")
        
        # Monitor server output in a separate thread
        def monitor_output():
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    print(f"[SERVER] {line.strip()}")
        
        output_thread = threading.Thread(target=monitor_output, daemon=True)
        output_thread.start()
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting EPLua server: {e}")
        return None

def wait_for_server(max_wait=10):
    """Wait for the EPLua server to be ready."""
    import requests
    
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8000/status", timeout=1)
            if response.status_code == 200:
                print("✅ EPLua server is ready!")
                return True
        except:
            pass
        
        print(f"⏳ Waiting for server... ({i+1}/{max_wait})")
        time.sleep(1)
    
    print("❌ Server not responding after 10 seconds")
    return False

def start_gui():
    """Start the EPLua GUI on the main thread."""
    try:
        from plua.gui import EPLuaGUI
        print("🖥️  Starting EPLua GUI...")
        gui = EPLuaGUI()
        gui.run()  # This blocks until GUI is closed
        print("👋 GUI closed")
        
    except ImportError as e:
        print(f"❌ Cannot import GUI: {e}")
        print("💡 Make sure eplua is installed: pip install -e .")
        return False
    except Exception as e:
        print(f"❌ GUI error: {e}")
        return False
    
    return True

def main():
    """Main application entry point."""
    print("🎮 EPLua GUI Launcher")
    print("=" * 40)
    
    server_process = None
    
    try:
        # Start the EPLua server in background
        server_process = start_eplua_server()
        if not server_process:
            return 1
        
        # Wait for server to be ready
        if not wait_for_server():
            return 1
        
        print("\n🎯 Both server and GUI are ready!")
        print("📡 Server: http://localhost:8000")
        print("🖱️  GUI: Opening now...\n")
        
        # Start GUI on main thread (this will block)
        start_gui()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        # Clean up server process
        if server_process:
            print("🧹 Stopping EPLua server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("✅ Server stopped")
    
    return 0

if __name__ == "__main__":
    exit(main())
