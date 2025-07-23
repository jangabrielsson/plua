--
-- Comprehensive WebSocket Server Example
-- Shows all server features and API usage
--

print("=== WebSocket Server Example ===")

-- Create a custom WebSocket server
local server = net.WebSocketServer()

server:start("localhost", 8891, {
    started = function()
        print("✓ WebSocket server started on localhost:8891")
    end,
    
    connected = function(client_id)
        print("✓ Client", client_id, "connected")
        
        -- Send welcome message to new client
        server:send(client_id, "Welcome client " .. client_id .. "!")
        
        -- Show current client list
        local clients = server:getClients()
        print("  Total clients connected:", #clients)
    end,
    
    receive = function(client_id, message)
        print("✓ Received from client", client_id .. ":", message)
        
        -- Echo back with client ID
        server:send(client_id, "Server echo [" .. client_id .. "]: " .. message)
        
        -- Special commands
        if message:lower() == "ping" then
            server:send(client_id, "pong")
        elseif message:lower() == "time" then
            server:send(client_id, "Server time: " .. os.date())
        elseif message:lower() == "clients" then
            local clients = server:getClients()
            server:send(client_id, "Connected clients: " .. json.encode(clients))
        end
    end,
    
    disconnected = function(client_id)
        print("✓ Client", client_id, "disconnected")
        local clients = server:getClients()
        print("  Remaining clients:", #clients)
    end,
    
    error = function(error_msg)
        print("✗ Server error:", error_msg)
    end
})

-- Test with multiple clients
setTimeout(function()
    print("\n--- Testing with first client ---")
    
    local client1 = net.WebSocketClient()
    
    client1:addEventListener("connected", function()
        print("Client 1 connected")
        client1:send("Hello from client 1")
        client1:send("ping")
    end)
    
    client1:addEventListener("dataReceived", function(data)
        print("Client 1 received:", data)
    end)
    
    client1:connect("ws://localhost:8891")
    
    -- Add second client
    setTimeout(function()
        print("\n--- Adding second client ---")
        
        local client2 = net.WebSocketClient()
        
        client2:addEventListener("connected", function()
            print("Client 2 connected")
            client2:send("Hello from client 2")
            client2:send("time")
            client2:send("clients")
        end)
        
        client2:addEventListener("dataReceived", function(data)
            print("Client 2 received:", data)
        end)
        
        client2:connect("ws://localhost:8891")
        
        -- Close clients
        setTimeout(function()
            print("\n--- Closing clients ---")
            client1:close()
            client2:close()
        end, 2000)
        
    end, 1500)
    
end, 1000)

-- Stop server
setTimeout(function()
    print("\n--- Stopping server ---")
    print("Server running before stop:", server:isRunning())
    server:stop()
    print("Server running after stop:", server:isRunning())
end, 6000)

print("WebSocket server example will run for 7 seconds")
