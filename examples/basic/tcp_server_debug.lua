-- Debug TCP Server Test
print("Starting Debug TCP Server Test...")

-- Create TCP server
local server_id = _PY.tcp_server_create()
print("Created TCP server with ID:", server_id)

-- Track events
local events = {}

-- Set up client connected callback
_PY.tcp_server_add_event_listener(server_id, "client_connected", function(client_id, addr)
    print("=== CLIENT CONNECTED ===")
    print("Client ID:", client_id)
    print("Address:", addr)
    table.insert(events, {type = "connected", client_id = client_id, addr = addr})
    
    -- Test if we can write to this client
    print("Testing write to client", client_id)
    _PY.tcp_write(client_id, "Hello from server!\n", function(success, result, message)
        print("Write result:", success, result, message)
        table.insert(events, {type = "write_result", success = success, result = result, message = message})
        
        -- After successful write, test reading
        if success then
            print("Testing read from client", client_id)
            _PY.tcp_read(client_id, 1024, function(success, data, message)
                print("Read result:", success, data, message)
                table.insert(events, {type = "read_result", success = success, data = data, message = message})
                
                if success and data then
                    print("Received data:", data)
                    -- Echo back
                    _PY.tcp_write(client_id, "Echo: " .. data, function(success, result, message)
                        print("Echo write result:", success, result, message)
                        table.insert(events, {type = "echo_write", success = success, result = result, message = message})
                    end)
                end
            end)
        end
    end)
end)

-- Set up client disconnected callback
_PY.tcp_server_add_event_listener(server_id, "client_disconnected", function(client_id, addr)
    print("=== CLIENT DISCONNECTED ===")
    print("Client ID:", client_id)
    print("Address:", addr)
    table.insert(events, {type = "disconnected", client_id = client_id, addr = addr})
end)

-- Set up error callback
_PY.tcp_server_add_event_listener(server_id, "error", function(err)
    print("=== SERVER ERROR ===")
    print("Error:", err)
    table.insert(events, {type = "error", error = err})
end)

-- Start the server
_PY.tcp_server_start(server_id, "127.0.0.1", 8767)
print("Server started on 127.0.0.1:8767")

-- Keep the script running for 30 seconds
print("Server will run for 30 seconds...")
print("Connect with: telnet 127.0.0.1 8767")
print("Then type a message and press Enter")

for i = 1, 30 do
    _PY.sleep(1)
    print("Server running...", i, "seconds")
    
    -- Print event summary every 5 seconds
    if i % 5 == 0 then
        print("Event summary:")
        for j, event in ipairs(events) do
            print("  ", j, event.type, event.client_id or event.success or event.error or "")
        end
    end
end

print("Server test completed.")
print("Final event count:", #events)

-- Close the server to allow clean termination
print("Closing TCP server...")
_PY.tcp_server_close(server_id)
print("TCP server closed. Script terminating.") 