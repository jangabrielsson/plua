-- Test script for the new typed Fibaro API
print("Testing typed Fibaro API endpoints...")

-- Set up a simple API hook
_PY.fibaro_api_hook = function(method, path, data)
    print("API Hook called:")
    print("  Method:", method)
    print("  Path:", path)
    print("  Data:", data)
    
    -- Simple device list response
    if path:match("/api/devices") and method == "GET" then
        return {
            {id = 1, name = "Test Device 1", type = "light"},
            {id = 2, name = "Test Device 2", type = "sensor"}
        }
    end
    
    -- Simple scene response
    if path:match("/api/scenes") and method == "GET" then
        return {
            {id = 10, name = "Good Morning", enabled = true},
            {id = 11, name = "Good Night", enabled = true}
        }
    end
    
    -- Default response
    return {success = true, message = "API endpoint handled"}
end

print("API hook registered. Ready for testing.")
print("Try: curl http://localhost:8888/api/devices")
print("Try: curl http://localhost:8888/api/scenes")
