# Test script to verify Windows subprocess encoding fix
# This simulates the conditions that caused the UnicodeDecodeError

import subprocess
import sys

def test_subprocess_encoding():
    """Test subprocess calls with proper encoding handling"""
    try:
        print("Testing Windows netstat command with proper encoding...")
        
        # This is the same command that was causing issues
        result = subprocess.run(
            ["netstat", "-ano", "-p", "TCP"], 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='replace',  # This will replace problematic characters instead of crashing
            check=False
        )
        
        if result.returncode == 0:
            print("✅ Success! Command executed without encoding errors")
            print(f"Output length: {len(result.stdout)} characters")
            # Check if we can process the output
            lines = result.stdout.split('\n')
            print(f"Total lines: {len(lines)}")
            
            # Look for listening ports
            listening_ports = [line for line in lines if "LISTENING" in line]
            print(f"Found {len(listening_ports)} listening ports")
            
        else:
            print(f"⚠️ Command returned non-zero exit code: {result.returncode}")
            
    except UnicodeDecodeError as e:
        print(f"❌ UnicodeDecodeError still occurs: {e}")
    except Exception as e:
        print(f"❌ Other error: {e}")

if __name__ == "__main__":
    test_subprocess_encoding()
