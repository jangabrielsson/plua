#!/usr/bin/env python3
"""
Test script to verify Ctrl+C handling in plua interactive mode
"""
import subprocess
import signal
import time
import sys

def test_ctrl_c():
    """Test that plua responds to Ctrl+C in interactive mode"""
    print("Starting plua in interactive mode...")
    
    # Start plua process
    proc = subprocess.Popen([
        sys.executable, "-m", "plua", "--fibaro", "-i", "examples/fibaro/QA_basic.lua"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Give it time to start up
    time.sleep(3)
    
    print("Sending SIGINT (Ctrl+C)...")
    
    # Send SIGINT
    proc.send_signal(signal.SIGINT)
    
    # Wait for it to terminate
    try:
        stdout, _ = proc.communicate(timeout=5)
        print("Process terminated successfully")
        print("Exit code:", proc.returncode)
        print("Output (last few lines):")
        lines = stdout.strip().split('\n')
        for line in lines[-10:]:
            print("  ", line)
        
        if "REPL interrupted" in stdout or "Received signal" in stdout:
            print("✅ Ctrl+C handling is working correctly")
            return True
        else:
            print("❌ Expected interrupt messages not found")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Process did not terminate within timeout - hanging!")
        proc.kill()
        proc.wait()
        return False

if __name__ == "__main__":
    success = test_ctrl_c()
    sys.exit(0 if success else 1)
