--%%name:SyncAPISingleTest
-- Single File Test for Synchronous API
-- Tests both server and client functionality in one file

print("[DEBUG] Script file loaded and starting execution...")

local mobdebug = require("mobdebug")

local client_connected = false
local server_client = nil

print("[DEBUG] Script started, about to setup server and client...")

-- Setup the asyncio-based TCP server
local function setupAsyncioTCPServer()
  print("[SERVER] Setting up asyncio-based TCP server...")
  local server = net.TCPServer(true) -- true for debug output
  server:start("127.0.0.1", 8768, function(client, addr)
    print("[SERVER] Client connected!")
    server_client = client
    -- Handle incoming data from client
    client:read({
      success = function(data)
        print("[SERVER] Received from client:", data:gsub("\n", "\\n"))
        -- Echo or respond as needed
        client:write("ACK: " .. data, {
          success = function()
            print("[SERVER] ACK sent")
          end,
          error = function(err)
            print("[SERVER] Failed to send ACK:", err)
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

-- Simulate external system connecting and sending responses (Lua client)
local function simulateExternalSystem()
  print("[SIM] Starting external system simulation...")
  local client = net.TCPSocket()
  client:connect("127.0.0.1", 8768, {
    success = function()
      print("[SIM] External system connected!")
      client_connected = true
      -- Start reading loop to respond to messages
      local function readLoop()
        client:read({
          success = function(data)
            print("[SIM] Received:", data:gsub("\n", "\\n"))
            -- Split data into lines and respond to each
            for line in data:gmatch("([^\n]+)") do
              local response
              if line:find("Hello") then
                response = "Hello back from external system!\n"
              elseif line:find("How are you") then
                response = "I'm doing great, thanks!\n"
              elseif line:find("STATUS") then
                response = "STATUS: OK\n"
              elseif line:find("PING") then
                response = "PONG\n"
              else
                response = "Unknown command\n"
              end
              print("[SIM] Sending response:", response:gsub("\n", "\\n"))
              client:write(response, {
                success = function()
                  print("[SIM] Response sent successfully")
                end,
                error = function(err)
                  print("[SIM] Failed to send response:", err)
                end
              })
            end
            -- Continue reading for next message
            readLoop()
          end,
          error = function(err)
            print("[SIM] Read error:", err)
          end
        })
      end
      readLoop()
    end,
    error = function(err)
      print("[SIM] Failed to connect:", err)
    end
  })
end

-- Test the asyncio-based API
local function testAsyncioAPI()
  print("[TEST] Starting asyncio-based API tests...")
  while not client_connected do
    print("[TEST] Waiting for external system to connect...")
    _PY.sleep(0.5)
  end
  -- Send test messages from server to client
  local test_msgs = {
    "Hello from PLua!\n",
    "How are you?\n",
    "STATUS\n",
    "PING\n",
    "UNKNOWN_COMMAND\n"
  }
  for i, msg in ipairs(test_msgs) do
    print("[TEST] Sending:", msg:gsub("\n", "\\n"))
    if server_client then
      server_client:write(msg, {
        success = function()
          print("[TEST] Message sent to client")
        end,
        error = function(err)
          print("[TEST] Failed to send message:", err)
        end
      })
    end
    _PY.sleep(0.5)
  end
  print("[TEST] All tests completed!")
end

print("[MAIN] Starting Asyncio API Single File Test")
print("[MAIN] ======================================")

setupAsyncioTCPServer()

-- Wait a moment for server to be fully ready
print("[MAIN] Waiting for server to be ready...")
_PY.sleep(1)

simulateExternalSystem()
testAsyncioAPI()

for i = 1, 5 do
  print("[MAIN] System running...")
  _PY.sleep(2)
end 