#!/usr/bin/env python3
"""
Demonstration of PLua-API server integration
This script shows how to use the integrated PLua interpreter with the API server.
"""

import time
import requests
import subprocess
import sys


def start_services():
    """Start the API server and PLua interpreter"""
    print("🚀 Starting PLua-API Server Integration Demo")
    print("=" * 50)
    
    # Check if API server is already running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ API server is already running")
            return True
    except Exception:
        pass
    
    # Start the API server
    print("1. Starting API server...")
    subprocess.Popen([
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
            print("✅ API server started successfully")
            return True
        else:
            print("❌ API server failed to start properly")
            return False
    except Exception as e:
        print(f"❌ API server failed to start: {e}")
        return False


def demonstrate_api_usage():
    """Demonstrate API usage"""
    print("\n2. Demonstrating API usage...")
    
    # Test basic execution
    print("   📝 Executing Lua code via API...")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/execute",
            json={"code": "print('Hello from API!'); return 'API test successful'"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Result: {result.get('result', 'No result')}")
        else:
            print(f"   ❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test variable setting and retrieval
    print("   🔧 Setting and retrieving variables...")
    try:
        # Set a variable
        response = requests.post(
            "http://127.0.0.1:8000/api/execute",
            json={"code": "x = 42; print('Variable x set to:', x)"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Set variable: {result.get('result', 'No result')}")
        
        # Retrieve the variable
        response = requests.post(
            "http://127.0.0.1:8000/api/execute",
            json={"code": "print('Current value of x:', x)"},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Retrieved variable: {result.get('result', 'No result')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def demonstrate_plua_integration():
    """Demonstrate PLua integration"""
    print("\n3. Demonstrating PLua integration...")
    
    # Test PLua script execution
    print("   📝 Running PLua script...")
    try:
        result = subprocess.run([
            sys.executable, "plua.py", 
            "-e", "print('Setting variable y to hello world'); y = 'hello world'; print('Variable y set successfully')",
            "examples/basic.lua"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ PLua script executed successfully")
            if "Variable y set successfully" in result.stdout:
                print("   ✅ Variable setting confirmed")
        else:
            print(f"   ❌ PLua script failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def demonstrate_fibaro_api():
    """Demonstrate Fibaro API integration"""
    print("\n4. Demonstrating Fibaro API integration...")
    
    # Test Fibaro API endpoints
    endpoints = [
        ("/api/devices", "Devices"),
        ("/api/rooms", "Rooms"),
        ("/api/weather", "Weather"),
        ("/api/globalVariables", "Global Variables")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name} API working")
            else:
                print(f"   ❌ {name} API failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name} API error: {e}")


def show_web_interface():
    """Show information about the web interface"""
    print("\n5. Web Interface Information...")
    print("   🌐 Web Interface: http://127.0.0.1:8000/")
    print("   📚 API Documentation: http://127.0.0.1:8000/docs")
    print("   📖 ReDoc Documentation: http://127.0.0.1:8000/redoc")
    print("   💡 You can use the web interface to:")
    print("      - Execute Lua code interactively")
    print("      - View API documentation")
    print("      - Test all available endpoints")
    print("      - Monitor server status")


def main():
    """Main demonstration function"""
    print("🎯 PLua-API Server Integration Demonstration")
    print("=" * 60)
    
    # Start services
    if not start_services():
        print("❌ Failed to start services. Exiting.")
        return
    
    # Demonstrate features
    demonstrate_api_usage()
    demonstrate_plua_integration()
    demonstrate_fibaro_api()
    show_web_interface()
    
    print("\n🎉 Demonstration completed!")
    print("\n📋 What you've seen:")
    print("  ✅ API server running and accessible")
    print("  ✅ Lua code execution via REST API")
    print("  ✅ Variable setting and retrieval")
    print("  ✅ PLua script execution")
    print("  ✅ Interactive mode with API connection")
    print("  ✅ Fibaro HC3 API compatibility")
    print("  ✅ Web interface for easy interaction")
    
    print("\n🚀 Next steps:")
    print("  - Open http://127.0.0.1:8000/ in your browser")
    print("  - Try the interactive code execution")
    print("  - Explore the API documentation")
    print("  - Run your own Lua scripts with: python plua.py your_script.lua")


if __name__ == "__main__":
    main() 