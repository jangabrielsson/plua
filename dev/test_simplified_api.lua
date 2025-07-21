-- Test script for the simplified API

print("Testing simplified Fibaro API...")

-- First, load the demo hook
dofile("dev/demo_api_hook.lua")

-- Now test some internal calls if that function still exists
if _PY.http_call_sync then
    print("\n1. Testing GET /api/devices")
    local result1 = _PY.http_call_sync("GET", "http://localhost:8888/api/devices")
    if result1 then
        print("Result:", result1)
    else
        print("No result")
    end

    print("\n2. Testing GET /api/devices/123")
    local result2 = _PY.http_call_sync("GET", "http://localhost:8888/api/devices/123")
    if result2 then
        print("Result:", result2)
    else
        print("No result")
    end

    print("\n3. Testing GET /api/rooms")
    local result3 = _PY.http_call_sync("GET", "http://localhost:8888/api/rooms")
    if result3 then
        print("Result:", result3)
    else
        print("No result")
    end
else
    print("http_call_sync not available")
end

print("\nDone testing simplified API!")
