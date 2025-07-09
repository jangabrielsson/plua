-- Test WebSocket server with new callback model
print("=== Testing WebSocket Server with New Callback Model ===")

-- Create WebSocket server
local server_id = _PY.websocket_server_create()
print("Created WebSocket server with ID:", server_id)

-- Add event listeners
_PY.websocket_server_add_event_listener(server_id, "client_connected", function(client)
  print("[CALLBACK] Client connected:", client)
end)

_PY.websocket_server_add_event_listener(server_id, "message", function(client, msg)
  print("[CALLBACK] Received message from client:", client, "Message:", msg)
  -- Echo back the message
  _PY.websocket_server_send(server_id, client, "Echo: " .. msg)
end)

_PY.websocket_server_add_event_listener(server_id, "client_disconnected", function(client)
  print("[CALLBACK] Client disconnected:", client)
end)

_PY.websocket_server_add_event_listener(server_id, "error", function(err)
  print("[CALLBACK] Server error:", err)
end)

-- Start the server
print("Starting WebSocket server on localhost:8769...")
_PY.websocket_server_start(server_id, "localhost", 8769)

-- Keep the server running for a while
print("Server started. Waiting for connections...")
print("You can test with: python -c \"import websocket; ws = websocket.create_connection('ws://localhost:8769'); ws.send('Hello'); print(ws.recv()); ws.close()\"")

-- Run for 10 seconds
_PY.sleep(10)

print("Shutting down server...")
_PY.websocket_server_close(server_id)
print("Test completed.") 