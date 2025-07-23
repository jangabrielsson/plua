--
-- Test WebSocket client implementation
-- Tests both ws:// and wss:// connections following Fibaro API
--

print("=== WebSocket Client Test ===")

-- Test with WebSocket echo server (wss for secure connection)
local echo_url = "wss://echo.websocket.org"
print("Testing WebSocket connection to: " .. echo_url)

-- Create WebSocket client
local ws = net.WebSocketClient()

-- Set up event handlers
ws:addEventListener("connected", function()
    print("✓ WebSocket connected successfully")
    
    -- Send a test message
    print("Sending test message...")
    ws:send("Hello from plua2 WebSocket client!")
    
    -- Send JSON message
    local json_msg = json.encode({
        type = "test",
        message = "JSON test from plua2",
        timestamp = os.time()
    })
    ws:send(json_msg)
end)

ws:addEventListener("disconnected", function()
    print("✓ WebSocket disconnected")
end)

ws:addEventListener("error", function(error)
    print("✗ WebSocket error: " .. tostring(error))
end)

ws:addEventListener("dataReceived", function(data)
    print("✓ Received data: " .. tostring(data))
    
    -- Try to parse as JSON
    local success, parsed = pcall(json.decode, data)
    if success then
        print("  Parsed JSON:", json.encode(parsed))
    else
        print("  Plain text message")
    end
    
    -- Keep track of messages received
    received_count = (received_count or 0) + 1
    print("  Total messages received:", received_count)
end)

-- Test connection status before connecting
print("isOpen before connect:", ws:isOpen())

-- Connect to the WebSocket server
ws:connect(echo_url)

-- Test connection status after connect (should still be false until connected event)
print("isOpen after connect call:", ws:isOpen())

-- Schedule some actions after connection
setTimeout(function()
    print("Connection status after 2 seconds:", ws:isOpen())
    
    if ws:isOpen() then
        print("Sending delayed message...")
        ws:send("Delayed message after 2 seconds")
    end
end, 2000)

-- Schedule close after 5 seconds
setTimeout(function()
    print("Closing WebSocket connection...")
    ws:close()
end, 5000)

-- Test WebSocketClientTls (should be identical)
setTimeout(function()
    print("\n=== Testing WebSocketClientTls ===")
    local wss = net.WebSocketClientTls()
    
    wss:addEventListener("connected", function()
        print("✓ WebSocketClientTls connected")
        wss:send("Hello from WebSocketClientTls!")
        
        -- Close after sending
        setTimeout(function()
            wss:close()
        end, 1000)
    end)
    
    wss:addEventListener("dataReceived", function(data)
        print("✓ WebSocketClientTls received: " .. tostring(data))
    end)
    
    wss:addEventListener("disconnected", function()
        print("✓ WebSocketClientTls disconnected")
    end)
    
    wss:connect(echo_url)
end, 6000)

print("WebSocket test started. Waiting for events...")
print("Note: This test will run for about 8 seconds")
