print("Web Server Demo")
print("==============")
print()

-- Start the web server
print("Starting web server...")
local success, message = _PY.start_web_server(8080, "0.0.0.0")
print("Start result:", success, message)
print()

-- Check server status
local status = _PY.get_web_server_status()
print("Server status:")
print("  Running:", status.running)
print("  Port:", status.port)
print("  Host:", status.host)
print("  Process ID:", status.process_id)
print()

-- Register a callback for HTTP requests
print("Registering HTTP request callback...")
local function handle_http_request(request)
    print("=== HTTP Request Received ===")
    print("Method:", request.method)
    print("Path:", request.path)
    print("Query params:", _PY.to_json(request.query))
    print("Headers:", _PY.to_json(request.headers))
    if request.body then
        print("Body:", _PY.to_json(request.body))
    end
    print("============================")
    print()
end

_PY.register_web_callback("http_request", handle_http_request)
print("Callback registered!")
print()

-- Start message processing
print("Starting message processing...")
_PY.start_web_message_processing()
print("Message processing started!")
print()

print("Web server is now running and listening for HTTP requests.")
print("You can test it with:")
print("  curl http://localhost:8080/test")
print("  curl -X POST http://localhost:8080/api -H 'Content-Type: application/json' -d '{key:value}'")
print()
print("Press Ctrl+C to stop...")

-- Keep the script running to receive requests
while true do
    -- Check for messages manually as well
    local message = _PY.get_web_server_message()
    if message then
        print("Manual message check received:", _PY.to_json(message))
    end
    
    -- Sleep a bit
    _PY.sleep(1000)  -- 1 second
end 