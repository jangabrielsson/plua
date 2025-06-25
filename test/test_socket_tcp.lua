-- Test TCP socket functionality
print("=== Testing TCP Socket ===")

local socket = require("socket")

-- Create a TCP socket
local tcp = socket.tcp()
print("TCP socket created:", tostring(tcp))

-- Try to connect to google.com:80
print("\n--- Connecting to google.com:80 ---")
local conn_id, msg = tcp:connect("google.com", 80)
if conn_id then
  print("Connected! Conn ID:", conn_id)
  -- Send a simple HTTP GET request
  print("\n--- Sending HTTP GET request ---")
  local len, err = tcp:send("GET / HTTP/1.0\r\nHost: google.com\r\n\r\n")
  if len then
    print("Sent bytes:", len)
    -- Receive response
    print("\n--- Receiving response ---")
    local data, datalen = tcp:receive("*a")
    if data then
      print("Received data (first 200 chars):\n" .. string.sub(data, 1, 200))
    else
      print("No data received.")
    end
  else
    print("Send failed:", err)
  end
  -- Close connection
  print("\n--- Closing connection ---")
  tcp:close()
  print("Connection closed.")
else
  print("Failed to connect:", msg)
end

print("\n=== TCP Socket test completed ===") 