-- HTTP Debug Test Suite
-- Comprehensive test suite using the debug utilities

-- Load debug utilities
local debug_utils = require("debug_network_utils")
net = require("net")

print("=== HTTP Debug Test Suite ===")

local server = net.HTTPServer()
local port = 8098
local request_counter = 0

local function handle_request(method, path, payload)
    request_counter = request_counter + 1
    local req_id = "REQ-" .. request_counter
    
    -- Use debug utilities to log the request
    debug_utils.print_request(method, path, payload, req_id)
    
    local response_data, status_code
    
    if path == "/debug/hex" then
        response_data = "Hello, World! This is a test response for hex dump."
        status_code = 200
        
        -- Show hex dump of response
        debug_utils.colored_print("yellow", "Response hex dump:")
        debug_utils.hex_dump(response_data)
        
    elseif path == "/debug/json" then
        local test_json = '{"test": true, "number": 42, "array": [1,2,3]}'
        debug_utils.test_json_parsing(test_json)
        
        response_data = test_json
        status_code = 200
        
    elseif path == "/debug/error" then
        debug_utils.colored_print("red", "Intentional error test")
        response_data = json.encode({error = "This is a test error", code = 123})
        status_code = 500
        
    elseif path == "/debug/large" then
        -- Generate a large response
        local large_data = {}
        for i = 1, 100 do
            large_data["item_" .. i] = "This is item number " .. i .. " with some extra data."
        end
        response_data = json.encode({
            message = "Large response test",
            items = large_data,
            total_items = 100
        })
        status_code = 200
        
    else
        response_data = json.encode({
            message = "HTTP Debug Test Suite",
            request_id = req_id,
            available_endpoints = {
                "/debug/hex - Response with hex dump",
                "/debug/json - JSON parsing test",
                "/debug/error - Error response test", 
                "/debug/large - Large response test"
            },
            server_info = {
                total_requests = request_counter,
                uptime = os.time()
            }
        })
        status_code = 200
    end
    
    -- Use debug utilities to log the response
    debug_utils.print_response(response_data, status_code, req_id)
    
    return response_data, status_code
end

print("Starting debug test suite server on 0.0.0.0:" .. port)
server:start("0.0.0.0", port, handle_request)

setTimeout(function()
    debug_utils.colored_print("green", "🔍 HTTP Debug Test Suite Running!")
    print("\nAvailable debug endpoints:")
    debug_utils.colored_print("cyan", "  http://localhost:" .. port .. "/")
    debug_utils.colored_print("cyan", "  http://localhost:" .. port .. "/debug/hex")
    debug_utils.colored_print("cyan", "  http://localhost:" .. port .. "/debug/json")
    debug_utils.colored_print("cyan", "  http://localhost:" .. port .. "/debug/error")
    debug_utils.colored_print("cyan", "  http://localhost:" .. port .. "/debug/large")
    
    print("\nTest commands:")
    print("  curl http://localhost:" .. port .. "/debug/hex")
    print("  curl http://localhost:" .. port .. "/debug/json")
    print("  curl -v http://localhost:" .. port .. "/debug/error")
    
    debug_utils.colored_print("yellow", "\nWatch the colorized debug output above!")
    print("Press Ctrl+C to stop...")
    
    -- Run a self-test after 3 seconds
    setTimeout(function()
        debug_utils.colored_print("magenta", "\n=== Running Self-Test ===")
        debug_utils.benchmark_request("http://localhost:" .. port .. "/", 3)
    end, 3000)
    
end, 1000)

print("Debug test suite starting...")
