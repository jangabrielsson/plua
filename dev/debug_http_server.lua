-- Simple HTTP Server Debug Test
net = require("net")

print("=== HTTP Server Debug Test ===")

local server = net.HTTPServer()
local port = 8090

print("Creating request handler...")

local function handle_request(method, path, payload)
    print("DEBUG: Callback executed!")
    print("  Method:", method)
    print("  Path:", path)
    print("  Payload:", payload or "nil")
    
    if path == "/test" then
        local response = {message = "Hello from debug test!"}
        print("  Returning:", json.encode(response))
        return json.encode(response), 200
    else
        print("  Returning 404")
        return json.encode({error = "Not found"}), 404
    end
end

print("Starting server on port", port)
server:start("localhost", port, handle_request)

setTimeout(function()
    print("Server should be running now!")
    print("Try: curl http://localhost:" .. port .. "/test")
end, 1000)

print("Debug test started...")
