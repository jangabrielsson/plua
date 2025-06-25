-- TCP Error Handling Demo
-- Shows how to handle "Resource temporarily unavailable" errors

print("=== TCP Error Handling Demo ===")

-- Strategy 1: Use proper timeout instead of non-blocking
print("\n1. Strategy: Use proper timeout instead of non-blocking")
local success, conn_id, message = _PY.tcp_connect_sync("httpbin.org", 80)
if success then
  print("Connected! Connection ID:", conn_id)
  
  -- Set a reasonable timeout (5 seconds)
  _PY.tcp_set_timeout_sync(conn_id, 5)
  print("Set timeout to 5 seconds")
  
  -- Try to read - this should work with proper timeout
  local success, data, message = _PY.tcp_read_sync(conn_id, 1024)
  if success then
  print("Read successful:", message)
  if #data > 0 then
  print("  Data received:", #data, "bytes")
  else
  print("  No data available")
  end
  else
  print("Read failed:", message)
  end
  
  _PY.tcp_close_sync(conn_id)
else
  print("Failed to connect:", message)
end

-- Strategy 2: Retry loop with non-blocking socket (improved)
print("\n2. Strategy: Retry loop with non-blocking socket (improved)")
local success, conn_id, message = _PY.tcp_connect_sync("httpbin.org", 80)
if success then
  print("Connected! Connection ID:", conn_id)
  
  -- Set to non-blocking mode
  _PY.tcp_set_timeout_sync(conn_id, 0)
  print("Set to non-blocking mode")
  
  -- Retry loop for reading (now much simpler!)
  local max_retries = 10
  local retry_count = 0
  local read_success = false
  
  while retry_count < max_retries and not read_success do
  retry_count = retry_count + 1
  print("  Attempt", retry_count, "of", max_retries)
  
  local success, data, message = _PY.tcp_read_sync(conn_id, 1024)
  if success then
  if #data > 0 then
  print("  ✓ Read successful:", message, "| Data:", #data, "bytes")
  read_success = true
  else
  print("  → No data available, retrying...")
  -- Small delay before retry
  os.execute("sleep 0.1")
  end
  else
  print("  ✗ Read error:", message)
  break
  end
  end
  
  if not read_success then
  print("  Failed to read data after", max_retries, "attempts")
  end
  
  _PY.tcp_close_sync(conn_id)
else
  print("Failed to connect:", message)
end

-- Strategy 3: Check if data is available before reading
print("\n3. Strategy: Send request first, then read response")
local success, conn_id, message = _PY.tcp_connect_sync("httpbin.org", 80)
if success then
  print("Connected! Connection ID:", conn_id)
  
  -- Set reasonable timeout
  _PY.tcp_set_timeout_sync(conn_id, 10)
  print("Set timeout to 10 seconds")
  
  -- Send HTTP request first
  local request = "GET / HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
  local success, message = _PY.tcp_write_sync(conn_id, request)
  if success then
  print("Request sent:", message)
  
  -- Now try to read response
  local success, data, message = _PY.tcp_read_sync(conn_id, "*a")  -- Read all available data
  if success then
  print("Response received:", message)
  print("Response length:", #data, "characters")
  if #data > 0 then
  print("First 200 chars:", string.sub(data, 1, 200))
  else
  print("No data received")
  end
  else
  print("Failed to read response:", message)
  end
  else
  print("Failed to send request:", message)
  end
  
  _PY.tcp_close_sync(conn_id)
else
  print("Failed to connect:", message)
end

-- Strategy 4: Simple non-blocking pattern
print("\n4. Strategy: Simple non-blocking pattern")
local success, conn_id, message = _PY.tcp_connect_sync("httpbin.org", 80)
if success then
  print("Connected! Connection ID:", conn_id)
  
  -- Set to non-blocking
  _PY.tcp_set_timeout_sync(conn_id, 0)
  
  -- Simple pattern: try to read, check if data available
  local success, data, message = _PY.tcp_read_sync(conn_id, 1024)
  if success then
  if #data > 0 then
  print("  ✓ Data available:", #data, "bytes")
  else
  print("  → No data available (normal for non-blocking)")
  end
  else
  print("  ✗ Read error:", message)
  end
  
  _PY.tcp_close_sync(conn_id)
else
  print("Failed to connect:", message)
end

print("\n=== Error Handling Demo Completed ===")
print("\nSummary of improved Errno 35 handling:")
print("1. Non-blocking reads now return empty string instead of error")
print("2. Much simpler retry loops: if #data > 0 then ...")
print("3. No need to check for specific error messages")
print("4. More intuitive API for non-blocking operations")
print("5. Easier to implement polling patterns") 