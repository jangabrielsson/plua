-- Test script for _PY.isRunning hook functionality
-- Demonstrates how to control script termination based on runtime state

print("=== Testing _PY.isRunning Hook ===")

local request_count = 0
local max_requests = 5

-- Define a custom isRunning hook
function _PY.isRunning(state)
    print(string.format("isRunning hook called - Timers: %d, Callbacks: %d, Total: %d, Requests: %d", 
        state.active_timers, state.pending_callbacks, state.total_tasks, request_count))
    
    -- Stop when we've processed enough requests and have no pending work
    if request_count >= max_requests and state.total_tasks == 0 then
        print("✅ Script completed successfully - terminating")
        return false  -- Stop running
    end
    
    -- Continue running
    return true
end

-- Start an HTTP server to generate some activity
net = require("net")
local server = net.HTTPServer()
local port = 8099

local function handle_request(method, path, payload)
    request_count = request_count + 1
    print(string.format("Handling request #%d: %s %s", request_count, method, path))
    
    local response = {
        message = "Request processed",
        request_number = request_count,
        max_requests = max_requests,
        remaining = max_requests - request_count
    }
    
    return json.encode(response), 200
end

server:start("0.0.0.0", port, handle_request)

print(string.format("Server started on port %d", port))
print(string.format("Make %d requests to trigger auto-termination", max_requests))
print("Try: for i in {1..5}; do curl http://localhost:" .. port .. "/test; done")

-- Set up some timers to show the system working
setTimeout(function()
    print("⏰ Timer 1 executed after 2 seconds")
end, 2000)

setTimeout(function()
    print("⏰ Timer 2 executed after 5 seconds")
end, 5000)

setTimeout(function()
    print("⏰ Timer 3 executed after 8 seconds")
    print("💡 Tip: Make HTTP requests to trigger completion!")
end, 8000)

print("Script initialized - waiting for activity...")
