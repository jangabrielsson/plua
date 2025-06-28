-- Simple TCP Server Test
print("Starting TCP Server Test...")

-- Create TCP server
local server_id = _PY.tcp_server_create()
print("Created TCP server with ID:", server_id)

-- Track if client connected
local client_connected = false
local client_id = nil

-- Set up client connected callback
_PY.tcp_server_add_event_listener(server_id, "client_connected", function(cid, addr)
    print("=== CLIENT CONNECTED ===")
    print("Client ID:", cid)
    print("Address:", addr)
    client_connected = true
    client_id = cid
    
    -- Send welcome message
    _PY.tcp_write(cid, "Welcome to TCP server!\n", function(success, result, message)
        print("Write result:", success, result, message)
        
        if success then
            -- Read response
            _PY.tcp_read(cid, 1024, function(success, data, message)
                print("Read result:", success, data, message)
                
                if success and data then
                    print("Received:", data)
                    -- Echo back
                    _PY.tcp_write(cid, "Echo: " .. data, function(success, result, message)
                        print("Echo write result:", success, result, message)
                        
                        -- Close connection after echo
                        _PY.tcp_close(cid, function(success, message)
                            print("Close result:", success, message)
                        end)
                    end)
                end
            end)
        end
    end)
end)

-- Set up client disconnected callback
_PY.tcp_server_add_event_listener(server_id, "client_disconnected", function(cid, addr)
    print("=== CLIENT DISCONNECTED ===")
    print("Client ID:", cid)
    print("Address:", addr)
end)

-- Start the server
_PY.tcp_server_start(server_id, "127.0.0.1", 8768)
print("Server started on 127.0.0.1:8768")

-- Wait a moment for server to start
_PY.sleep(1)

-- Connect to the server using tcp_connect
print("Connecting to server...")
_PY.tcp_connect("127.0.0.1", 8768, function(success, conn_id, message)
    print("Connect result:", success, conn_id, message)
    
    if success then
        -- Send a message
        _PY.tcp_write(conn_id, "Hello from client!\n", function(success, result, message)
            print("Client write result:", success, result, message)
            
            if success then
                -- Read response
                _PY.tcp_read(conn_id, 1024, function(success, data, message)
                    print("Client read result:", success, data, message)
                    
                    if success and data then
                        print("Client received:", data)
                    end
                    
                    -- Close connection
                    _PY.tcp_close(conn_id, function(success, message)
                        print("Client close result:", success, message)
                        
                        -- Close server after a short delay
                        _PY.sleep(1)
                        print("Closing server...")
                        _PY.tcp_server_close(server_id)
                        print("Test completed.")
                    end)
                end)
            end
        end)
    else
        print("Failed to connect to server")
        _PY.tcp_server_close(server_id)
    end
end)

-- Keep running for a few seconds
for i = 1, 10 do
    _PY.sleep(1)
    print("Test running...", i, "seconds")
end

print("Test timeout reached. Closing server...")
_PY.tcp_server_close(server_id)
print("Test completed.") 