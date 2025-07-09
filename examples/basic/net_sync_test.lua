-- Test the new synchronous functions in the net module
print("=== Testing net module synchronous functions ===")

-- Test 1: Coroutine-based synchronous functions
print("\n--- Test 1: Coroutine-based sync functions ---")
local function test_coroutine_sync()
  print("Connecting to tcpbin.com:4242 using coroutine sync...")
  local success, conn_id, message = net.tcp_connect_sync("tcpbin.com", 4242)
  print("Connect result:", success, conn_id, message)
  
  if success then
    print("Sending message...")
    local write_success, bytes_written, write_msg = net.tcp_write_sync(conn_id, "Hello from net module!\n")
    print("Write result:", write_success, bytes_written, write_msg)
    
    if write_success then
      print("Reading response...")
      local read_success, data, read_msg = net.tcp_read_sync(conn_id, 1024)
      print("Read result:", read_success, read_msg)
      if read_success and data then
        print("Received:", data:gsub("\n", "\\n"))
      end
    end
    
    print("Closing connection...")
    local close_success, close_msg = net.tcp_close_sync(conn_id)
    print("Close result:", close_success, close_msg)
  end
end

-- Run the coroutine test
local co = coroutine.create(test_coroutine_sync)
coroutine.resume(co)

-- Test 2: Direct synchronous functions
print("\n--- Test 2: Direct sync functions ---")
print("Connecting to tcpbin.com:4242 using direct sync...")
local success, conn_id, message = net.tcp_connect_direct("tcpbin.com", 4242)
print("Connect result:", success, conn_id, message)

if success then
  print("Sending message...")
  local write_success, bytes_written, write_msg = net.tcp_write_direct(conn_id, "Hello from direct sync!\n")
  print("Write result:", write_success, bytes_written, write_msg)
  
  if write_success then
    print("Reading response...")
    local read_success, data, read_msg = net.tcp_read_direct(conn_id, 1024)
    print("Read result:", read_success, read_msg)
    if read_success and data then
      print("Received:", data:gsub("\n", "\\n"))
    end
  end
  
  print("Closing connection...")
  local close_success, close_msg = net.tcp_close_direct(conn_id)
  print("Close result:", close_success, close_msg)
end

print("\n=== Test completed ===") 