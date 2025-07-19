-- Test basic socket functionality for MobDebug compatibility
local socket = require("socket")

print("Testing socket module for MobDebug compatibility...")

-- Test socket creation
local tcp_socket = socket.tcp()
print("✓ TCP socket created:", tcp_socket)

-- Test connection to localhost (this will fail but should return proper error)
local result, err = tcp_socket:connect("127.0.0.1", 8172)
if result then
    print("✓ Connected (unexpected)")
    tcp_socket:close()
else
    print("✓ Connection failed as expected:", err)
end

print("Socket module is ready for MobDebug!")
