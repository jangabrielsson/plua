-- tcp_sync_only_demo.lua - Demonstration of synchronous TCP functions
print("=== Synchronous TCP Functions Demo ===")

-- Function to demonstrate a complete TCP conversation
local function tcp_conversation(host, port, request)
  print(string.format("\n--- TCP Conversation with %s:%d ---", host, port))
  
  -- Step 1: Connect
  print("1. Connecting...")
  local success, conn_id, message = _PY.tcp_connect_sync(host, port)
  print("   Result:", success, conn_id, message)
  
  if not success then
    print("   Failed to connect, aborting conversation")
    return false
  end
  
  -- Step 2: Send request
  print("2. Sending request...")
  local write_success, bytes_written, write_message = _PY.tcp_write_sync(conn_id, request)
  print("   Result:", write_success, bytes_written, write_message)
  
  if not write_success then
    print("   Failed to write, closing connection")
    _PY.tcp_close_sync(conn_id)
    return false
  end
  
  -- Step 3: Read response
  print("3. Reading response...")
  local read_success, data, read_message = _PY.tcp_read_sync(conn_id, 1024)
  print("   Result:", read_success, read_message)
  
  if read_success then
    print("   Response preview (first 150 chars):")
    print("   " .. string.sub(data, 1, 150) .. "...")
  end
  
  -- Step 4: Close connection
  print("4. Closing connection...")
  local close_success, close_message = _PY.tcp_close_sync(conn_id)
  print("   Result:", close_success, close_message)
  
  return success and write_success and read_success and close_success
end

-- Test 1: HTTP request to Google
print("\n=== Test 1: HTTP Request ===")
local http_request = "GET / HTTP/1.1\r\nHost: google.com\r\nConnection: close\r\n\r\n"
tcp_conversation("google.com", 80, http_request)

-- Test 2: Simple text request to a different server
print("\n=== Test 2: Simple Text Request ===")
local text_request = "Hello, server!\n"
tcp_conversation("httpbin.org", 80, "GET / HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n")

-- Test 3: Error handling - try to connect to a non-existent service
print("\n=== Test 3: Error Handling ===")
print("Attempting to connect to non-existent service...")
local success, conn_id, message = _PY.tcp_connect_sync("nonexistent.example.com", 9999)
print("Connect result:", success, conn_id, message)

-- Test 4: Multiple operations on same connection
print("\n=== Test 4: Multiple Operations ===")
print("Connecting to google.com...")
local success, conn_id, message = _PY.tcp_connect_sync("google.com", 80)
print("Connect:", success, conn_id, message)

if success then
  -- Send multiple requests
  local requests = {
    "GET / HTTP/1.1\r\nHost: google.com\r\nConnection: close\r\n\r\n",
    "HEAD / HTTP/1.1\r\nHost: google.com\r\nConnection: close\r\n\r\n"
  }
  
  for i, request in ipairs(requests) do
    print(string.format("Sending request %d...", i))
    local write_success, bytes_written, write_msg = _PY.tcp_write_sync(conn_id, request)
    print("Write result:", write_success, bytes_written, write_msg)
    
    if write_success then
      local read_success, data, read_msg = _PY.tcp_read_sync(conn_id, 512)
      print("Read result:", read_success, read_msg)
      if read_success then
        print("Response starts with:", string.sub(data, 1, 50) .. "...")
      end
    end
  end
  
  -- Close connection
  local close_success, close_msg = _PY.tcp_close_sync(conn_id)
  print("Final close:", close_success, close_msg)
end

print("\n=== Demo completed ===")
print("Key benefits of synchronous functions:")
print("- No callbacks needed")
print("- Direct return values")
print("- Sequential, easy-to-follow code")
print("- Simple error handling")
print("- Blocking operations (may not be suitable for all use cases)") 