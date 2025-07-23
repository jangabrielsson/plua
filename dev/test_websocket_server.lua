--
-- WebSocket Server Test
-- Tests the WebSocket server implementation
--

print("=== WebSocket Server Test ===")

-- Create echo server
local echoServer = net.WebSocketEchoServer("localhost", 8890, true)

-- Wait a moment for server to start
setTimeout(function()
    print("Testing WebSocket server with client...")
    
    -- Create client to test the server
    local client = net.WebSocketClient()
    
    client:addEventListener("connected", function()
        print("✓ Client connected to server")
        client:send("Hello Server!")
        client:send("JSON test: " .. json.encode({test = "data", number = 42}))
    end)
    
    client:addEventListener("dataReceived", function(data)
        print("✓ Client received echo:", data)
    end)
    
    client:addEventListener("error", function(error)
        print("✗ Client error:", error)
    end)
    
    -- Connect to our echo server
    client:connect("ws://localhost:8890")
    
    -- Close client after testing
    setTimeout(function()
        print("Closing client connection...")
        client:close()
    end, 3000)
    
end, 1000)

-- Stop server after test
setTimeout(function()
    print("Stopping echo server...")
    echoServer:stop()
    print("Server running:", echoServer:isRunning())
end, 5000)

print("WebSocket server test started - will run for 6 seconds")
