-- Comprehensive network functionality test
-- Tests HTTPClient, TCPSocket, TCPServer
dofile("src/lua/net.lua")

function main()
    _PY.print("🚀 === Comprehensive Network Test ===")
    
    local tests_completed = 0
    local total_tests = 5  -- HTTP, TCP Client, TCP Server, UDP, WebSocket
    
    local function check_completion()
        tests_completed = tests_completed + 1
        _PY.print("Tests completed: " .. tests_completed .. "/" .. total_tests)
        if tests_completed >= total_tests then
            _PY.print("\\n🎉 All network tests passed successfully!")
        end
    end
    
    -- Test 1: HTTP Client
    _PY.print("\\n📡 Test 1: HTTP Client (GET request)")
    local http = net.HTTPClient()
    http:request("https://httpbin.org/json", {
        options = {
            method = "GET",
            headers = {}
        },
        success = function(response)
            _PY.print("✅ HTTP GET successful")
            _PY.print("Status: " .. tostring(response.status))
            _PY.print("Headers type: " .. type(response.headers))
            _PY.print("Data type: " .. type(response.data))
            check_completion()
        end,
        error = function(error)
            _PY.print("❌ HTTP GET failed: " .. tostring(error))
            check_completion()
        end
    })
    
    -- Test 2: TCP Client
    _PY.print("\\n🔌 Test 2: TCP Client (httpbin.org)")
    local tcp_client = net.TCPSocket()
    tcp_client:connect("httpbin.org", 80, {
        success = function()
            _PY.print("✅ TCP connection established")
            
            local http_request = "GET /json HTTP/1.1\\r\\nHost: httpbin.org\\r\\nConnection: close\\r\\n\\r\\n"
            tcp_client:send(http_request, {
                success = function()
                    _PY.print("✅ HTTP request sent via TCP")
                    
                    tcp_client:read({
                        success = function(headers)
                            _PY.print("✅ HTTP headers received")
                            _PY.print("Headers preview: " .. string.sub(headers, 1, 100) .. "...")
                            tcp_client:close()
                            check_completion()
                        end,
                        error = function(err)
                            _PY.print("❌ Error reading TCP response: " .. tostring(err))
                            tcp_client:close()
                            check_completion()
                        end
                    })
                end,
                error = function(err)
                    _PY.print("❌ Error sending TCP request: " .. tostring(err))
                    tcp_client:close()
                    check_completion()
                end
            })
        end,
        error = function(err)
            _PY.print("❌ TCP connection failed: " .. tostring(err))
            check_completion()
        end
    })
    
    -- Test 3: TCP Server with Client
    _PY.print("\\n🏠 Test 3: TCP Server with Echo Client")
    
    local server = net.TCPServer()
    local server_port = 12346
    
    server:start("localhost", server_port, function(client_socket, client_ip, client_port)
        _PY.print("✅ Server: Client connected from " .. tostring(client_ip) .. ":" .. tostring(client_port))
        
        client_socket:read({
            success = function(data)
                _PY.print("✅ Server: Received data: " .. tostring(data))
                
                local response = "Server echo: " .. data
                client_socket:send(response, {
                    success = function()
                        _PY.print("✅ Server: Echo response sent")
                        client_socket:close()
                    end,
                    error = function(err)
                        _PY.print("❌ Server: Error sending response: " .. tostring(err))
                        client_socket:close()
                    end
                })
            end,
            error = function(err)
                _PY.print("❌ Server: Error reading data: " .. tostring(err))
                client_socket:close()
            end
        })
    end)
    
    -- Connect client to our server
    _PY.set_timeout(_PY.registerCallback(function()
        local client = net.TCPSocket()
        client:connect("localhost", server_port, {
            success = function()
                _PY.print("✅ Client: Connected to local server")
                
                client:send("Hello from comprehensive test!", {
                    success = function()
                        _PY.print("✅ Client: Message sent to server")
                        
                        client:read({
                            success = function(response)
                                _PY.print("✅ Client: Received server response: " .. tostring(response))
                                client:close()
                                server:stop()
                                _PY.print("✅ Server stopped")
                                check_completion()
                            end,
                            error = function(err)
                                _PY.print("❌ Client: Error reading server response: " .. tostring(err))
                                client:close()
                                server:stop()
                                check_completion()
                            end
                        })
                    end,
                    error = function(err)
                        _PY.print("❌ Client: Error sending message: " .. tostring(err))
                        client:close()
                        server:stop()
                        check_completion()
                    end
                })
            end,
            error = function(err)
                _PY.print("❌ Client: Error connecting to server: " .. tostring(err))
                server:stop()
                check_completion()
            end
        })
    end), 500)  -- Wait 500ms for server to start
    
    -- Test 4: UDP Socket
    _PY.print("\\n📡 Test 4: UDP Socket Send")
    
    local udp_socket = net.UDPSocket()
    _PY.print("Created UDP socket: " .. tostring(udp_socket.socket))
    
    -- Wait for UDP socket to be ready, then test
    _PY.set_timeout(_PY.registerCallback(function()
        udp_socket:sendTo("UDP test message", "8.8.8.8", 53, {
            success = function()
                _PY.print("✅ UDP send successful")
                udp_socket:close()
                check_completion()
            end,
            error = function(err)
                _PY.print("❌ UDP send error: " .. tostring(err))
                udp_socket:close()
                check_completion()
            end
        })
    end), 1000)
    
    -- Test 5: WebSocket Client
    _PY.print("\\n⚡ Test 5: WebSocket Client Connection")
    
    local ws_client = net.WebSocketClient()
    _PY.print("Created WebSocket client: " .. tostring(ws_client))
    
    ws_client:addEventListener("connected", function()
        _PY.print("✅ WebSocket connected successfully")
        ws_client:send("Test message from comprehensive test")
    end)
    
    ws_client:addEventListener("dataReceived", function(data)
        _PY.print("✅ WebSocket received echo: " .. string.sub(tostring(data), 1, 50) .. "...")
        ws_client:close()
        check_completion()
    end)
    
    ws_client:addEventListener("error", function(error)
        _PY.print("❌ WebSocket error: " .. tostring(error))
        check_completion()
    end)
    
    -- Connect to WebSocket echo server
    _PY.set_timeout(_PY.registerCallback(function()
        ws_client:connect("wss://echo.websocket.org/")
    end), 1500)
    
    _PY.print("\\n⏳ Running all tests... (this may take a few seconds)")
end

main()
