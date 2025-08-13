-- Simple web server test
print("Simple Web Server Test")
print("======================")

-- Test server status
local status = _PY.get_web_server_status()
print("Initial server status:")
print("  Running: " .. tostring(status.running))

-- Start the server
print("Starting web server...")
local result = _PY.start_web_server("127.0.0.1", 8000)

print("Start result:")
print("  Success: " .. tostring(result.success))
print("  Message: " .. result.message)

if result.success then
    -- Wait for 5 seconds
    _PY.setTimeout(function()
        print("Stopping web server...")
        local stop_result = _PY.stop_web_server()
        print("Stop result:")
        print("  Success: " .. tostring(stop_result.success))
        print("  Message: " .. stop_result.message)
    end, 5000)
else
    print("Failed to start server")
end
