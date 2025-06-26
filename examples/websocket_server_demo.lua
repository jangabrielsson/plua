-- WebSocket Server and Client Demo
-- Demonstrates PLua Python WebSocket server extension and Lua client

local _PY = _PY or {}

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