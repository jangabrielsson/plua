-- Test TCP Server Client Disconnect Event
print("Starting TCP Server Client Disconnect Test...")

-- Create TCP server
local server_id = _PY.tcp_server_create()
print("Created TCP server with ID:", server_id)

-- Track events
local events = {}
local client_connected = false
local client_disconnected = false

-- Set up client connected callback
_PY.tcp_server_add_event_listener(server_id, "client_connected", function(client_id, addr)
    print("=== CLIENT CONNECTED ===")
    print("Client ID:", client_id)
    print("Address:", addr)
    client_connected = true
    table.insert(events, {type = "connected", client_id = client_id, addr = addr})
    
    -- Send a message to the client
    _PY.tcp_write(client_id, "Hello from server!\n", function(success, result, message)
        print("Write result:", success, result, message)
        if success then
            print("Message sent to client, waiting for client to disconnect...")
        end
    end)
end)

-- Set up client disconnected callback
_PY.tcp_server_add_event_listener(server_id, "client_disconnected", function(client_id, addr)
    print("=== CLIENT DISCONNECTED ===")
    print("Client ID:", client_id)
    print("Address:", addr)
    client_disconnected = true
    table.insert(events, {type = "disconnected", client_id = client_id, addr = addr})
end)

-- Set up error callback
_PY.tcp_server_add_event_listener(server_id, "error", function(err)
    print("=== SERVER ERROR ===")
    print("Error:", err)
    table.insert(events, {type = "error", error = err})
end)

-- Start the server
_PY.tcp_server_start(server_id, "127.0.0.1", 8769)
print("Server started on 127.0.0.1:8769")
print("Connect with: telnet 127.0.0.1 8769")
print("Then close the telnet connection to test disconnect event")

-- Keep the script running for 60 seconds
print("Server will run for 60 seconds...")

for i = 1, 60 do
    _PY.sleep(1)
    
    -- Print status every 10 seconds
    if i % 10 == 0 then
        print("Server running...", i, "seconds")
        print("Events so far:", #events)
        for j, event in ipairs(events) do
            print("  ", j, event.type, event.client_id or event.error or "")
        end
    end
    
    -- Stop if we've seen both connect and disconnect
    if client_connected and client_disconnected then
        print("Both connect and disconnect events received! Test successful.")
        break
    end
end

print("Server test completed.")
print("Final event count:", #events)
print("Client connected:", client_connected)
print("Client disconnected:", client_disconnected)

-- Close the server
print("Closing TCP server...")
_PY.tcp_server_close(server_id)
print("TCP server closed. Script terminating.") 