-- TCP Server and Async Client Demo
-- Demonstrates PLua Python TCP server extension with async TCP client

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
  print("[Client] Connecting to TCP server using async functions...")
  
  -- Connect using async TCP functions
  _PY.tcp_connect("127.0.0.1", 8766, function(success, conn_id, message)
    if success then
      print("[Client] Connected! Connection ID:", conn_id, "Message:", message)
      
      -- Send first message
      _PY.tcp_write(conn_id, "Hello from async TCP client!", function(success, bytes_written, message)
        if success then
          print("[Client] Sent:", bytes_written, "bytes. Message:", message)
          
          -- Read response
          _PY.tcp_read(conn_id, 1024, function(success, data, message)
            if success then
              print("[Client] Received:", data:gsub("\n", "\\n"), "Message:", message)
              
              -- Send second message
              setTimeout(function()
                _PY.tcp_write(conn_id, "Second message from async client!", function(success, bytes_written, message)
                  if success then
                    print("[Client] Sent second message:", bytes_written, "bytes. Message:", message)
                    
                    -- Read second response
                    _PY.tcp_read(conn_id, 1024, function(success, data, message)
                      if success then
                        print("[Client] Received second response:", data:gsub("\n", "\\n"), "Message:", message)
                        
                        -- Close connection after receiving echo
                        setTimeout(function()
                          print("[Client] Closing connection...")
                          _PY.tcp_close(conn_id, function(success, message)
                            if success then
                              print("[Client] Closed:", message)
                              
                              -- Stop server after short delay
                              setTimeout(function()
                                print("[Server] Closing server...")
                                _PY.tcp_server_close(server_id)
                              end, 500)
                            else
                              print("[Client] Close error:", message)
                            end
                          end)
                        end, 500)
                      else
                        print("[Client] Read error:", message)
                      end
                    end)
                  else
                    print("[Client] Write error:", message)
                  end
                end)
              end, 500)
            else
              print("[Client] Read error:", message)
            end
          end)
        else
          print("[Client] Write error:", message)
        end
      end)
    else
      print("[Client] Connect error:", message)
    end
  end)
end, 500) 