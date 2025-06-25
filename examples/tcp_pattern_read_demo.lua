-- tcp_pattern_read_demo.lua - Demonstration of TCP read patterns
print("=== TCP Read Patterns Demo ===")

-- Test 1: Read specific number of bytes
print("\n=== Test 1: Read 100 bytes ===")
local success, conn_id, message = _PY.tcp_connect_sync("google.com", 80)
if success then
  print("Connected:", message)
  
  -- Send HTTP request
  local request = "GET / HTTP/1.1\r\nHost: google.com\r\nConnection: close\r\n\r\n"
  local write_success, bytes_written, write_message = _PY.tcp_write_sync(conn_id, request)
  if write_success then
    print("Request sent:", write_message)
    
    -- Read exactly 100 bytes
    local read_success, data, read_message = _PY.tcp_read_sync(conn_id, 100)
    if read_success then
      print("Read result:", read_message)
      print("Data received:", #data, "bytes")
      print("Data preview:", string.sub(data, 1, 50) .. "...")
    else
      print("Read failed:", read_message)
    end
  end
  
  _PY.tcp_close_sync(conn_id)
else
  print("Failed to connect:", message)
end

-- Test 2: Read a line
print("\n=== Test 2: Read a line (*l) ===")
local success2, conn_id2, message2 = _PY.tcp_connect_sync("google.com", 80)
if success2 then
  print("Connected:", message2)
  
  -- Send HTTP request
  local request = "GET / HTTP/1.1\r\nHost: google.com\r\nConnection: close\r\n\r\n"
  local write_success, bytes_written, write_message = _PY.tcp_write_sync(conn_id2, request)
  if write_success then
    print("Request sent:", write_message)
    
    -- Read a line
    local read_success, data, read_message = _PY.tcp_read_sync(conn_id2, "*l")
    if read_success then
      print("Read result:", read_message)
      print("Line received:", #data, "chars")
      print("Line content:", data)
    else
      print("Read failed:", read_message)
    end
  end
  
  _PY.tcp_close_sync(conn_id2)
else
  print("Failed to connect:", message2)
end

-- Test 3: Read all available data
print("\n=== Test 3: Read all data (*a) ===")
local success3, conn_id3, message3 = _PY.tcp_connect_sync("httpbin.org", 80)
if success3 then
  print("Connected:", message3)
  
  -- Send HTTP request
  local request = "GET / HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n"
  local write_success, bytes_written, write_message = _PY.tcp_write_sync(conn_id3, request)
  if write_success then
    print("Request sent:", write_message)
    
    -- Read all available data
    local read_success, data, read_message = _PY.tcp_read_sync(conn_id3, "*a")
    if read_success then
      print("Read result:", read_message)
      print("Total data received:", #data, "bytes")
      print("Response preview (first 200 chars):")
      print(string.sub(data, 1, 200) .. "...")
    else
      print("Read failed:", read_message)
    end
  end
  
  _PY.tcp_close_sync(conn_id3)
else
  print("Failed to connect:", message3)
end

-- Test 4: Multiple reads with different patterns
print("\n=== Test 4: Multiple reads with different patterns ===")
local success4, conn_id4, message4 = _PY.tcp_connect_sync("google.com", 80)
if success4 then
  print("Connected:", message4)
  
  -- Send HTTP request
  local request = "GET / HTTP/1.1\r\nHost: google.com\r\nConnection: close\r\n\r\n"
  local write_success, bytes_written, write_message = _PY.tcp_write_sync(conn_id4, request)
  if write_success then
    print("Request sent:", write_message)
    
    -- Read first 50 bytes
    local read_success, data, read_message = _PY.tcp_read_sync(conn_id4, 50)
    if read_success then
      print("First 50 bytes:", read_message)
      print("Data:", string.sub(data, 1, 30) .. "...")
    end
    
    -- Read a line
    local read_success2, data2, read_message2 = _PY.tcp_read_sync(conn_id4, "*l")
    if read_success2 then
      print("Next line:", read_message2)
      print("Line:", data2)
    end
    
    -- Read remaining data
    local read_success3, data3, read_message3 = _PY.tcp_read_sync(conn_id4, "*a")
    if read_success3 then
      print("Remaining data:", read_message3)
      print("Remaining bytes:", #data3)
    end
  end
  
  _PY.tcp_close_sync(conn_id4)
else
  print("Failed to connect:", message4)
end

-- Test 5: Error handling with invalid patterns
print("\n=== Test 5: Error handling with invalid patterns ===")
local success5, conn_id5, message5 = _PY.tcp_connect_sync("google.com", 80)
if success5 then
  print("Connected:", message5)
  
  -- Try to read with invalid pattern
  local read_success, data, read_message = _PY.tcp_read_sync(conn_id5, "invalid_pattern")
  if read_success then
    print("Read succeeded (unexpected):", read_message)
  else
    print("Read failed (expected):", read_message)
  end
  
  _PY.tcp_close_sync(conn_id5)
else
  print("Failed to connect:", message5)
end

print("\n=== Demo completed ===")
print("Available read patterns:")
print("- Number (e.g., 1024): Read exactly N bytes")
print("- '*l': Read a line (terminated by LF)")
print("- '*a': Read all available data until connection closes")
print("- Invalid patterns will return an error") 