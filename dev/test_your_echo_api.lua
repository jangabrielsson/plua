--
-- Test your exact WebSocketEchoServer API
--

print("=== Testing Your WebSocket Echo Server API ===")

-- Your exact function definition
function net.WebSocketEchoServer(host,port,debugFlag)
  
  local server = net.WebSocketServer()
  
  local function debug(...) 
    if debugFlag then print("[EchWS] "..tostring(server.server_id), string.format(...)) end
  end
  
  server:start(host, port, {
    receive = function(client, msg)
      debug("Received from client: %s", msg)
      server:send(client, "Echo "..msg)
    end,
    connected = function(client)
      debug("Client connected: %s", tostring(client))
    end,
    error = function(err)
      debug("Client error: %s", tostring(err))
    end,
    disconnected = function(client)
      debug("Client disconnected: %s", tostring(client))
    end
  })
  return server
end

-- Test the exact function
local echoServer = net.WebSocketEchoServer("localhost", 8892, true)

-- Test with client
setTimeout(function()
    local client = net.WebSocketClient()
    
    client:addEventListener("connected", function()
        print("✓ Connected to echo server")
        client:send("Test message 1")
        client:send("Test message 2")
    end)
    
    client:addEventListener("dataReceived", function(data)
        print("✓ Echo received:", data)
    end)
    
    client:connect("ws://localhost:8892")
    
    setTimeout(function()
        client:close()
        echoServer:stop()
    end, 2000)
    
end, 500)

print("Testing your exact API...")
