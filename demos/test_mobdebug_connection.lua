-- Test MobDebug Connection
print("Testing MobDebug connection...")

-- Test basic socket functionality
local socket = require("socket")
local sock = socket.tcp()

print("Socket created successfully")

-- Test connection to a non-existent server (should fail quickly)
local success, err = sock:connect("127.0.0.1", 9999)
if not success then
  print("Connection test failed as expected:", err)
else
  print("Unexpected connection success")
end

print("MobDebug connection test completed") 