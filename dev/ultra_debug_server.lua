-- Ultra simple HTTP server debug
net = require("net")

print("=== Ultra Simple HTTP Debug ===")

local server = net.HTTPServer()

local function handle_request(method, path, payload)
    print("=== REQUEST RECEIVED ===")
    print("Method type:", type(method), "Value:", tostring(method))
    print("Path type:", type(path), "Value:", tostring(path))
    print("Payload type:", type(payload), "Value:", tostring(payload))
    print("========================")
    
    return json.encode({status = "ok", received = {method = method, path = path}}), 200
end

server:start("localhost", 8092, handle_request)

setTimeout(function()
    print("Server started on port 8092")
    print("Test with: curl http://localhost:8092/test")
end, 1000)

print("Starting ultra simple debug server...")
