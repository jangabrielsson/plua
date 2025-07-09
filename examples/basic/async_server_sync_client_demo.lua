--[[
Async Server with Synchronous Client Operations Demo
This demonstrates:
1. Using asyncio TCP server in PLua
2. Performing synchronous write/read operations to connected clients
3. Testing with a Python echo client
]]

-- QuickApp ID for Fibaro
local QA_ID = 5555

-- Main test function
local function runAsyncServerSyncClientTest()
  print("[MAIN] Starting Async Server with Sync Client Operations Test")
  print("[MAIN] =====================================================")
  
  -- Create async TCP server
  print("[SERVER] Creating async TCP server...")
  local server_id = _PY.tcp_server_create()
  if not server_id then
    print("[SERVER] ✗ Failed to create server")
    return
  end
  print("[SERVER] ✓ Async server created with ID:", server_id)
  
  -- Add event listeners
  _PY.tcp_server_add_event_listener(server_id, "client_connected", function(client_id, addr)
    print("[SERVER] ✓ Client connected! Client ID:", client_id, "Address:", addr)
    
    -- Send welcome message using synchronous write
    local write_result = _PY.tcp_write_sync_client(client_id, "Welcome to the async server!\n")
    if write_result and write_result.success then
      print("[SERVER] ✓ Welcome message sent:", write_result.bytes_written, "bytes")
    else
      print("[SERVER] ✗ Failed to send welcome:", write_result and write_result.message or "Unknown error")
    end
    
    -- Read echo response using synchronous read
    local read_result = _PY.tcp_read_sync_client(client_id, 1024)
    if read_result and read_result.success and read_result.data then
      print("[SERVER] ✓ Received echo:", read_result.data:gsub("\n", "\\n"))
    else
      print("[SERVER] ✗ Failed to read echo:", read_result and read_result.message or "Unknown error")
    end
    
    -- Send a test message and get echo back
    local test_messages = {
      "Hello from PLua server!\n",
      "How are you?\n",
      "STATUS\n",
      "PING\n",
      "Goodbye!\n"
    }
    
    for i, msg in ipairs(test_messages) do
      print("[SERVER] Sending message", i, ":", msg:gsub("\n", "\\n"))
      
      -- Send message using synchronous write
      local write_result = _PY.tcp_write_sync_client(client_id, msg)
      if write_result and write_result.success then
        print("[SERVER] ✓ Message sent:", write_result.bytes_written, "bytes")
      else
        print("[SERVER] ✗ Failed to send message:", write_result and write_result.message or "Unknown error")
        break
      end
      
      -- Read echo response using synchronous read
      local read_result = _PY.tcp_read_sync_client(client_id, 1024)
      if read_result and read_result.success and read_result.data then
        print("[SERVER] ✓ Received echo:", read_result.data:gsub("\n", "\\n"))
      else
        print("[SERVER] ✗ Failed to read echo:", read_result and read_result.message or "Unknown error")
        break
      end
      
      -- Small delay between messages
      _PY.sleep(0.5)
    end
    
    print("[SERVER] All messages sent, closing client connection")
    _PY.tcp_close_sync_client(client_id)
  end)
  
  _PY.tcp_server_add_event_listener(server_id, "client_disconnected", function(client_id)
    print("[SERVER] Client disconnected:", client_id)
  end)
  
  -- Start server
  print("[SERVER] Starting server on 127.0.0.1:8768...")
  _PY.tcp_server_start(server_id, "127.0.0.1", 8768)
  
  -- Wait for server to be ready with timeout
  print("[MAIN] Waiting for server to be ready...")
  local ready = false
  for i = 1, 50 do  -- Wait up to 5 seconds
    if _PY.tcp_server_is_ready(server_id) then
      ready = true
      break
    end
    _PY.sleep(0.1)
  end
  
  if not ready then
    print("[SERVER] ✗ Server failed to become ready within timeout")
    return
  end
  print("[SERVER] ✓ Server is ready and listening")
  
  -- Start Python echo client in separate process
  print("[MAIN] Starting Python echo client...")
  local python_script = "examples/basic/sync_server_client_demo.py"
  local python_cmd = string.format("python %s 8768", python_script)
  
  -- Use os.execute to run Python client in background
  local result = os.execute(python_cmd .. " &")
  if result then
    print("[MAIN] ✓ Python client started")
  else
    print("[MAIN] ✗ Failed to start Python client")
  end
  
  -- Keep server running for a while to handle client
  print("[MAIN] Server running for 10 seconds...")
  for i = 1, 10 do
    _PY.sleep(1)
    if i % 2 == 0 then
      print("[MAIN] Server running...", i, "seconds")
    end
  end
  
  -- Close server
  print("[MAIN] Closing server...")
  _PY.tcp_server_close(server_id)
  
  print("[MAIN] Test completed!")
end

-- Run the test
runAsyncServerSyncClientTest()

-- Keep system running
for i = 1, 3 do
  print("[MAIN] System running...")
  _PY.sleep(2)
end 