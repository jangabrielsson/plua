# Test script to verify FastAPI external access
# This script will help test if the FastAPI server accepts external connections

import requests
import socket
import time

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def test_fastapi_access():
    """Test FastAPI access on both localhost and local IP"""
    port = 8080
    local_ip = get_local_ip()
    
    print(f"Testing FastAPI access...")
    print(f"Local IP detected: {local_ip}")
    print()
    
    # Test URLs
    test_urls = [
        f"http://127.0.0.1:{port}/health",
        f"http://localhost:{port}/health", 
        f"http://{local_ip}:{port}/health"
    ]
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ SUCCESS - Server responds on {url}")
                data = response.json()
                print(f"  📊 Status: {data.get('status', 'unknown')}")
            else:
                print(f"  ⚠️  HTTP {response.status_code} - {url}")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ CONNECTION REFUSED - {url}")
        except requests.exceptions.Timeout:
            print(f"  ⏱️  TIMEOUT - {url}")
        except Exception as e:
            print(f"  ❌ ERROR - {url}: {e}")
        print()
    
    print("Instructions:")
    print("1. Start PLua with: plua your_script.lua")
    print("2. The server should now bind to 0.0.0.0:8080 (all interfaces)")
    print(f"3. External systems can connect to: http://{local_ip}:8080")
    print("4. If you need localhost-only, use: plua --api-host localhost your_script.lua")

if __name__ == "__main__":
    test_fastapi_access()
