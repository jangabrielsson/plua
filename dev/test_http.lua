-- Test HTTP request using socket
local socket = require("socket")

print("Testing HTTP request...")

-- Create a TCP socket
local tcp_socket = socket.tcp()

-- Connect to httpbin.org (a testing service)
print("Connecting to httpbin.org:80...")
local result, err = tcp_socket:connect("httpbin.org", 80)

if result then
    print("Connected! Connection ID:", result)
    
    -- Set timeout
    tcp_socket:settimeout(5)
    
    -- Send HTTP GET request
    local http_request = "GET /ip HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
    print("Sending HTTP request...")
    
    local bytes_sent, send_err = tcp_socket:send(http_request)
    if bytes_sent then
        print("Sent", bytes_sent, "bytes")
        
        -- Read response
        print("Reading response...")
        local response, recv_err = tcp_socket:receive("*a")
        if response then
            print("Received response:")
            print("--- Response Start ---")
            print(response)
            print("--- Response End ---")
        else
            print("Failed to receive response:", recv_err)
        end
    else
        print("Failed to send request:", send_err)
    end
    
    -- Close connection
    tcp_socket:close()
    print("Connection closed")
else
    print("Failed to connect:", err)
end

print("HTTP test completed")
