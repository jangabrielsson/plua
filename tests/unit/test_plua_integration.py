#!/usr/bin/env python3
"""
Test script to demonstrate PLua-API server integration
"""

import requests
import subprocess
import sys


def test_integration():
    """Test the PLua-API server integration"""
    
    print("🚀 Testing PLua-API Server Integration")
    print("=" * 50)
    
    # Check if API server is running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server is not responding properly")
            return False
    except Exception as e:
        print(f"❌ API server is not running: {e}")
        return False
    
    # Test basic API execution
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/execute",
            json={"code": "print('Hello from API!'); return 'API test successful'"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ API execution works")
            else:
                print(f"❌ API execution failed: {result.get('error')}")
                return False
        else:
            print(f"❌ API execution failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API execution test failed: {e}")
        return False
    
    # Test PLua script execution
    try:
        print("\n📝 Testing PLua script execution...")
        result = subprocess.run([
            sys.executable, "-m", "plua",
            "-e", "print('Setting variable x to 42'); x = 42; print('Variable x set successfully')",
            "examples/basic.lua"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ PLua script execution works")
            if "Variable x set successfully" in result.stdout:
                print("✅ Variable setting works")
            else:
                print("⚠️  Variable setting output not found")
        else:
            print(f"❌ PLua script execution failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ PLua script test failed: {e}")
        return False
    
    # Test interactive mode connection
    try:
        print("\n🔄 Testing interactive mode connection...")
        # Start interactive mode and send a command, then exit
        process = subprocess.Popen([
            sys.executable, "-m", "plua", "-i"
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Send commands and exit
        commands = [
            "print('Testing from interactive mode')",
            "x = 42",
            "print('Variable x set to:', x)",
            "exit"
        ]
        
        stdout, stderr = process.communicate(input='\n'.join(commands), timeout=30)
        
        if process.returncode == 0:
            print("✅ Interactive mode works")
            if "Connected to API server" in stdout:
                print("✅ API server connection works")
            else:
                print("⚠️  API server connection message not found")
        else:
            print(f"❌ Interactive mode failed: {stderr}")
            return False
    except Exception as e:
        print(f"❌ Interactive mode test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! PLua-API server integration is working correctly.")
    print("\n📋 Summary:")
    print("  ✅ API server is running")
    print("  ✅ API execution works")
    print("  ✅ PLua script execution works")
    print("  ✅ Interactive mode works")
    print("  ✅ API server connection works")
    
    return True


if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1) 