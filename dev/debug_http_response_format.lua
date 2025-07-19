-- HTTP Response Format Debug Test
-- Tests the exact HTTP response formatting with raw output inspection

net = require("net")

print("=== HTTP Response Format Debug Test ===")

local server = net.HTTPServer()
local port = 8095

local function handle_request(method, path, payload)
    print(string.format("\n[%s] %s %s", os.date("%H:%M:%S"), method, path))
    
    if path == "/raw" then
        -- Simple text response for easy inspection
        return "Hello, World!", 200
        
    elseif path == "/json" then
        -- JSON response
        local response = {
            message = "Test JSON response",
            timestamp = os.time(),
            method = method,
            path = path
        }
        return json.encode(response), 200
        
    elseif path == "/headers" then
        -- Test different content types
        return "<html><body><h1>HTML Response</h1></body></html>", 200
        
    elseif path == "/empty" then
        -- Empty response
        return "", 204
        
    elseif path == "/error" then
        -- Error response
        return json.encode({error = "Test error", code = 500}), 500
        
    else
        local help = {
            message = "HTTP Response Format Debug Server",
            available_endpoints = {
                "/raw - Plain text response",
                "/json - JSON response", 
                "/headers - HTML response",
                "/empty - Empty 204 response",
                "/error - Error 500 response"
            }
        }
        return json.encode(help), 200
    end
end

print("Starting debug server on 0.0.0.0:" .. port)
server:start("0.0.0.0", port, handle_request)

setTimeout(function()
    print("\n🔍 HTTP Response Format Debug Server Running!")
    print("\nTest raw HTTP responses with:")
    print("  curl -v http://localhost:" .. port .. "/raw")
    print("  curl -v http://localhost:" .. port .. "/json")
    print("  curl -v http://localhost:" .. port .. "/headers")
    print("  curl -v http://localhost:" .. port .. "/empty")
    print("  curl -v http://localhost:" .. port .. "/error")
    print("\nInspect with netcat:")
    print("  echo -e 'GET /raw HTTP/1.1\\r\\nHost: localhost:" .. port .. "\\r\\n\\r\\n' | nc localhost " .. port .. " | hexdump -C")
    print("\nPress Ctrl+C to stop...")
end, 1000)

print("Debug server starting...")
