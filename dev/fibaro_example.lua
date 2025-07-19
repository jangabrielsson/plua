-- Example demonstrating Fibaro-compatible net.TCPSocket usage
net = require("net")

print("=== Fibaro API Compatible TCPSocket Example ===")

-- Create TCPSocket with timeout option (like Fibaro API)
local socket = net.TCPSocket({timeout = 5000})  -- 5 second timeout

print("Connecting to a test server...")

-- Connect using proper Fibaro callback style
socket:connect("httpbin.org", 80, {
    success = function()
        print("✅ Connected successfully!")
        
        -- Send HTTP request using Fibaro send method
        local request = "GET /ip HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
        socket:send(request, {
            success = function()
                print("✅ HTTP request sent")
                
                -- Read response using Fibaro read method
                socket:read({
                    success = function(data)
                        print("✅ Received response:")
                        print(data)
                        socket:close()
                        print("Connection closed")
                    end,
                    error = function(err)
                        print("❌ Error reading response: " .. err)
                    end
                })
            end,
            error = function(err)
                print("❌ Error sending request: " .. err)
            end
        })
    end,
    error = function(err)
        print("❌ Connection failed: " .. err)
    end
})

print("Fibaro API example started...")
