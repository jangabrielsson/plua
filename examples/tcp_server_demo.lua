-- TCP Server and Client Demo
-- Demonstrates PLua Python TCP server extension and Lua client

local _PY = _PY or {}

-- Create TCP server
local server_id = _PY.tcp_server_create()
print("[Server] Created TCP server with id:", server_id)

-- Register server event listeners
_PY.tcp_server_add_event_listener(server_id, "client_connected", function(client_id, addr)
  print("[Server] Client connected:", client_id, "from", tostring(addr))
  -- Send welcome message
  _PY.tcp_server_send(server_id, client_id, "Welcome to TCP server!\n")
end)

_PY.tcp_server_add_event_listener(server_id, "data_received", function(client_id, data)
  print("[Server] Received from client", client_id, ":", data:gsub("\n", "\\n"))
  -- Echo the message back
  local reply = "Echo: " .. data
  print("[Server] Sending echo:", reply:gsub("\n", "\\n"))
  _PY.tcp_server_send(server_id, client_id, reply)
end)

_PY.tcp_server_add_event_listener(server_id, "client_disconnected", function(client_id, addr)
  print("[Server] Client disconnected:", client_id, "from", tostring(addr))
end)

_PY.tcp_server_add_event_listener(server_id, "error", function(err)
  print("[Server] Error:", err)
end)

-- Start the server on localhost:8766
_PY.tcp_server_start(server_id, "127.0.0.1", 8766)
print("[Server] TCP Server started on 127.0.0.1:8766")

-- Wait a moment for the server to start
setTimeout(function()
  -- Start the client
  print("[Client] Connecting to TCP server...")
  local tcp = net.TCPSocket()

  -- Connect to the server
  tcp:connect("127.0.0.1", 8766, {
    success = function()
      print("[Client] Connected to TCP server!")
      
      -- Send first message
      tcp:write("Hello from TCP client!", {
        success = function()
          print("[Client] Sent: Hello from TCP client!")
          
          -- Read response
          tcp:read({
            success = function(data)
              print("[Client] Received:", data:gsub("\n", "\\n"))
              
              -- Send second message
              tcp:write("Second message from client!", {
                success = function()
                  print("[Client] Sent: Second message from client!")
                  
                  -- Read second response
                  tcp:read({
                    success = function(data)
                      print("[Client] Received:", data:gsub("\n", "\\n"))
                      
                      -- Close connection after receiving echo
                      print("[Client] Closing connection...")
                      tcp:close()
                      
                      -- Stop server
                      print("[Server] Closing server...")
                      _PY.tcp_server_close(server_id)
                    end,
                    error = function(err)
                      print("[Client] Read error:", err)
                    end
                  })
                end,
                error = function(err)
                  print("[Client] Write error:", err)
                end
              })
            end,
            error = function(err)
              print("[Client] Read error:", err)
            end
          })
        end,
        error = function(err)
          print("[Client] Write error:", err)
        end
      })
    end,
    error = function(err)
      print("[Client] Connect error:", err)
    end
  })
end, 100)  -- Just 100ms for server to start 