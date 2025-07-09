--%%name:SyncClientDemo
-- Synchronous TCP Client Demo
-- Shows how to use tcp_write_sync/tcp_read_sync with a client connection
-- Note: PLua only supports synchronous clients, not synchronous servers

print("[DEBUG] Script file loaded and starting execution...")

local mobdebug = require("mobdebug")

function QuickApp:onInit()
  mobdebug.on()
  self:debug(self.name, self.id)
  
  print("[DEBUG] Script started, about to setup server and synchronous client...")

  -- Setup an async TCP server (using existing API)
  local function setupAsyncServer()
    print("[SERVER] Setting up async TCP server...")
    local server = net.TCPServer(true) -- true for debug output
    server:start("127.0.0.1", 8768, function(client, addr)
      print("[SERVER] Client connected!")
      -- Handle incoming data from client
      client:read({
        success = function(data)
          print("[SERVER] Received from client:", data:gsub("\n", "\\n"))
          -- Echo the message back
          client:write("Echo: " .. data, {
            success = function()
              print("[SERVER] Echo sent")
            end,
            error = function(err)
              print("[SERVER] Failed to send echo:", err)
            end
          })
          -- Continue reading
          client:read({
            success = function(d) 
              print("[SERVER] More:", d) 
            end,
            error = function(err)
              print("[SERVER] Read error:", err)
            end
          })
        end,
        error = function(err)
          print("[SERVER] Read error:", err)
        end
      })
    end)
    return server
  end

  -- Synchronous client using tcp_write_sync/tcp_read_sync
  local function runSyncClient()
    print("[CLIENT] Starting synchronous client...")
    
    -- Connect to server synchronously
    print("[CLIENT] Connecting to server...")
    local success, client_id, message = _PY.tcp_connect_sync("127.0.0.1", 8768)
    if success then
      print("[CLIENT] ✓ Connected to server! Client ID:", client_id, "Message:", message)
      
      -- Send test messages using synchronous API
      local test_messages = {
        "Hello from synchronous client!\n",
        "How are you?\n",
        "STATUS\n",
        "PING\n",
        "Goodbye!\n"
      }
      
      for i, msg in ipairs(test_messages) do
        print("[CLIENT] Sending message", i, ":", msg:gsub("\n", "\\n"))
        
        -- Send message using synchronous API
        local success, bytes_written, msg = _PY.tcp_write_sync(client_id, msg)
        if success then
          print("[CLIENT] ✓ Message sent:", bytes_written, "bytes")
        else
          print("[CLIENT] ✗ Failed to send message:", msg)
          break
        end
        
        -- Read response using synchronous API
        local success, data, msg = _PY.tcp_read_sync(client_id, 1024)
        if success and data then
          print("[CLIENT] ✓ Received response:", data:gsub("\n", "\\n"))
        else
          print("[CLIENT] ✗ Failed to read response:", msg)
          break
        end
        
        -- Small delay between messages
        _PY.sleep(0.5)
      end
      
      print("[CLIENT] All messages sent, closing connection")
      _PY.tcp_close_sync(client_id)
      
    else
      print("[CLIENT] ✗ Failed to connect:", message)
    end
  end

  -- Main test sequence
  local function runTest()
    print("[MAIN] Starting Synchronous Client Test")
    print("[MAIN] ==================================")
    
    -- Setup async server
    local server = setupAsyncServer()
    
    -- Wait a moment for server to be ready
    print("[MAIN] Waiting for server to be ready...")
    _PY.sleep(1)
    
    -- Run synchronous client
    runSyncClient()
    
    -- Keep the system running for a while to observe
    for i = 1, 3 do
      print("[MAIN] System running...")
      _PY.sleep(2)
    end
    
    -- Stop server
    server:stop()
    print("[MAIN] Test completed!")
  end

  -- Run the test
  runTest()
end 