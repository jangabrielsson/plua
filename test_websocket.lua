--%%name:WebSocketTest
--%%type:com.fibaro.binarySwitch

print("WebSocket Test")
function QuickApp:onInit()
  self:debug("onInit")
  
  -- Test WebSocket client (non-TLS)
  self.ws = net.WebSocketClient()
  
  self.ws:addEventListener("connected", function() 
    self:debug("WebSocket connected!")
    self.ws:send("Hello from PLua!")
  end)
  
  self.ws:addEventListener("disconnected", function() 
    self:debug("WebSocket disconnected")
  end)
  
  self.ws:addEventListener("error", function(error) 
    self:error("WebSocket error:", error)
  end)
  
  self.ws:addEventListener("dataReceived", function(data) 
    self:debug("Received:", data)
  end)
  
  -- Connect to PieSocket echo server (non-TLS)
  self.ws:connect("ws://echo.piesocket.com/v3/channel_1?api_key=TEST")
  
  -- Test TLS WebSocket after 3 seconds
  setTimeout(function()
    self:debug("Testing TLS WebSocket...")
    self.ws_tls = net.WebSocketClientTls()
    
    self.ws_tls:addEventListener("connected", function() 
      self:debug("TLS WebSocket connected!")
      self.ws_tls:send("Hello from PLua TLS!")
    end)
    
    self.ws_tls:addEventListener("disconnected", function() 
      self:debug("TLS WebSocket disconnected")
    end)
    
    self.ws_tls:addEventListener("error", function(error) 
      self:error("TLS WebSocket error:", error)
    end)
    
    self.ws_tls:addEventListener("dataReceived", function(data) 
      self:debug("TLS Received:", data)
    end)
    
    -- Connect to echo.websocket.org (TLS)
    self.ws_tls:connect("wss://echo.websocket.org")
  end, 3000)
  
  -- Close connections after 10 seconds
  setTimeout(function()
    self:debug("Closing WebSocket connections...")
    if self.ws and self.ws:isOpen() then
      self.ws:close()
    end
    if self.ws_tls and self.ws_tls:isOpen() then
      self.ws_tls:close()
    end
  end, 10000)
end

function QuickApp:onStart()
  self:debug("onStart")
end

function QuickApp:onStop()
  self:debug("onStop")
end 