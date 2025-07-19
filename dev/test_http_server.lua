-- Test HTTP Server functionality
net = require("net")

print("=== HTTP Server Test ===")

-- Test 1: Basic HTTP Server
print("\n1. Testing HTTP Server with different endpoints")

local server = net.HTTPServer()
local server_port = 8081

-- Request handler using new API: function(method, path, payload) return data, status_code
local function handle_request(method, path, payload)
    print(string.format("HTTP %s %s", method, path))
    
    if payload and payload ~= "" then
        print("Payload: " .. payload)
    end
    
    -- Route the request
    if path == "/" then
        local response_data = {
            message = "Welcome to plua2 HTTP Server!",
            method = method,
            timestamp = os.time()
        }
        return json.encode(response_data), 200
        
    elseif path == "/api/hello" then
        local response_data = {
            greeting = "Hello from Lua!",
            method = method
        }
        return json.encode(response_data), 200
        
    elseif path == "/api/echo" and method == "POST" then
        -- Echo the request body back
        local response_data = {
            echo = payload,
            method = method
        }
        return json.encode(response_data), 200
        
    elseif path == "/html" then
        local html = [[
<!DOCTYPE html>
<html>
<head>
    <title>plua2 HTTP Server</title>
</head>
<body>
    <h1>Hello from plua2!</h1>
    <p>This is served by a Lua HTTP server.</p>
    <p>Current time: ]] .. os.date() .. [[</p>
</body>
</html>]]
        return html, 200
        
    else
        -- 404 Not Found
        local error_data = {
            error = "Not Found",
            path = path,
            available_endpoints = {"/", "/api/hello", "/api/echo", "/html"}
        }
        return json.encode(error_data), 404
    end
end

-- Start the server
print("Starting HTTP server on port " .. server_port)
server:start("localhost", server_port, handle_request)

-- Give server time to start
setTimeout(function()
    print("\nHTTP Server is now running!")
    print("Try these URLs in your browser or with curl:")
    print("  http://localhost:" .. server_port .. "/")
    print("  http://localhost:" .. server_port .. "/api/hello")  
    print("  http://localhost:" .. server_port .. "/html")
    print("  curl -X POST http://localhost:" .. server_port .. "/api/echo -d '{\"test\":\"data\"}'")
    print("\nPress Ctrl+C to stop the server...")
    
    -- Make some test requests using our own HTTP client
    setTimeout(function()
        print("\n--- Making test requests ---")
        
        -- Test GET request to root
        local client = net.HTTPClient()
        client:request("http://localhost:" .. server_port .. "/", {
            success = function(response)
                print("✅ GET / response (status " .. response.status .. "):")
                print(response.data)
            end,
            error = function(err)
                print("❌ GET / failed: " .. err)
            end
        })
        
        -- Test GET request to /api/hello
        setTimeout(function()
            client:request("http://localhost:" .. server_port .. "/api/hello", {
                success = function(response)
                    print("\n✅ GET /api/hello response (status " .. response.status .. "):")
                    print(response.data)
                end,
                error = function(err)
                    print("❌ GET /api/hello failed: " .. err)
                end
            })
        end, 500)
        
        -- Test POST request to /api/echo
        setTimeout(function()
            client:request("http://localhost:" .. server_port .. "/api/echo", {
                options = {
                    method = "POST",
                    headers = {
                        ["Content-Type"] = "application/json"
                    },
                    data = json.encode({message = "Hello from client!", test = true})
                },
                success = function(response)
                    print("\n✅ POST /api/echo response (status " .. response.status .. "):")
                    print(response.data)
                end,
                error = function(err)
                    print("❌ POST /api/echo failed: " .. err)
                end
            })
        end, 1000)
        
        -- Test 404 response
        setTimeout(function()
            client:request("http://localhost:" .. server_port .. "/nonexistent", {
                success = function(response)
                    print("\n✅ GET /nonexistent response (status " .. response.status .. "):")
                    print(response.data)
                end,
                error = function(err)
                    print("❌ GET /nonexistent failed: " .. err)
                end
            })
        end, 1500)
        
    end, 2000)
    
end, 1000)

print("HTTP Server test started...")
