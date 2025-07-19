-- Test script to verify that src/lua is in package.path
print("Testing package.path configuration...")
print("Current package.path:", package.path)

-- Try to require the socket module
local socket = require("socket")
print("Successfully loaded socket module:", socket)

-- Test creating a TCP socket
local tcp_socket = socket.tcp()
print("Created TCP socket:", tcp_socket)
