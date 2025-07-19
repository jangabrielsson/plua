-- HTTP Stress Test and Concurrency Debug
-- Tests multiple concurrent connections and persistent callback handling

net = require("net")

print("=== HTTP Stress Test Debug ===")

local server = net.HTTPServer()
local port = 8097
local request_count = 0

local function handle_request(method, path, payload)
    request_count = request_count + 1
    local req_id = request_count
    
    print(string.format("[%d] %s %s - Request #%d", 
        os.time(), method, path, req_id))
    
    if path == "/slow" then
        -- Simulate slow processing
        local start = os.time()
        while os.time() - start < 2 do
            -- Busy wait for 2 seconds
        end
        return json.encode({
            message = "Slow response completed",
            request_id = req_id,
            processing_time = "2 seconds"
        }), 200
        
    elseif path == "/fast" then
        return json.encode({
            message = "Fast response",
            request_id = req_id,
            timestamp = os.time()
        }), 200
        
    elseif path == "/stats" then
        return json.encode({
            total_requests = request_count,
            server_uptime = os.time(),
            current_request_id = req_id
        }), 200
        
    else
        return json.encode({
            message = "Stress test server",
            request_id = req_id,
            endpoints = {"/fast", "/slow", "/stats"},
            total_requests_so_far = request_count
        }), 200
    end
end

print("Starting stress test server on 0.0.0.0:" .. port)
server:start("0.0.0.0", port, handle_request)

setTimeout(function()
    print("\n🚀 HTTP Stress Test Server Running!")
    print("\nTest concurrent requests:")
    print("  # Fast requests:")
    print("  curl http://localhost:" .. port .. "/fast &")
    print("  curl http://localhost:" .. port .. "/fast &")
    print("  curl http://localhost:" .. port .. "/fast &")
    print("\n  # Mixed fast/slow:")
    print("  curl http://localhost:" .. port .. "/slow &")
    print("  curl http://localhost:" .. port .. "/fast")
    print("\n  # Check stats:")
    print("  curl http://localhost:" .. port .. "/stats")
    print("\nWatch the logs to verify persistent callback handling.")
    print("Press Ctrl+C to stop...")
end, 1000)

print("Stress test server starting...")
