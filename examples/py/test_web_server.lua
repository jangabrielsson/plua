-- Example: Web Server Integration
-- This script demonstrates how to start a web server and interact with it

print("EPLua Web Server Example")
print("========================")

-- Start the web server
print("Starting web server...")
local server_result = _PY.start_web_server("127.0.0.1", 8000)

if server_result.success then
    print("✓ Web server started successfully!")
    print("  URL: " .. server_result.server_info.url)
    print("  Host: " .. server_result.server_info.host)
    print("  Port: " .. server_result.server_info.port)
    print("")
    
    print("Available endpoints:")
    print("  GET  /           - Root endpoint")
    print("  GET  /status     - Server and engine status")
    print("  POST /execute    - Execute Lua scripts")
    print("  GET  /engine/callbacks - View active callbacks")
    print("")
    
    -- Set up some timers and intervals to make the status more interesting
    print("Setting up some background operations...")
    
    -- Timer that fires after 5 seconds
    _PY.setTimeout(function()
        print("⏰ Timer fired after 5 seconds")
    end, 5000)
    
    -- Interval that fires every 3 seconds
    local interval_id = _PY.setInterval(function()
        print("🔄 Interval tick every 3 seconds")
    end, 3000)
    
    -- HTTP request to test network functionality
    _PY.call_http("https://api.github.com/repos/python/cpython", {}, function(response, error)
        if error then
            print("❌ HTTP request failed: " .. error)
        else
            print("✓ HTTP request completed successfully")
            print("  Repository: " .. (response.body.full_name or "unknown"))
            print("  Stars: " .. (response.body.stargazers_count or "unknown"))
        end
    end)
    
    print("")
    print("Try these curl commands in another terminal:")
    print("")
    print("# Get server status:")
    print("curl http://127.0.0.1:8000/status")
    print("")
    print("# Execute a simple Lua script:")
    print("curl -X POST http://127.0.0.1:8000/execute \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"script\": \"return {message = \\\"Hello from Lua!\\\", time = os.time()}\"}'")
    print("")
    print("# Get active callbacks:")
    print("curl http://127.0.0.1:8000/engine/callbacks")
    print("")
    
    -- Keep the server running for a while
    print("Server will run for 30 seconds...")
    _PY.setTimeout(function()
        print("⏹️  Stopping web server...")
        local stop_result = _PY.stop_web_server()
        if stop_result.success then
            print("✓ Web server stopped")
        else
            print("❌ Failed to stop web server: " .. stop_result.message)
        end
        
        -- Clear the interval
        _PY.clearInterval(interval_id)
        print("Script completed")
    end, 30000)
    
else
    print("❌ Failed to start web server: " .. server_result.message)
end
