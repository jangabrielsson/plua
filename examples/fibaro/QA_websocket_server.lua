-- WebSocket Server and Client Demo
-- Demonstrates PLua Python WebSocket server extension and Lua client

--%%name:WSServer

function QuickApp:onInit()
  self:debug(self.name)
  
  local server = net.WebSocketEchoServer("127.0.0.1", 8765, false)
  
  -- Wait a moment for the server to start
  setTimeout(function()
    print("[Client] Connecting to ws://127.0.0.1:8765 ...")
    local ws = net.WebSocketClient()
    
    local messages = {
      "Hello from TCP client!\n",
      "How are you?\n",
      "I'm fine, thank you!\n",
      "What's your name?\n",
      "My name is John Doe.\n",
      "What's your favorite color?\n",
      "My favorite color is blue\n"
    }
    ws:addEventListener("connected", function()
      print("[Client] connected")
      local function sender(n)
        if n > #messages then
          ws:close()
          return
        end
        ws:send(messages[n])
        setTimeout(function() sender(n+1) end, 500)
      end
      sender(1)
    end)
    
    ws:addEventListener("dataReceived", function(data)
      -- Only close after receiving echo message (not welcome message)
      print("[Client] Received from server:", data)
    end)
    
    ws:addEventListener("disconnected", function()
      print("[Client] Disconnected.")
    end)
    
    ws:addEventListener("error", function(err)
      print("[Client] Error:", err)
    end)
    
    ws:connect("ws://127.0.0.1:8765")
  end, 500) 
  
end