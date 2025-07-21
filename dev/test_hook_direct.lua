-- Direct test of the fibaro_api_hook function

print("Testing fibaro_api_hook directly...")

-- Set up the hook
_PY.fibaro_api_hook = function(method, path, data)
    print("=== FIBARO API HOOK ===")
    print("Method:", method)
    print("Path:", path)
    print("Data:", data)
    print("=======================")
    
    return {
        message = "Success",
        method = method,
        path = path,
        data = data
    }
end

-- Test it directly
print("\n1. Testing GET /api/devices")
local result1 = _PY.fibaro_api_hook("GET", "/api/devices", "")
print("Result:", result1.message)

print("\n2. Testing POST /api/devices with data")
local result2 = _PY.fibaro_api_hook("POST", "/api/devices", '{"name":"Test Device"}')
print("Result:", result2.message)

print("\n3. Testing GET /api/devices/123?param=value")
local result3 = _PY.fibaro_api_hook("GET", "/api/devices/123?param=value", "")
print("Result:", result3.message)

print("\nDirect testing complete!")
