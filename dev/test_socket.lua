-- Test TCP socket functionality
local socket = require("socket")

print("Testing TCP socket functionality...")

-- Create a TCP socket
local tcp_socket = socket.tcp()
print("Created TCP socket:", tcp_socket)

-- Try to connect to a well-known server (Google DNS on port 53)
print("Attempting to connect to 8.8.8.8:53...")
local result, err = tcp_socket:connect("8.8.8.8", 53)

if result then
    print("Successfully connected! Connection ID:", result)
    
    -- Set a short timeout
    tcp_socket:settimeout(2)
    print("Set timeout to 2 seconds")
    
    -- Close the connection
    tcp_socket:close()
    print("Connection closed")
else
    print("Failed to connect:", err)
end

print("Socket test completed")
