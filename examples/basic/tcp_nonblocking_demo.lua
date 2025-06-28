-- TCP Non-blocking Demo
-- Shows improved behavior with empty string returns for no data

print("=== TCP Non-blocking Socket Demo ===")

-- Connect to a test server
print("\n1. Connecting to httpbin.org:80...")
local success, conn_id, message = _PY.tcp_connect_sync("httpbin.org", 80)
if not success then
  print("Failed to connect:", message)
  os.exit(1)
end
print("Connected! Connection ID:", conn_id)

-- Set to non-blocking mode
print("\n2. Setting socket to non-blocking mode...")
local success, message = _PY.tcp_set_timeout_sync(conn_id, 0)
if success then
  print("Success:", message)
else
  print("Failed:", message)
end

-- Test reading with no data available
print("\n3. Testing read with no data available...")
local success, data, message = _PY.tcp_read_sync(conn_id, 1024)
if success then
  print("Read result:", message)
  print("Data length:", #data)
  if data == "" then
  print("✓ Correctly returned empty string for no data")
  else
  print("✗ Unexpected data received")
  end
else
  print("Read failed:", message)
end

-- Test multiple reads
print("\n4. Testing multiple reads...")
for i = 1, 5 do
  local success, data, message = _PY.tcp_read_sync(conn_id, 1024)
  if success then
  print("  Read", i, ":", message, "| Data length:", #data)
  else
  print("  Read", i, "failed:", message)
  break
  end
end

-- Send a request to get some data
print("\n5. Sending HTTP request...")
local request = "GET / HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
local success, message = _PY.tcp_write_sync(conn_id, request)
if success then
  print("Request sent:", message)
  
  -- Now try to read response
  print("\n6. Reading response...")
  local success, data, message = _PY.tcp_read_sync(conn_id, "*a")  -- Read all available data
  if success then
  print("Response received:", message)
  print("Response length:", #data, "characters")
  if #data > 0 then
  print("✓ Successfully received data")
  print("First 100 chars:", string.sub(data, 1, 100))
  else
  print("✗ No data received")
  end
  else
  print("Failed to read response:", message)
  end
else
  print("Failed to send request:", message)
end

-- Test non-blocking read after data is sent
print("\n7. Testing non-blocking read after data exchange...")
local success, data, message = _PY.tcp_read_sync(conn_id, 1024)
if success then
  print("Read result:", message)
  print("Data length:", #data)
  if data == "" then
  print("✓ Correctly returned empty string (no more data)")
  else
  print("✗ Unexpected data received")
  end
else
  print("Read failed:", message)
end

-- Clean up
print("\n8. Closing connection...")
local success, message = _PY.tcp_close_sync(conn_id)
if success then
  print("Success:", message)
else
  print("Failed:", message)
end

print("\n=== Demo completed ===")
print("\nBenefits of empty string return:")
print("- No need to check for errors when no data is expected")
print("- Can use simple string length checks: if #data > 0 then ...")
print("- More intuitive for non-blocking socket patterns")
print("- Easier to implement retry loops") 