-- WebSocket Server and Client Demo
-- Demonstrates PLua Python WebSocket server extension and Lua client

local _PY = _PY or {}

local websocket_server_create = _PY.websocket_server_create
local websocket_server_start = _PY.websocket_server_start
local websocket_server_add_event_listener = _PY.websocket_server_add_event_listener
local websocket_server_send = _PY.websocket_server_send
local websocket_server_close = _PY.websocket_server_close

-- Create WebSocket server
local server_id = _PY.websocket_server_create()
print("[Server] Created server with id:", server_id)

-- Register server event listeners
_PY.websocket_server_add_event_listener(server_id, "client_connected", function(client)
  print("[Server] Client connected:", tostring(client))
  -- Optionally send a welcome message
  _PY.websocket_server_send(server_id, client, "Welcome client!")
end)

_PY.websocket_server_add_event_listener(server_id, "message", function(client, msg)
  print("[Server] Received from client:", msg)
  -- Echo the message back
  local reply = "Echo: " .. msg
  print("[Server] echo message:",reply)
  _PY.websocket_server_send(server_id, client, reply)
end)

_PY.websocket_server_add_event_listener(server_id, "client_disconnected", function(client)
  print("[Server] Client disconnected:", tostring(client))
end)

_PY.websocket_server_add_event_listener(server_id, "error", function(err)
  print("[Server] Error:", err)
end)

-- Start the server on localhost:8765
_PY.websocket_server_start(server_id, "127.0.0.1", 8765)
print("[Server] Listening on ws://127.0.0.1:8765")

function net.WebSocketServer(debugFlag)
  local self = { _debug = debugFlag }
  local server_id = websocket_server_create()
  self.server_id = server_id
  
  local function debug(...) 
    if self._debug then print("[Server] "..tostring(self.server_id), string.format(...)) end
  end
  
  debug("Created WS server with id: %s", tostring(server_id))
  
  -- Register server event listeners
  websocket_server_add_event_listener(server_id, "client_connected", function(client)
    debug("Client connected: %", tostring(client))
    if self.callbacks.connected then
      local stat,res = pcall(self.callbacks.connected, client)
      if not stat then
        debug("Error in connected callback: %s", tostring(res))
      end
    end
  end)
  
  websocket_server_add_event_listener(server_id, "message", function(client, msg)
    debug("Received from client: %s", msg)
    if self.callbacks.receive then
      local stat,res = pcall(self.callback, client, msg)
      if not stat then
        debug("Error in callback : %s", tostring(res))
      end
    end
  end)
  
  websocket_server_add_event_listener(server_id, "client_disconnected", function(client)
    if self.callbacks.disconnected then
      local stat,res = pcall(self.callbacks.disconnected, client)
      if not stat then
        debug("Error in disconnected callback: %s", tostring(res))
      end
    end
  end)
  
  websocket_server_add_event_listener(server_id, "error", function(err)
    debug("Error: %s", tostring(err))
    if self.callbacks.error then
      local stat,res = pcall(self.callbacks.error, err)
      if not stat then
        debug("Error in error callback: %s", tostring(res))
      end
    end
  end)
  
  function self:start(host, port, callbacks)
    assert(type(host) == "string", "host must be a string")
    assert(type(port) == "number", "port must be a number")
    self.callback = callbacks
    websocket_server_start(server_id, host, port)
    debug("Listening on ws://%s:%s", host, port)
  end
  
  function self:send(client, msg)
    if not self.server_id then
      return false, "Server not started"
    end
    return websocket_server_send(self.server_id, client, msg)
  end

  function self:stop()
    if self.server_id then
      websocket_server_close(self.server_id)
      self.server_id = nil
    end
  end
  
  return self
end

function net.WebSocketEchoServer(host,port,debugFlag)

  local server = net.WebSocketServer(debugFlag)

  local function debug(...) 
    if debugFlag then print("[EchWS] "..tostring(server.server_id), string.format(...)) end
  end

  server:start(host, port, {
    receieve = function(client, msg)
      debug("Received from client: %s", msg)
      server:send(client, "Echo "..msg)
    end,
    connected = function(client)
      debug("Client connected: %s", tostring(client))
    end,
    disconnected = function(client)
      debug("Client disconnected: %s", tostring(client))
    end
  })
  return server
end

-- Wait a moment for the server to start
setTimeout(function()
  print("[Client] Connecting to ws://127.0.0.1:8765 ...")
  local ws = net.WebSocketClient()

  ws:addEventListener("connected", function()
    print("[Client] Connected!")
    ws:send("Hello from Lua client!")
  end)

  ws:addEventListener("dataReceived", function(data)
    print("[Client] Received from server:", data)
    -- Only close after receiving echo message (not welcome message)
    if string.find(data, "^Echo:") then
      print("[Client] Received echo, closing connection...")
      ws:close()
      -- Stop server after short delay
      setTimeout(function()
        print("[Server] Closing server...")
        _PY.websocket_server_close(server_id)
      end, 500)
    end
  end)

  ws:addEventListener("disconnected", function()
    print("[Client] Disconnected.")
  end)

  ws:addEventListener("error", function(err)
    print("[Client] Error:", err)
  end)

  ws:connect("ws://127.0.0.1:8765")
end, 500) 