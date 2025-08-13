#!/usr/bin/env python3
"""
Simple test script for update_view endpoint
Avoids shell quoting issues by using Python requests directly
"""

import requests
import json
import time

def test_updateview_endpoint():
    """Test the updateView endpoint with proper request formatting"""
    
    base_url = "http://localhost:8081"
    
    # Test data
    test_data = {
        "qa_id": 5555,
        "element_id": "lbl1", 
        "property_name": "text",
        "value": f"Updated at {time.strftime('%H:%M:%S')}"
    }
    
    print(f"Testing updateView endpoint at {base_url}")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Test the updateView endpoint
        response = requests.post(
            f"{base_url}/api/plugins/updateView",
            json=test_data,
            timeout=5
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.text:
            print(f"Response body: {response.text}")
        else:
            print("Response body: (empty)")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server not running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_updateview_endpoint()
    print(f"\n{'✅ Test passed' if success else '❌ Test failed'}")
