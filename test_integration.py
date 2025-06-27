#!/usr/bin/env python3
"""
Test script to demonstrate PLua-API server integration
"""

import time
import requests
import subprocess
import sys


def test_integration():
    """Test the PLua-API server integration"""
    
    # Start the API server
    print("Starting API server...")
    api_server = subprocess.Popen([
        sys.executable, "api_server.py", 
        "--host", "127.0.0.1", 
        "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ API server is running")
        else:
            print("✗ API server failed to start")
            return False
    except Exception as e:
        print(f"✗ API server failed to start: {e}")
        return False
    
    # Start PLua in interactive mode (this will register with the API server)
    print("Starting PLua in interactive mode...")
    plua_process = subprocess.Popen([
        sys.executable, "plua.py", "-i"
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Wait a moment for PLua to start and register
    time.sleep(2)
    
    # Test if we can execute code via the API server
    print("Testing API execution...")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/execute",
            json={"code": "print('Hello from API!'); return 'API test successful'"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ API execution successful")
                print(f"  Result: {result.get('result')}")
            else:
                print(f"✗ API execution failed: {result.get('error')}")
        else:
            print(f"✗ API request failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ API execution test failed: {e}")
    
    # Test setting a variable in PLua and accessing it via API
    print("Testing variable persistence...")
    try:
        # Set a variable
        response = requests.post(
            "http://127.0.0.1:8000/api/execute",
            json={"code": "test_var = 42; print('Variable set to:', test_var)"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ Variable set successfully")
                
                # Try to access the variable
                response2 = requests.post(
                    "http://127.0.0.1:8000/api/execute",
                    json={"code": "print('Variable value:', test_var); return test_var"},
                    timeout=10
                )
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    if result2.get("success"):
                        print("✓ Variable access successful")
                        print(f"  Variable value: {result2.get('result')}")
                    else:
                        print(f"✗ Variable access failed: {result2.get('error')}")
                else:
                    print(f"✗ Variable access request failed: {response2.status_code}")
            else:
                print(f"✗ Variable setting failed: {result.get('error')}")
        else:
            print(f"✗ Variable setting request failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Variable persistence test failed: {e}")
    
    # Cleanup
    print("Cleaning up...")
    if plua_process:
        plua_process.terminate()
        plua_process.wait()
    
    if api_server:
        api_server.terminate()
        api_server.wait()
    
    print("Integration test completed!")


if __name__ == "__main__":
    test_integration() 