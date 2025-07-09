-- Test async TCP functions with coroutine pattern
-- This should now work with the updated callback system

local host = "tcpbin.com"
local port = 4242

-- Wrapper function to make async tcp_connect appear synchronous
local function tcp_connect_sync(host, port)
  local co = coroutine.running()
  if not co then
    error("tcp_connect_sync must be called from within a coroutine")
  end
  
  _PY.tcp_connect(host, port, function(success, conn_id, message)
    coroutine.resume(co, success, conn_id, message)
  end)
  
  return coroutine.yield()
end

-- Wrapper function to make async tcp_write appear synchronous
local function tcp_write_sync(conn_id, data)
  local co = coroutine.running()
  if not co then
    error("tcp_write_sync must be called from within a coroutine")
  end
  
  _PY.tcp_write(conn_id, data, function(success, bytes_written, message)
    coroutine.resume(co, success, bytes_written, message)
  end)
  
  return coroutine.yield()
end

-- Wrapper function to make async tcp_read appear synchronous
local function tcp_read_sync(conn_id, max_bytes)
  local co = coroutine.running()
  if not co then
    error("tcp_read_sync must be called from within a coroutine")
  end
  
  _PY.tcp_read(conn_id, max_bytes, function(success, data, message)
    coroutine.resume(co, success, data, message)
  end)
  
  return coroutine.yield()
end

-- Wrapper function to make async tcp_close appear synchronous
local function tcp_close_sync(conn_id)
  local co = coroutine.running()
  if not co then
    error("tcp_close_sync must be called from within a coroutine")
  end
  
  _PY.tcp_close(conn_id, function(success, message)
    coroutine.resume(co, success, message)
  end)
  
  return coroutine.yield()
end

-- Main test function that runs in a coroutine
local function test_async_tcp_client()
  print("Testing async TCP with coroutine pattern...")
  print("Connecting to " .. host .. ":" .. port)
  
  local ok, client_id, msg = tcp_connect_sync(host, port)
  print("Connect result:", ok, client_id, msg)
  if not ok then
    print("Failed to connect")
    return
  end

  print("Connected! Client ID:", client_id)

  local msg = "Hello, tcpbin!\n"
  local ok, bytes_written, write_msg = tcp_write_sync(client_id, msg)
  print("Write result:", ok, bytes_written, write_msg)
  if not ok then
    print("Write failed:", write_msg)
    tcp_close_sync(client_id)
    return
  end

  print("Message sent, waiting for response...")

  local ok, data, read_msg = tcp_read_sync(client_id, 1024)
  print("Read result:", ok, data, read_msg)
  if ok and data then
    print("Received:", data)
  else
    print("Read failed:", read_msg)
  end

  tcp_close_sync(client_id)
  print("Connection closed.")
  print("Test completed!")
end

-- Start the test in a coroutine
local co = coroutine.create(test_async_tcp_client)
coroutine.resume(co) 