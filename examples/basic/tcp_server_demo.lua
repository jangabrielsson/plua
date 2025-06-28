-- TCP Server and Client Demo
-- Demonstrates PLua Python TCP server extension and Lua client with bidirectional communication

local _PY = _PY or {}
print("START")
-- Create TCP server
local server_id = _PY.tcp_server_create()
print("[Server] Created TCP server with id:", server_id)

-- Function to continuously read from a client and echo
local function _read_from_client(client_id)
  _PY.tcp_read(client_id, 1024, function(success, data, message)
    if success and data then
      print("[Server] Received from client", client_id, ":", data:gsub("\n", "\\n"))
      
      -- Echo the message back
      local reply = "Echo: " .. data
      print("[Server] Sending echo:", reply:gsub("\n", "\\n"))
      _PY.tcp_write(client_id, reply, function(write_success, write_result, write_message)
        if write_success then
          print("[Server] Echo sent to client", client_id)
        else
          print("[Server] Failed to send echo to client", client_id, ":", write_message)
        end
      end)
      
      -- Continue reading from this client
      _read_from_client(client_id)
    else
      if data == "" then
        print("[Server] Client", client_id, "disconnected (no data)")
      else
        print("[Server] Read error from client", client_id, ":", message)
      end
    end
  end)
end

-- Add event listeners for the server
_PY.tcp_server_add_event_listener(server_id, "client_connected", function(client_id, addr)
  print("[Server] Client connected:", client_id, "from", addr)
  
  -- Send welcome message to the client
  _PY.tcp_write(client_id, "Welcome to TCP server!\n", function(success, result, message)
    if success then
      print("[Server] Welcome message sent to client", client_id)
      -- Start reading from this client after sending welcome message
      _read_from_client(client_id)
    else
      print("[Server] Failed to send welcome message to client", client_id, ":", message)
    end
  end)
end)

_PY.tcp_server_add_event_listener(server_id, "client_disconnected", function(client_id, addr)
  print("[Server] Client disconnected:", client_id, "from", addr)
end)

_PY.tcp_server_add_event_listener(server_id, "error", function(error_msg)
  print("[Server] TCP Server error:", error_msg)
end)

-- Start the server on localhost:8766
_PY.tcp_server_start(server_id, "127.0.0.1", 8766)
print("[Server] TCP Server started on 127.0.0.1:8766")

-- Use setTimeout to ensure server is ready before connecting
setTimeout(function()
  -- Start the client using _PY.tcp_connect
  print("[Client] Connecting to TCP server...")
  _PY.tcp_connect("127.0.0.1", 8766, function(success, conn_id, message)
    if success then
      print("[Client] Connected to TCP server! Connection ID:", conn_id)
      
      -- Wait for server to process the connection and send welcome message
      -- Use yield_to_loop to allow server callbacks to execute
      --_PY.yield_to_loop()
      --_PY.yield_to_loop()  -- Give it a couple of chances
      
      -- Read the welcome message from server
      _PY.tcp_read(conn_id, 1024, function(read_success, data, read_message)
        if read_success and data then
          print("[Client] Received:", data:gsub("\n", "\\n"))
          
          -- Send a message to the server
          _PY.tcp_write(conn_id, "Hello from TCP client!\n", function(write_success, write_result, write_message)
            if write_success then
              print("[Client] Sent: Hello from TCP client!")
              
              -- Read the server's echo response
              _PY.tcp_read(conn_id, 1024, function(read_success2, data2, read_message2)
                if read_success2 and data2 then
                  print("[Client] Received echo:", data2:gsub("\n", "\\n"))
                  
                  -- Send another message
                  _PY.tcp_write(conn_id, "Second message from client!\n", function(write_success3, write_result3, write_message3)
                    if write_success3 then
                      print("[Client] Sent: Second message from client!")
                      
                      -- Read the second echo
                      _PY.tcp_read(conn_id, 1024, function(read_success4, data4, read_message4)
                        if read_success4 and data4 then
                          print("[Client] Received second echo:", data4:gsub("\n", "\\n"))
                          
                          -- Close the connection
                          _PY.tcp_close(conn_id, function(close_success, close_result, close_message)
                            if close_success then
                              print("[Client] Connection closed successfully")
                            else
                              print("[Client] Close error:", close_message)
                            end
                            
                            -- Close the server
                            _PY.tcp_server_close(server_id)
                            print("[Main] Demo completed.")
                          end)
                        else
                          print("[Client] Read error for second echo:", read_message4)
                        end
                      end)
                    else
                      print("[Client] Write error for second message:", write_message3)
                    end
                  end)
                else
                  print("[Client] Read error for echo:", read_message2)
                end
              end)
            else
              print("[Client] Write error:", write_message)
            end
          end)
        else
          print("[Client] Read error for welcome message:", read_message)
        end
      end)
    else
      print("[Client] Connect error:", message)
      -- Stop server on connection failure
      _PY.tcp_server_close(server_id)
    end
  end)
end, 1000)  -- 1 second delay

print("[Main] Demo completed.")
