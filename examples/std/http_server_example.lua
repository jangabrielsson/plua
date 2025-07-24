-- HTTP Server Example
-- This example shows how to create a simple HTTP server using the built-in net module

print("=== HTTP Server Example ===")

-- Create and start HTTP server
local server = net.HTTPServer()
local port = 8094

print("Starting HTTP server on port " .. port .. "...")

-- Request handler: receives method, path, payload and returns data, status_code
local function handle_request(method, path, payload)
    print(string.format("[%s] %s %s", os.date("%H:%M:%S"), method, path))
    
    if payload and payload ~= "" then
        print("  Payload: " .. payload)
    end
    
    -- Route handling
    if path == "/" then
        local response = {
            message = "Welcome to plua HTTP Server!",
            version = "1.0",
            endpoints = {"/", "/api/info", "/api/echo", "/time"},
            timestamp = os.time()
        }
        return json.encode(response), 200
        
    elseif path == "/api/info" then
        local info = {
            server = "plua-http",
            lua_version = _VERSION,
            uptime = os.time(),
            method_used = method
        }
        return json.encode(info), 200
        
    elseif path == "/api/echo" then
        if method == "POST" and payload then
            -- Try to parse JSON payload
            local parsed_payload = json.decode(payload)
            local response = {
                echo = parsed_payload or payload,
                received_method = method,
                timestamp = os.time()
            }
            return json.encode(response), 200
        else
            local error_response = {
                error = "Echo endpoint requires POST with data",
                usage = "POST /api/echo with JSON body"
            }
            return json.encode(error_response), 400
        end
        
    elseif path == "/time" then
        local time_response = {
            current_time = os.date("%Y-%m-%d %H:%M:%S"),
            unix_timestamp = os.time(),
            timezone = os.date("%Z")
        }
        return json.encode(time_response), 200
        
    elseif path:match("^/hello/(.+)") then
        local name = path:match("^/hello/(.+)")
        local greeting = {
            message = "Hello, " .. name .. "!",
            method = method,
            timestamp = os.time()
        }
        return json.encode(greeting), 200
        
    else
        -- 404 Not Found
        local not_found = {
            error = "Not Found",
            path = path,
            available_endpoints = {
                "/",
                "/api/info", 
                "/api/echo",
                "/time",
                "/hello/{name}"
            }
        }
        return json.encode(not_found), 404
    end
end

-- Start the server
server:start("0.0.0.0", port, handle_request)

-- Wait a moment then show usage info
setTimeout(function()
    print("\n🚀 HTTP Server is running!")
    print("\nTry these commands:")
    print("  curl http://localhost:" .. port .. "/")
    print("  curl http://localhost:" .. port .. "/api/info")
    print("  curl http://localhost:" .. port .. "/time")
    print("  curl http://localhost:" .. port .. "/hello/YourName")
    print("  curl -X POST http://localhost:" .. port .. "/api/echo -H 'Content-Type: application/json' -d '{\"message\":\"Hello World\"}'")
    print("\nOr open http://localhost:" .. port .. "/ in your browser")
    print("\nPress Ctrl+C to stop the server...")
    
    -- Demonstrate making requests to our own server
    setTimeout(function()
        print("\n--- Testing our own server ---")
        
        local client = net.HTTPClient()
        
        -- Test GET request
        client:request("http://localhost:" .. port .. "/api/info", {
            success = function(response)
                print("✅ Self-test GET successful (status " .. response.status .. "):")
                local data = json.decode(response.data)
                if data then
                    print("  Server: " .. (data.server or "unknown"))
                    print("  Lua: " .. (data.lua_version or "unknown"))
                end
            end,
            error = function(status)
                print("❌ Self-test GET failed: " .. status)
            end
        })
        
        -- Test POST request
        setTimeout(function()
            client:request("http://localhost:" .. port .. "/api/echo", {
                options = {
                    method = "POST",
                    headers = {["Content-Type"] = "application/json"},
                    data = json.encode({test = "self-test", value = 42})
                },
                success = function(response)
                    print("✅ Self-test POST successful (status " .. response.status .. "):")
                    local data = json.decode(response.data)
                    if data and data.echo then
                        print("  Echo received: test=" .. tostring(data.echo.test))
                    end
                end,
                error = function(status)
                    print("❌ Self-test POST failed: " .. status)
                end
            })
        end, 1000)
        
    end, 2000)
end, 1000)

print("HTTP Server example started...")
