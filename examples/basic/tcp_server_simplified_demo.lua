-- Simplified TCP Server Demo
-- This demonstrates the new simplified TCP server API with only 2 callbacks:
-- - client_connected: Called when a client connects
-- - client_disconnected: Called when a client disconnects
-- Data handling is done with the existing tcp_read and tcp_write functions

print("Starting Simplified TCP Server Demo...")

-- Create TCP server
local server_id = _PY.tcp_server_create()
print("Created TCP server with ID:", server_id)

-- Set up client connected callback
_PY.tcp_server_add_event_listener(server_id, "client_connected", function(client_id, addr)
    print("Client connected:", client_id, "from", addr)
    
    -- Send welcome message using tcp_write
    _PY.tcp_write(client_id, "Welcome to simplified TCP server!\n", function(success, result, message)
        if success then
            print("Welcome message sent to client", client_id)
        else
            print("Failed to send welcome message to client", client_id, ":", message)
        end
    end)
    
    -- Start reading data from this client
    _read_from_client(client_id)
end)

-- Set up client disconnected callback
_PY.tcp_server_add_event_listener(server_id, "client_disconnected", function(client_id, addr)
    print("Client disconnected:", client_id, "from", addr)
end)

-- Set up error callback
_PY.tcp_server_add_event_listener(server_id, "error", function(err)
    print("Server error:", err)
end)

-- Function to continuously read from a client
function _read_from_client(client_id)
    _PY.tcp_read(client_id, 1024, function(success, data, message)
        if success and data then
            print("Received from client", client_id, ":", data:gsub("\n", "\\n"))
            
            -- Echo the message back
            local reply = "Echo: " .. data
            print("Sending echo:", reply:gsub("\n", "\\n"))
            _PY.tcp_write(client_id, reply, function(write_success, write_result, write_message)
                if write_success then
                    print("Echo sent to client", client_id)
                else
                    print("Failed to send echo to client", client_id, ":", write_message)
                end
            end)
            
            -- Continue reading
            _read_from_client(client_id)
        else
            if success then
                print("Client", client_id, "disconnected (no data)")
            else
                print("Read error from client", client_id, ":", message)
            end
        end
    end)
end

-- Start the server
_PY.tcp_server_start(server_id, "127.0.0.1", 8766)
print("Server started on 127.0.0.1:8766")
print("Server is running. Connect with: telnet 127.0.0.1 8766")
print("Press Ctrl+C to stop")

-- Keep the server running
while true do
    _PY.sleep(1)
end 