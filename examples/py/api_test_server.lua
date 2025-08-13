-- Web API Test Server
print("Starting web API test server...")

local result = _PY.start_web_server("127.0.0.1", 8000)
if result.success then
    print("✓ Server started at http://127.0.0.1:8000")
    print("")
    print("Test these endpoints:")
    print("1. GET  http://127.0.0.1:8000/")
    print("2. GET  http://127.0.0.1:8000/status")
    print("3. POST http://127.0.0.1:8000/execute")
    print("4. GET  http://127.0.0.1:8000/engine/callbacks")
    print("")
    print("Server will run for 2 minutes...")
    
    print("Making test API calls...")
_PY.call_http("http://httpbin.org/get", {}, function(response, error)
    if error then
        print("❌ Error:", error)
    else
        print("✓ GET request succeeded")
    end
end)

-- Keep server running for 60 seconds
_PY.setTimeout(function()
    print("Stopping API test server...")
    _PY.stop_web_server()
    print("Test completed")
end, 60000)
else
    print("❌ Failed to start server: " .. result.message)
end
