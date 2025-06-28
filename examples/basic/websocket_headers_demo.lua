-- WebSocket Headers Demo
-- Demonstrates WebSocket client connection with custom headers

local _PY = _PY or {}

-- Create WebSocket server
local server_id = _PY.websocket_server_create()
print("[Server] Created server with id:", server_id)

-- Register server event listeners
_PY.websocket_server_add_event_listener(server_id, "client_connected", function(client)
  print("[Server] Client connected:", tostring(client))
  _PY.websocket_server_send(server_id, client, "Welcome client!")
end)

_PY.websocket_server_add_event_listener(server_id, "message", function(client, msg)
  print("[Server] Received from client:", msg)
  local reply = "Echo: " .. msg
  print("[Server] echo message:", reply)
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
  print("[Client] Connecting to ws://127.0.0.1:8765 with custom headers...")
  local ws = net.WebSocketClient()

  -- Example 1: Connect with API key header (as mentioned by user)
  local headers_with_api_key = {
    ["X-API-KEY"] = "IplpxPXbz4vkuwPzgZjVpsd78HbIV-XF"
  }
  print("[Client] Connecting with API key header...")
  ws:connect("ws://127.0.0.1:8765", headers_with_api_key)

  ws:addEventListener("connected", function()
    print("[Client] Connected with API key header!")
    ws:send("Hello from client with API key!")
  end)

  ws:addEventListener("dataReceived", function(data)
    print("[Client] Received from server:", data)
    if string.find(data, "^Echo:") then
      print("[Client] Received echo, closing connection...")
      ws:close()
      -- Stop server after short delay
      setTimeout(function()
        print("[Server] Closing server...")
        _PY.websocket_server_close(server_id)
      end, 1000)
    end
  end)

  ws:addEventListener("disconnected", function()
    print("[Client] Disconnected.")
  end)

  ws:addEventListener("error", function(err)
    print("[Client] Error:", err)
  end)
end, 500) 