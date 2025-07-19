-- Test TCP Server functionality
net = require("net")
print("=== TCP Server Test ===")

-- Test 1: Basic TCP Server and Client
print("\n1. Testing TCP Server with Client Connection")

local server = net.TCPServer()
local client = net.TCPSocket()
local server_port = 12345
local received_messages = {}
local client_connected = false

-- Server callback to handle client connections
local function handle_client(client_socket, client_ip, client_port)
    print(string.format("Client connected from %s:%d", client_ip, client_port))
    client_connected = true
    
    -- Read data from client
    client_socket:read({
        success = function(data)
            print("Server received from client: " .. data)
            table.insert(received_messages, data)
            
            -- Echo back to client
            local response = "Echo: " .. data
            client_socket:send(response, {
                success = function()
                    print("Server echoed back to client")
                end,
                error = function(err)
                    print("Failed to echo back to client: " .. err)
                end
            })
        end,
        error = function(err)
            print("Client disconnected: " .. err)
        end
    })
end

-- Start the server
print("Starting TCP server on port " .. server_port)
server:start("localhost", server_port, handle_client)

-- Give server time to start
setTimeout(function()
    print("\nConnecting client to server...")
    
    -- Connect client to server
    client:connect("localhost", server_port, {
        success = function()
            print("Client connected successfully")
            
            -- Send test message
            client:send("Hello from client!", {
                success = function()
                    print("Client sent message")
                    
                    -- Receive echo
                    client:read({
                        success = function(response)
                            print("Client received echo: " .. response)
                             -- Close client
                            client:close()
                            print("Client closed")
                            
                            -- Stop server
                            setTimeout(function()
                                server:stop()
                                print("Server stopped")
                                
                                -- Verify results
                                print("\n--- Test Results ---")
                                print("Client connected: " .. tostring(client_connected))
                                print("Messages received by server: " .. #received_messages)
                                if #received_messages > 0 then
                                    print("First message: " .. received_messages[1])
                                end
                                
                                -- Start next test
                                setTimeout(test_multiple_clients, 1000)
                            end, 500)
                        end,
                        error = function(err)
                            print("Client failed to receive echo: " .. err)
                        end
                    })
                end,
                error = function(err)
                    print("Client failed to send message: " .. err)
                end
            })
        end,
        error = function(err)
            print("Client failed to connect: " .. err)
        end
    })
end, 1000)

-- Test 2: Multiple Client Connections
function test_multiple_clients()
    print("\n\n2. Testing Multiple Client Connections")
    
    local server2 = net.TCPServer()
    local clients = {}
    local connections_count = 0
    local messages_received = {}
    
    -- Server callback for multiple clients
    local function handle_multiple_clients(client_socket, client_ip, client_port)
        connections_count = connections_count + 1
        local client_id = connections_count
        print(string.format("Client %d connected from %s:%d", client_id, client_ip, client_port))
        
        -- Store client info
        table.insert(clients, {
            socket = client_socket,
            id = client_id,
            ip = client_ip,
            port = client_port
        })
        
        -- Read from this client
        client_socket:read({
            success = function(data)
                local msg = string.format("Client %d said: %s", client_id, data)
                print("Server received: " .. msg)
                table.insert(messages_received, msg)
                
                -- Broadcast to all other clients
                for _, other_client in ipairs(clients) do
                    if other_client.id ~= client_id and other_client.socket then
                        other_client.socket:send("Broadcast: " .. msg, {
                            success = function()
                                -- Message sent successfully
                            end,
                            error = function(err)
                                print("Failed to broadcast to client " .. other_client.id .. ": " .. err)
                            end
                        })
                    end
                end
            end,
            error = function(err)
                print("Error reading from client " .. client_id .. ": " .. err)
            end
        })
    end
    
    -- Start server on different port
    local port2 = 12346
    print("Starting multi-client server on port " .. port2)
    server2:start("localhost", port2, handle_multiple_clients)
    
    -- Connect multiple clients
    setTimeout(function()
        local client1 = net.TCPSocket()
        local client2 = net.TCPSocket()
        local client3 = net.TCPSocket()
        
        print("\nConnecting multiple clients...")
        
        -- Connect client 1
        client1:connect("localhost", port2, {
            success = function()
                print("Client 1 connected")
                
                -- Connect client 2
                client2:connect("localhost", port2, {
                    success = function()
                        print("Client 2 connected")
                        
                        -- Connect client 3
                        client3:connect("localhost", port2, {
                            success = function()
                                print("Client 3 connected")
                                
                                -- Send messages from each client
                                setTimeout(function()
                                    client1:send("Hello from client 1", {})
                                end, 200)
                                
                                setTimeout(function()
                                    client2:send("Greetings from client 2", {})
                                end, 400)
                                
                                setTimeout(function()
                                    client3:send("Hi from client 3", {})
                                end, 600)
                                
                                -- Clean up after a while
                                setTimeout(function()
                                    client1:close()
                                    client2:close()
                                    client3:close()
                                    server2:stop()
                                    
                                    print("\n--- Multiple Clients Test Results ---")
                                    print("Total connections: " .. connections_count)
                                    print("Messages received: " .. #messages_received)
                                    for i, msg in ipairs(messages_received) do
                                        print("  " .. i .. ": " .. msg)
                                    end
                                    
                                    -- Start final test
                                    setTimeout(test_error_handling, 1000)
                                end, 2000)
                            end,
                            error = function(err)
                                print("Client 3 failed to connect: " .. err)
                            end
                        })
                    end,
                    error = function(err)
                        print("Client 2 failed to connect: " .. err)
                    end
                })
            end,
            error = function(err)
                print("Client 1 failed to connect: " .. err)
            end
        })
    end, 1000)
end

-- Test 3: Error Handling
function test_error_handling()
    print("\n\n3. Testing Error Handling")
    
    -- Test starting server on already used port
    local server3 = net.TCPServer()
    local server4 = net.TCPServer()
    
    local port3 = 12347
    
    print("Starting first server on port " .. port3)
    server3:start("localhost", port3, function(client_socket, client_ip, client_port)
        print("Client connected to first server")
    end)
    
    -- Try to start another server on same port (should fail or handle gracefully)
    setTimeout(function()
        print("Attempting to start second server on same port...")
        server4:start("localhost", port3, function(client_socket, client_ip, client_port)
            print("Client connected to second server")
        end)
        
        -- Try connecting to invalid port
        setTimeout(function()
            print("Testing connection to invalid port...")
            local test_client = net.TCPSocket()
            test_client:connect("localhost", 99999, {
                success = function()
                    print("Unexpectedly connected to invalid port")
                end,
                error = function(err)
                    print("Expected failure connecting to invalid port: " .. err)
                end
            })
            
            -- Clean up
            setTimeout(function()
                server3:stop()
                server4:stop()
                
                print("\n--- Error Handling Test Complete ---")
                print("=== All TCP Server Tests Complete ===")
            end, 500)
        end, 1000)
    end, 1000)
end

print("TCP Server tests started...")
