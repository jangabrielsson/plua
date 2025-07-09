-- TCP client test using coroutine pattern with synchronous network functions
-- The synchronous functions work perfectly with coroutines because they block and return values directly

local host = "tcpbin.com"
local port = 4242

-- Wrapper function to make synchronous tcp_connect work in coroutine context
local function tcp_connect_sync(host, port)
  local co = coroutine.running()
  if not co then
    error("tcp_connect_sync must be called from within a coroutine")
  end
  
  -- The synchronous function blocks and returns values directly
  return _PY.tcp_connect_sync(host, port)
end

-- Wrapper function to make synchronous tcp_write work in coroutine context
local function tcp_write_sync(conn_id, data)
  local co = coroutine.running()
  if not co then
    error("tcp_write_sync must be called from within a coroutine")
  end
  
  -- The synchronous function blocks and returns values directly
  return _PY.tcp_write_sync(conn_id, data)
end

-- Wrapper function to make synchronous tcp_read work in coroutine context
local function tcp_read_sync(conn_id, max_bytes)
  local co = coroutine.running()
  if not co then
    error("tcp_read_sync must be called from within a coroutine")
  end
  
  -- The synchronous function blocks and returns values directly
  return _PY.tcp_read_sync(conn_id, max_bytes)
end

-- Wrapper function to make synchronous tcp_close work in coroutine context
local function tcp_close_sync(conn_id)
  local co = coroutine.running()
  if not co then
    error("tcp_close_sync must be called from within a coroutine")
  end
  
  -- The synchronous function blocks and returns values directly
  return _PY.tcp_close_sync(conn_id)
end

-- Main test function that runs in a coroutine
local function test_tcp_client()
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
end

-- Start the test in a coroutine
test_tcp_client()
-- local co = coroutine.create(test_tcp_client)
-- coroutine.resume(co) 