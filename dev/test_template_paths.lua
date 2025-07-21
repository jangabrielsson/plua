-- Test script to demonstrate template path functionality

print("Testing template path functionality...")

-- Set up a Fibaro API hook that shows all received parameters
_PY.fibaro_api_hook = function(method, path, path_params, query_params, data)
    print("\n=== Fibaro API Hook Called ===")
    print("Method:", method)
    print("Template Path:", path)
    
    if path_params then
        print("Path Params:")
        for k, v in pairs(path_params) do
            print("  " .. k .. " = " .. tostring(v))
        end
    else
        print("Path Params: None")
    end
    
    if query_params then
        print("Query Params:")
        for k, v in pairs(query_params) do
            print("  " .. k .. " = " .. tostring(v))
        end
    else
        print("Query Params: None")
    end
    
    if data then
        print("Body Data:", data)
    else
        print("Body Data: None")
    end
    
    -- Return sample data based on the template path
    if path == "/api/devices/{deviceID}" then
        return {id = path_params.deviceID, name = "Test Device", type = "com.fibaro.binarySwitch"}, 200
    elseif path == "/api/devices" then
        return {{id = 1, name = "Device 1"}, {id = 2, name = "Device 2"}}, 200
    else
        return {error = "Unhandled endpoint: " .. path}, 404
    end
end

print("\n1. Testing internal call to /api/devices/123")
local result1 = _PY.http_call_internal("GET", "http://localhost:8888/api/devices/123")
print("Result1:", result1)

print("\n2. Testing internal call to /api/devices with query params")
local result2 = _PY.http_call_internal("GET", "http://localhost:8888/api/devices?limit=10&offset=0")
print("Result2:", result2)

print("\n3. Testing external call to /api/devices/456")
local result3 = _PY.http_call_sync("GET", "http://localhost:8888/api/devices/456")
print("Result3:", result3)

print("\nTemplate path testing complete!")
