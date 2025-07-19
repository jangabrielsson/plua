-- HTTP Request Parser Debug Test
-- Tests how the server parses different types of HTTP requests

net = require("net")

print("=== HTTP Request Parser Debug Test ===")

local server = net.HTTPServer()
local port = 8096

local function handle_request(method, path, payload)
    local separator = "=================================================="
    print("\n" .. separator)
    print(string.format("REQUEST DEBUG [%s]", os.date("%H:%M:%S")))
    print(separator)
    print("Method:", method)
    print("Path:", path)
    print("Payload length:", payload and #payload or 0)
    
    if payload and payload ~= "" then
        print("Payload content:")
        print("  Raw: " .. string.format("%q", payload))
        print("  Length: " .. #payload .. " bytes")
        
        -- Try to parse as JSON
        local success, parsed = pcall(json.decode, payload)
        if success then
            print("  Parsed JSON:")
            for k, v in pairs(parsed) do
                print("    " .. k .. ": " .. tostring(v))
            end
        else
            print("  Not valid JSON")
        end
    else
        print("Payload: (empty)")
    end
    
    local dash_line = "------------------------------"
    print(dash_line)
    
    -- Echo back the request details
    local response = {
        received = {
            method = method,
            path = path,
            payload = payload,
            payload_length = payload and #payload or 0,
            timestamp = os.time()
        },
        message = "Request successfully parsed and processed"
    }
    
    return json.encode(response), 200
end

print("Starting request parser debug server on 0.0.0.0:" .. port)
server:start("0.0.0.0", port, handle_request)

setTimeout(function()
    print("\n🔍 HTTP Request Parser Debug Server Running!")
    print("\nTest different request types:")
    print("  curl http://localhost:" .. port .. "/test")
    print("  curl -X POST http://localhost:" .. port .. "/post -d 'simple text'")
    print("  curl -X POST http://localhost:" .. port .. "/json \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"key\":\"value\",\"number\":42}'")
    print("  curl -X PUT http://localhost:" .. port .. "/put/123 -d 'update data'")
    print("  curl -X DELETE http://localhost:" .. port .. "/delete/456")
    print("\nWatch the server logs to see how requests are parsed.")
    print("Press Ctrl+C to stop...")
end, 1000)

print("Request parser debug server starting...")
