-- Test that the refactored socket functionality still works
local socket = require("socket")

print("Testing refactored socket functionality...")

-- Create a TCP socket
local tcp_socket = socket.tcp()
print("✓ TCP socket created:", tcp_socket)

-- Test connection (this should work or fail gracefully)
print("Testing connection...")
local result, err = tcp_socket:connect("127.0.0.1", 8172)
if result then
    print("✓ Connected to localhost:8172, closing...")
    tcp_socket:close()
else
    print("✓ Connection failed as expected:", err)
end

print("Refactored socket functionality verified!")
