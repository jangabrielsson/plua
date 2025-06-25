-- Test UDP socket functionality
print("=== Testing UDP Socket ===")

-- Load the socket module
local socket = require("socket")

-- Test UDP socket creation
print("\n--- Creating UDP socket ---")
local udp_socket = socket.udp()
print("UDP socket created:", tostring(udp_socket))

-- Test UDP connection (this will fail since we're not connecting to a real server)
print("\n--- Testing UDP connection ---")
local success, message = udp_socket:connect("127.0.0.1", 12345)
if success then
  print("UDP connection successful:", message)
  
  -- Test sending data
  print("\n--- Testing UDP send ---")
  local len, err = udp_socket:send("Hello UDP!")
  if len then
    print("UDP send successful, bytes sent:", len)
  else
    print("UDP send failed:", err)
  end
  
  -- Test receiving data
  print("\n--- Testing UDP receive ---")
  local data, len = udp_socket:receive(1024)
  if data then
    print("UDP receive successful, data:", data, "length:", len)
  else
    print("UDP receive failed or no data")
  end
  
  -- Close the connection
  print("\n--- Closing UDP connection ---")
  udp_socket:close()
  print("UDP connection closed")
else
  print("UDP connection failed:", message)
end

print("\n=== UDP Socket test completed ===") 