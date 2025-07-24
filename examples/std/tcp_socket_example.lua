-- TCP Socket Example
-- This example shows how to create TCP connections using the built-in net module

print("=== TCP Socket Example ===")

-- Example 1: Connect to a public echo server
print("\n1. Connecting to echo server...")

local socket = net.TCPSocket()

socket:connect("tcpbin.com", 4242, {
    success = function()
        print("✅ Connected to echo server!")
        
        -- Send a message
        local message = "Hello from plua TCP client!\n"
        print("Sending:", message:gsub("\n", ""))
        
        socket:send(message, {
            success = function()
                print("✅ Message sent successfully!")
                
                -- Read the echo response
                socket:read({
                    success = function(data)
                        print("✅ Received echo:", data:gsub("\n", ""))
                        
                        -- Close the connection
                        socket:close()
                        print("Connection closed.")
                    end,
                    error = function(err)
                        print("❌ Read failed:", err)
                        socket:close()
                    end
                })
            end,
            error = function(err)
                print("❌ Send failed:", err)
                socket:close()
            end
        })
    end,
    error = function(err)
        print("❌ Connection failed:", err)
    end
})

-- Example 2: HTTP request over raw TCP (educational)
setTimeout(function()
    print("\n2. Making raw HTTP request over TCP...")
    
    local http_socket = net.TCPSocket()
    
    http_socket:connect("httpbin.org", 80, {
        success = function()
            print("✅ Connected to httpbin.org!")
            
            -- Send raw HTTP request
            local http_request = "GET /get HTTP/1.1\r\n" ..
                               "Host: httpbin.org\r\n" ..
                               "Connection: close\r\n" ..
                               "User-Agent: plua-tcp-example/1.0\r\n" ..
                               "\r\n"
            
            print("Sending HTTP request...")
            
            http_socket:send(http_request, {
                success = function()
                    print("✅ HTTP request sent!")
                    
                    -- Read the response
                    http_socket:readUntil("\r\n\r\n", {
                        success = function(headers)
                            print("✅ Received HTTP headers:")
                            print(headers)
                            
                            http_socket:close()
                        end,
                        error = function(err)
                            print("❌ Failed to read headers:", err)
                            http_socket:close()
                        end
                    })
                end,
                error = function(err)
                    print("❌ Failed to send HTTP request:", err)
                    http_socket:close()
                end
            })
        end,
        error = function(err)
            print("❌ Failed to connect to httpbin.org:", err)
        end
    })
end, 3000)

-- Example 3: Chat-like interaction with timeout handling
setTimeout(function()
    print("\n3. Testing timeout behavior...")
    
    local timeout_socket = net.TCPSocket({timeout = 5000}) -- 5 second timeout
    
    timeout_socket:connect("httpbin.org", 80, {
        success = function()
            print("✅ Connected! Testing read timeout...")
            
            -- Try to read without sending anything (should timeout)
            timeout_socket:read({
                success = function(data)
                    print("Unexpected data:", data)
                    timeout_socket:close()
                end,
                error = function(err)
                    print("✅ Expected timeout/error:", err)
                    timeout_socket:close()
                end
            })
        end,
        error = function(err)
            print("❌ Connection failed:", err)
        end
    })
end, 6000)

print("\nTCP socket examples started. Results will appear as they complete...")
