-- HTTP Server with Auto-Termination Example
-- Shows how to create an HTTP server that shuts down automatically
-- after processing a certain number of requests

print("=== HTTP Server Auto-Termination Example ===")

local server = net.HTTPServer()
local port = 8100
local request_count = 0
local max_requests = 5
local start_time = os.time()

-- Define the isRunning hook for HTTP server auto-shutdown
function _PY.isRunning(state)
    local elapsed = os.time() - start_time
    
    print(string.format("📊 [%ds] Server status - Requests: %d/%d, Timers: %d, Callbacks: %d", 
        elapsed, request_count, max_requests, state.active_timers, state.pending_callbacks))
    
    -- Stop when we've processed enough requests and have no pending work
    if request_count >= max_requests and state.total_tasks == 0 then
        print("✅ Request limit reached and no pending work - shutting down server")
        return false
    end
    
    -- Optional: Add maximum runtime (uncomment if needed)
    -- if elapsed > 60 then
    --     print("⏰ Maximum runtime reached - shutting down server")
    --     return false
    -- end
    
    return true
end

-- HTTP request handler
local function handle_request(method, path, payload)
    request_count = request_count + 1
    local remaining = max_requests - request_count
    
    print(string.format("🌐 [%s] %s %s - Request #%d (%d remaining)", 
        os.date("%H:%M:%S"), method, path, request_count, remaining))
    
    if path == "/status" then
        local response = {
            message = "Server status",
            request_count = request_count,
            max_requests = max_requests,
            remaining = remaining,
            uptime = os.time() - start_time
        }
        return json.encode(response), 200
        
    elseif path == "/hello" then
        local response = {
            message = "Hello from auto-terminating server!",
            request_number = request_count,
            will_shutdown_after = max_requests
        }
        return json.encode(response), 200
        
    else
        local response = {
            message = "Auto-terminating HTTP server",
            request_number = request_count,
            max_requests = max_requests,
            available_endpoints = {"/", "/hello", "/status"},
            note = "Server will auto-shutdown after " .. max_requests .. " requests"
        }
        return json.encode(response), 200
    end
end

-- Start the server
server:start("0.0.0.0", port, handle_request)

print(string.format("🚀 HTTP server started on port %d", port))
print(string.format("📝 Server will automatically shut down after %d requests", max_requests))
print("\n💡 Test the server:")
print("   curl http://localhost:" .. port .. "/")
print("   curl http://localhost:" .. port .. "/hello")
print("   curl http://localhost:" .. port .. "/status")
print("\n🔄 Make multiple requests to trigger auto-shutdown:")
print("   for i in {1.." .. max_requests .. "}; do curl http://localhost:" .. port .. "/hello; echo; done")

print("\n⭐ This example demonstrates:")
print("   • HTTP server with automatic shutdown")
print("   • Request counting and limits")
print("   • Clean termination without manual intervention")
print("   • Monitoring server state in real-time")

print("\n🎯 Waiting for requests...")
