-- TCP Timeout Demo
-- Tests various timeout settings including non-blocking mode

print("=== TCP Timeout Demo ===")

-- Connect to a test server
print("\n1. Connecting to httpbin.org:80...")
local success, conn_id, message = _PY.tcp_connect_sync("httpbin.org", 80)
if not success then
  print("Failed to connect:", message)
  os.exit(1)
end
print("Connected! Connection ID:", conn_id)

-- Test 1: Check default timeout
print("\n2. Checking default timeout...")
local success, timeout, message = _PY.tcp_get_timeout_sync(conn_id)
if success then
  print("Default timeout:", timeout, "(" .. message .. ")")
else
  print("Failed to get timeout:", message)
end

-- Test 2: Set to non-blocking mode (timeout = 0)
print("\n3. Setting socket to non-blocking mode (timeout = 0)...")
local success, message = _PY.tcp_set_timeout_sync(conn_id, 0)
if success then
  print("Success:", message)
else
  print("Failed:", message)
end

-- Verify non-blocking mode
local success, timeout, message = _PY.tcp_get_timeout_sync(conn_id)
if success then
  print("Current timeout:", timeout, "(" .. message .. ")")
  if timeout == 0 then
  print("✓ Socket is correctly in non-blocking mode")
  else
  print("✗ Socket is NOT in non-blocking mode")
  end
else
  print("Failed to get timeout:", message)
end

-- Test 3: Set to blocking mode (timeout = nil)
print("\n4. Setting socket to blocking mode (timeout = nil)...")
local success, message = _PY.tcp_set_timeout_sync(conn_id, nil)
if success then
  print("Success:", message)
else
  print("Failed:", message)
end

-- Verify blocking mode
local success, timeout, message = _PY.tcp_get_timeout_sync(conn_id)
if success then
  print("Current timeout:", timeout, "(" .. message .. ")")
  if timeout == nil then
  print("✓ Socket is correctly in blocking mode")
  else
  print("✗ Socket is NOT in blocking mode")
  end
else
  print("Failed to get timeout:", message)
end

-- Test 4: Set to 5 second timeout
print("\n5. Setting timeout to 5 seconds...")
local success, message = _PY.tcp_set_timeout_sync(conn_id, 5)
if success then
  print("Success:", message)
else
  print("Failed:", message)
end

-- Verify 5 second timeout
local success, timeout, message = _PY.tcp_get_timeout_sync(conn_id)
if success then
  print("Current timeout:", timeout, "(" .. message .. ")")
  if timeout == 5 then
  print("✓ Socket timeout is correctly set to 5 seconds")
  else
  print("✗ Socket timeout is NOT set to 5 seconds")
  end
else
  print("Failed to get timeout:", message)
end

-- Test 5: Try a non-blocking read (should return immediately)
print("\n6. Testing non-blocking read...")
local success, message = _PY.tcp_set_timeout_sync(conn_id, 0)
if success then
  print("Set to non-blocking mode")
  
  -- Try to read - should return immediately with no data
  local success, data, message = _PY.tcp_read_sync(conn_id, 1024)
  if success then
  print("Read result:", message)
  if data == "" then
  print("✓ Non-blocking read correctly returned empty string immediately")
  else
  print("✗ Non-blocking read returned data when it shouldn't")
  end
  else
  print("Read failed:", message)
  end
else
  print("Failed to set non-blocking mode:", message)
end

-- Clean up
print("\n7. Closing connection...")
local success, message = _PY.tcp_close_sync(conn_id)
if success then
  print("Success:", message)
else
  print("Failed:", message)
end

print("\n=== Demo completed ===")
print("Key features of TCP timeout functions:")
print("- Set timeout for any TCP connection")
print("- Get current timeout value")
print("- Both sync and async versions available")
print("- Affects read/write operations")
print("- Useful for controlling connection behavior") 