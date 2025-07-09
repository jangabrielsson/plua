--%%name:SyncAPIDemo
-- Synchronous API Demo
-- Demonstrates the new synchronous API for external system communication
-- This allows users to call api.hc3.restricted.send(str) without wrapping in coroutines

local mobdebug = require("mobdebug")

-- Setup the synchronous API server
local function setupSyncAPI()
  print("[SYNC API] Setting up TCP server for external system...")
  
  -- Setup the TCP server that external systems can connect to
  local server_id = _PY.sync_api_setup_server("127.0.0.1", 8767)
  print("[SYNC API] Server started on 127.0.0.1:8767 with ID:", server_id)
  
  return server_id
end

-- Example of user code that can call the synchronous API
local function userCodeExample()
  print("[USER] Starting user code example...")
  
  -- Wait a bit for external system to connect
  _PY.sleep(2)
  
  -- User can call this synchronously without any coroutine wrapping!
  print("[USER] Sending message to external system...")
  local success, response, message = _PY.sync_api_send("Hello from PLua!\n")
  
  if success then
    print("[USER] Success! Response:", response)
  else
    print("[USER] Failed:", message)
  end
  
  -- Send another message
  print("[USER] Sending second message...")
  success, response, message = _PY.sync_api_send("How are you?\n")
  
  if success then
    print("[USER] Success! Response:", response)
  else
    print("[USER] Failed:", message)
  end
  
  -- Send a command
  print("[USER] Sending command...")
  success, response, message = _PY.sync_api_send("STATUS\n")
  
  if success then
    print("[USER] Success! Response:", response)
  else
    print("[USER] Failed:", message)
  end
end

-- Simulate external system connecting and sending responses
local function simulateExternalSystem()
  print("[SIM] Starting external system simulation...")
  
  -- Wait for server to be ready
  _PY.sleep(1)
  
  -- Connect to the server
  local client = net.TCPSocket()
  client:connect("127.0.0.1", 8767, {
    success = function()
      print("[SIM] External system connected!")
      
      -- Start reading loop to respond to messages
      local function readLoop()
        client:read({
          success = function(data)
            print("[SIM] Received:", data:gsub("\n", "\\n"))
            
            -- Send a response based on the message
            local response
            if data:find("Hello") then
              response = "Hello back from external system!\n"
            elseif data:find("How are you") then
              response = "I'm doing great, thanks for asking!\n"
            elseif data:find("STATUS") then
              response = "STATUS: OK, all systems operational\n"
            else
              response = "Unknown command received\n"
            end
            
            print("[SIM] Sending response:", response:gsub("\n", "\\n"))
            client:write(response, {
              success = function()
                print("[SIM] Response sent successfully")
                -- Continue reading
                _PY.setTimeout(readLoop, 100)
              end,
              error = function(err)
                print("[SIM] Failed to send response:", err)
              end
            })
          end,
          error = function(err)
            print("[SIM] Read error:", err)
          end
        })
      end
      
      -- Start the read loop
      readLoop()
    end,
    error = function(err)
      print("[SIM] Failed to connect:", err)
    end
  })
end

function QuickApp:onInit()
  mobdebug.on()
  self:debug(self.name, self.id)
  
  print("[MAIN] Starting Synchronous API Demo")
  
  -- Setup the synchronous API server
  local server_id = setupSyncAPI()
  
  -- Simulate external system connecting
  simulateExternalSystem()
  
  -- Run user code example (this is what users would write)
  -- Note: No coroutine wrapping needed!
  userCodeExample()
  
  -- Keep the system running
  setInterval(function()
    print("[MAIN] System running...")
  end, 5000)
  
  -- Cleanup on exit
  _PY.setTimeout(function()
    print("[MAIN] Cleaning up...")
    _PY.sync_api_close()
  end, 30000)
end 