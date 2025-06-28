print("Web Server Status Demo")
print("=====================")
print()

-- Global state for the status page
local system_status = {
    uptime = 0,
    requests_received = 0,
    last_request_time = nil,
    active_connections = 0,
    version = "1.0.0"
}

-- Start the web server
print("Starting web server...")
local success, message = _PY.start_web_server(8080, "0.0.0.0")
print("Start result:", success, message)
print()

-- Register a callback for HTTP requests
print("Registering HTTP request callback...")
local function handle_http_request(request)
    system_status.requests_received = system_status.requests_received + 1
    system_status.last_request_time = os.date()
    
    print("=== HTTP Request Received ===")
    print("Method:", request.method)
    print("Path:", request.path)
    print("Total requests:", system_status.requests_received)
    print("============================")
    print()
    
    -- Handle different paths
    if request.path == "/status" then
        -- Return JSON status
        local status_response = {
            status = "ok",
            data = system_status,
            timestamp = os.time()
        }
        print("Status requested, returning:", _PY.to_json(status_response))
        
    elseif request.path == "/health" then
        -- Simple health check
        print("Health check requested")
        
    elseif request.path == "/api/update" and request.method == "POST" then
        -- Update system status via API
        if request.body and request.body.uptime then
            system_status.uptime = request.body.uptime
            print("System uptime updated to:", system_status.uptime)
        end
        if request.body and request.body.active_connections then
            system_status.active_connections = request.body.active_connections
            print("Active connections updated to:", system_status.active_connections)
        end
        
    elseif request.path == "/api/restart" and request.method == "POST" then
        -- Simulate restart
        print("Restart requested via API")
        system_status.uptime = 0
        system_status.requests_received = 0
        
    else
        print("Unknown path:", request.path)
    end
end

_PY.register_web_callback("http_request", handle_http_request)
print("Callback registered!")
print()

-- Start message processing
print("Starting message processing...")
_PY.start_web_message_processing()
print("Message processing started!")
print()

-- Update uptime every second
local function update_uptime()
    while true do
        system_status.uptime = system_status.uptime + 1
        _PY.sleep(1000)  -- 1 second
    end
end

-- Start uptime updater in background
_PY.setTimeout(1000, update_uptime)

print("Web server is now running with status endpoints!")
print("Available endpoints:")
print("  GET  /status     - Get system status as JSON")
print("  GET  /health     - Simple health check")
print("  POST /api/update - Update system status")
print("  POST /api/restart - Simulate restart")
print()
print("Test with:")
print("  curl http://localhost:8080/status")
print("  curl http://localhost:8080/health")
print("  curl -X POST http://localhost:8080/api/update -H 'Content-Type: application/json' -d '{\"uptime\":100,\"active_connections\":5}'")
print("  curl -X POST http://localhost:8080/api/restart")
print()
print("Press Ctrl+C to stop...")

-- Keep the script running
while true do
    _PY.sleep(5000)  -- 5 seconds
    print("System running for", system_status.uptime, "seconds, received", system_status.requests_received, "requests")
end 