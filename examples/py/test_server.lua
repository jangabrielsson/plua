-- Server for testing endpoints
print("Starting web server for testing...")

local result = _PY.start_web_server("127.0.0.1", 8000)
if result.success then
    print("✓ Server started at http://127.0.0.1:8000")
    
    -- Keep server running for 60 seconds
    _PY.setTimeout(function()
        print("Stopping server...")
        _PY.stop_web_server()
    end, 60000)
else
    print("❌ Failed to start server: " .. result.message)
end
