--[[
Sync Server with Python Echo Client Demo
This demonstrates:
1. Using synchronous TCP server in PLua
2. Performing synchronous write/read operations to connected clients
3. Testing with a Python echo client running in separate process
]]

-- QuickApp ID for Fibaro
local QA_ID = 5555

-- Main test function
local function runSyncServerPythonClientTest()
  print("[MAIN] Starting Sync Server with Python Echo Client Test")
  print("[MAIN] =================================================")
  
  -- Create sync TCP server
  print("[SERVER] Creating synchronous TCP server...")
  local server_id = _PY.tcp_server_create_sync("127.0.0.1", 8768)
  if not server_id then
    print("[SERVER] ✗ Failed to create server")
    return
  end
  print("[SERVER] ✓ Sync server created with ID:", server_id)
  
  -- Wait for server to be ready
  print("[MAIN] Waiting for server to be ready...")
  _PY.sleep(1)
  
  -- Accept client connection
  print("[SERVER] Waiting for client connection...")
  local result = _PY.tcp_server_accept_sync(server_id, 10.0)
  if result and result.success then
    local client_id = result.client_id
    local message = result.message
    print("[SERVER] ✓ Client connected! Client ID:", client_id, "Message:", message)
    
    -- Send welcome message
    local write_result = _PY.tcp_write_sync_client(client_id, "Welcome to the sync server!\n")
    if write_result and write_result.success then
      print("[SERVER] ✓ Welcome message sent:", write_result.bytes_written, "bytes")
    else
      print("[SERVER] ✗ Failed to send welcome:", write_result and write_result.message or "Unknown error")
    end
    
    -- Read echo response
    local read_result = _PY.tcp_read_sync_client(client_id, 1024)
    if read_result and read_result.success and read_result.data then
      print("[SERVER] ✓ Received echo:", read_result.data:gsub("\n", "\\n"))
    else
      print("[SERVER] ✗ Failed to read echo:", read_result and read_result.message or "Unknown error")
    end
    
    -- Send test messages and get echoes back
    local test_messages = {
      "Hello from PLua server!\n",
      "How are you?\n",
      "STATUS\n",
      "PING\n",
      "Goodbye!\n"
    }
    
    for i, msg in ipairs(test_messages) do
      print("[SERVER] Sending message", i, ":", msg:gsub("\n", "\\n"))
      
      -- Send message
      local write_result = _PY.tcp_write_sync_client(client_id, msg)
      if write_result and write_result.success then
        print("[SERVER] ✓ Message sent:", write_result.bytes_written, "bytes")
      else
        print("[SERVER] ✗ Failed to send message:", write_result and write_result.message or "Unknown error")
        break
      end
      
      -- Read echo response
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
    
  else
    print("[SERVER] ✗ Failed to accept client:", result and result.message or "Unknown error")
  end
  
  -- Close server
  print("[MAIN] Closing server...")
  _PY.tcp_server_close_sync(server_id)
  
  print("[MAIN] Test completed!")
end

local function start_python_client()

  -- Start Python echo client in separate process
  print("[MAIN] Starting Python echo client in separate process...")
  local python_script = "examples/basic/sync_server_client_demo.py"
  local python_cmd = string.format("python %s 8768", python_script)
  
  -- Use os.execute to run Python client in background
  local result = os.execute(python_cmd .. " &")
  if result then
    print("[MAIN] ✓ Python client started")
  else
    print("[MAIN] ✗ Failed to start Python client")
  end
  
  -- Wait a moment for client to connect
  _PY.sleep(2)
end

-- Run the test
setTimeout(start_python_client,0)
runSyncServerPythonClientTest()


-- Keep system running
setInterval(function() end,1000)