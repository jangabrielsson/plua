-- TCP client using async API, but with coroutine/yield pattern for sync-like code

local host = "tcpbin.com"
local port = 4242

-- Wrapper: async connect, but looks synchronous
local function tcp_connect_sync(host, port)
  local co = coroutine.running()
  print("[DEBUG] tcp_connect_sync: yielding for connect...")
  if not co then error("Must be called from within a coroutine") end
  _PY.tcp_connect(host, port, function(success, conn_id, message)
    print("[DEBUG] tcp_connect_sync: callback called", success, conn_id, message)
    local ok, err = coroutine.resume(co, success, conn_id, message)
    print("[DEBUG] tcp_connect_sync: coroutine.resume returned", ok, err)
  end)
  local result = {coroutine.yield()}
  print("[DEBUG] tcp_connect_sync: resumed with", table.unpack(result))
  return table.unpack(result)
end

-- Wrapper: async write, but looks synchronous
local function tcp_write_sync(conn_id, data)
  local co = coroutine.running()
  print("[DEBUG] tcp_write_sync: yielding for write...")
  if not co then error("Must be called from within a coroutine") end
  _PY.tcp_write(conn_id, data, function(success, bytes_written, message)
    print("[DEBUG] tcp_write_sync: callback called", success, bytes_written, message)
    local ok, err = coroutine.resume(co, success, bytes_written, message)
    print("[DEBUG] tcp_write_sync: coroutine.resume returned", ok, err)
  end)
  local result = {coroutine.yield()}
  print("[DEBUG] tcp_write_sync: resumed with", table.unpack(result))
  return table.unpack(result)
end

-- Wrapper: async read, but looks synchronous
local function tcp_read_sync(conn_id, max_bytes)
  local co = coroutine.running()
  print("[DEBUG] tcp_read_sync: yielding for read...")
  if not co then error("Must be called from within a coroutine") end
  _PY.tcp_read(conn_id, max_bytes, function(success, data, message)
    print("[DEBUG] tcp_read_sync: callback called", success, data, message)
    local ok, err = coroutine.resume(co, success, data, message)
    print("[DEBUG] tcp_read_sync: coroutine.resume returned", ok, err)
  end)
  local result = {coroutine.yield()}
  print("[DEBUG] tcp_read_sync: resumed with", table.unpack(result))
  return table.unpack(result)
end

-- Wrapper: async close, but looks synchronous
local function tcp_close_sync(conn_id)
  local co = coroutine.running()
  print("[DEBUG] tcp_close_sync: yielding for close...")
  if not co then error("Must be called from within a coroutine") end
  _PY.tcp_close(conn_id, function(success, message)
    print("[DEBUG] tcp_close_sync: callback called", success, message)
    local ok, err = coroutine.resume(co, success, message)
    print("[DEBUG] tcp_close_sync: coroutine.resume returned", ok, err)
  end)
  local result = {coroutine.yield()}
  print("[DEBUG] tcp_close_sync: resumed with", table.unpack(result))
  return table.unpack(result)
end

-- Timer test wrapper
local function timer_test_sync()
  local co = coroutine.running()
  print("[DEBUG] timer_test_sync: yielding for timer...")
  if not co then error("Must be called from within a coroutine") end
  setTimeout(function()
    print("[DEBUG] timer_test_sync: timer callback called")
    local ok, err = coroutine.resume(co, "Timer fired!")
    print("[DEBUG] timer_test_sync: coroutine.resume returned", ok, err)
  end, 2000)
  local result = {coroutine.yield()}
  print("[DEBUG] timer_test_sync: resumed with", table.unpack(result))
  return table.unpack(result)
end

-- Main logic in a coroutine
local function main()
  print("Connecting to " .. host .. ":" .. port)
  local ok, client_id, msg = tcp_connect_sync(host, port)
  print("Connect result:", ok, client_id, msg)
  if not ok then 
    print("Connect failed, trying timer test...")
    local timer_result = timer_test_sync()
    print("Timer test result:", timer_result)
    return 
  end

  local message = "Hello, tcpbin!\n"
  local ok, bytes_written, write_msg = tcp_write_sync(client_id, message)
  print("Write result:", ok, bytes_written, write_msg)
  if not ok then tcp_close_sync(client_id) return end

  print("Waiting for echo...")
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

-- Start the main logic in a coroutine
-- local co = coroutine.create(main)
-- coroutine.resume(co) 
function QuickApp:onInit()
   main()
end