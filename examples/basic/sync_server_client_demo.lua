print("[DEBUG] Top-level: sync_server_client_demo.lua is being executed!")
--%%name:SyncServerClientDemo
-- Fully Synchronous TCP Server and Client Demo
-- Uses tcp_write_sync/tcp_read_sync for all communication
-- Demonstrates how to use synchronous API for both server and client

print("[DEBUG] Script file loaded and starting execution...")

local mobdebug = require("mobdebug")

function QuickApp:onInit()
  mobdebug.on()
  self:debug(self.name, self.id)
  
  print("[DEBUG] Script started, about to setup synchronous server and client...")

  -- Setup the synchronous TCP server
  local function setupSyncServer()
    print("[SERVER] Setting up synchronous TCP server...")
    local server_id = _PY.tcp_server_create_sync("127.0.0.1", 8768)
    if server_id then
      print("[SERVER] ✓ Synchronous server created with ID:", server_id)
      return server_id
    else
      print("[SERVER] ✗ Failed to create synchronous server")
      return nil
    end
  end

  -- Accept client connections synchronously
  local function acceptClient(server_id)
    print("[SERVER] Waiting for client connection...")
    local success, client_id, message = _PY.tcp_server_accept_sync(server_id, 10.0) -- 10 second timeout
    if success then
      print("[SERVER] ✓ Client connected! Client ID:", client_id, "Message:", message)
      return client_id
    else
      print("[SERVER] ✗ Failed to accept client:", message)
      return nil
    end
  end

  -- Handle client communication synchronously
  local function handleClient(client_id)
    print("[SERVER] Starting synchronous communication with client", client_id)
    -- Send welcome message
    local success, bytes_written, msg = _PY.tcp_write_sync(client_id, "Welcome to synchronous server!\n")
    if success then
      print("[SERVER] ✓ Welcome message sent:", bytes_written, "bytes")
    else
      print("[SERVER] ✗ Failed to send welcome:", msg)
      return
    end
    -- Read client messages and respond
    local message_count = 0
    while message_count < 5 do
      print("[SERVER] Waiting for client message...")
      local success, data, msg = _PY.tcp_read_sync(client_id, 1024)
      if success then
        if data and data ~= "" then
          print("[SERVER] ✓ Received from client:", data:gsub("\n", "\\n"))
          message_count = message_count + 1
          -- Send response based on message
          local response
          if data:find("Hello") then
            response = "Hello back from synchronous server!\n"
          elseif data:find("How are you") then
            response = "I'm doing great, thanks!\n"
          elseif data:find("STATUS") then
            response = "STATUS: OK\n"
          elseif data:find("PING") then
            response = "PONG\n"
          else
            response = "Unknown command\n"
          end
          local success, bytes_written, msg = _PY.tcp_write_sync(client_id, response)
          if success then
            print("[SERVER] ✓ Response sent:", bytes_written, "bytes")
          else
            print("[SERVER] ✗ Failed to send response:", msg)
            break
          end
        else
          print("[SERVER] Client sent empty message, continuing...")
        end
      else
        print("[SERVER] ✗ Failed to read from client:", msg)
        break
      end
    end
    print("[SERVER] Communication completed, closing client connection")
    _PY.tcp_close_sync(client_id)
  end

  -- Simulate external system (synchronous client)
  local function simulateSyncClient()
    print("[CLIENT] Starting synchronous client simulation...")
    print("[CLIENT] Connecting to server...")
    
    -- Use the new sync client function to connect to our sync server
    local result = _PY.tcp_connect_to_sync_server("127.0.0.1", 8768)
    print("[DEBUG] Raw tcp_connect_to_sync_server return:", result, type(result))
    if result and result.success then
      local client_id = result.client_id
      local message = result.message
      print("[CLIENT] ✓ Connected to server! Client ID:", client_id, "Message:", message)
      
      -- Short delay to allow server to accept
      _PY.sleep(0.2)
      
      -- Send initial message to server
      local write_result = _PY.tcp_write_sync_client(client_id, "Hello from client!\n")
      print("[CLIENT] Sent initial message to server.")
      
      -- Read response from server
      local read_result = _PY.tcp_read_sync_client(client_id, 1024)
      print("[DEBUG] Raw tcp_read_sync_client return:", read_result, type(read_result))
      if read_result and read_result.success and read_result.data then
        print("[CLIENT] ✓ Received response:", read_result.data:gsub("\n", "\\n"))
      else
        print("[CLIENT] ✗ Failed to read response:", read_result and read_result.message or "Unknown error")
        return
      end
      
      -- Send test messages
      local test_messages = {
        "Hello from synchronous client!\n",
        "How are you?\n",
        "STATUS\n",
        "PING\n",
        "Goodbye!\n"
      }
      
      for i, msg in ipairs(test_messages) do
        print("[CLIENT] Sending message", i, ":", msg:gsub("\n", "\\n"))
        
        -- Send message using sync client API
        local write_result = _PY.tcp_write_sync_client(client_id, msg)
        if write_result and write_result.success then
          print("[CLIENT] ✓ Message sent:", write_result.bytes_written, "bytes")
        else
          print("[CLIENT] ✗ Failed to send message:", write_result and write_result.message or "Unknown error")
          break
        end
        
        -- Read response using sync client API
        local read_result = _PY.tcp_read_sync_client(client_id, 1024)
        if read_result and read_result.success and read_result.data then
          print("[CLIENT] ✓ Received response:", read_result.data:gsub("\n", "\\n"))
        else
          print("[CLIENT] ✗ Failed to read response:", read_result and read_result.message or "Unknown error")
          break
        end
        
        -- Small delay between messages
        _PY.sleep(0.5)
      end
      
      print("[CLIENT] All messages sent, closing connection")
      _PY.tcp_close_sync_client(client_id)
      
    else
      print("[CLIENT] ✗ Failed to connect:", message)
    end
  end

  -- Main test function
  local function runSyncServerClientTest()
    print("[MAIN] Starting Synchronous Server/Client Test")
    print("[MAIN] =======================================")
    
    -- Setup synchronous server
    print("[SERVER] Setting up synchronous TCP server...")
    local server_id = _PY.tcp_server_create_sync("127.0.0.1", 8768)
    if server_id then
      print("[SERVER] ✓ Synchronous server created with ID:", server_id)
      
      -- Wait a moment for server to be ready
      print("[MAIN] Waiting for server to be ready...")
      _PY.sleep(0.2)
      
      -- Start client simulation immediately before blocking accept
      local client_success, client_id, client_message = pcall(simulateSyncClient)
      print("[DEBUG] simulateSyncClient returned:", client_success, client_id, client_message)
      
      -- Server waits for client connection
      print("[SERVER] Waiting for client connection...")
      local result = _PY.tcp_server_accept_sync(server_id, 10.0)
      print("[DEBUG] Raw tcp_server_accept_sync return:", result, type(result))
      print("[DEBUG] tcp_server_accept_sync returned:", result and result.success, result and result.client_id, result and result.message)
      if result and result.success then
        local client_id = result.client_id
        local message = result.message
        print("[SERVER] ✓ Client connected! Client ID:", client_id, "Message:", message)
        
        -- Read message from client
        local read_result = _PY.tcp_read_sync_client(client_id, 1024)
        print("[DEBUG] tcp_read_sync_client returned:", read_result and read_result.success, read_result and read_result.data, read_result and read_result.message)
        if read_result and read_result.success and read_result.data then
          print("[SERVER] ✓ Received message:", read_result.data:gsub("\n", "\\n"))
          
          -- Send response
          local response = "Server received: " .. read_result.data:gsub("\n", "") .. "\n"
          local write_result = _PY.tcp_write_sync_client(client_id, response)
          print("[DEBUG] tcp_write_sync_client (response) returned:", write_result and write_result.success, write_result and write_result.bytes_written, write_result and write_result.message)
          if write_result and write_result.success then
            print("[SERVER] ✓ Response sent:", write_result.bytes_written, "bytes")
          else
            print("[SERVER] ✗ Failed to send response:", write_result and write_result.message or "Unknown error")
          end
        else
          print("[SERVER] ✗ Failed to read message:", read_result and read_result.message or "Unknown error")
        end
        
        print("[SERVER] Closing client connection")
        _PY.tcp_close_sync_client(client_id)
        
      else
        print("[SERVER] ✗ Failed to accept client:", result and result.message or "Unknown error")
      end
      
      -- Close server
      print("[MAIN] Closing server...")
      _PY.tcp_server_close_sync(server_id)
      
    else
      print("[SERVER] ✗ Failed to create server")
    end
    
    print("[MAIN] Test completed!")
  end

  runSyncServerClientTest()
  for i = 1, 3 do
    print("[MAIN] System running...")
    _PY.sleep(2)
  end
end 