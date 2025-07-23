--
-- WebSocket Client Example - Following Fibaro HC3 API
-- Demonstrates net.WebSocketClient() and net.WebSocketClientTls()
--

print("=== Fibaro-Compatible WebSocket Example ===")

-- Example 1: Basic WebSocket client (following Fibaro documentation exactly)
local ws = net.WebSocketClient()

-- Add event listeners following Fibaro API
ws:addEventListener("connected", function()
    print("✓ WebSocket connected")
    
    -- Send some test messages
    ws:send("Hello from plua2!")
    ws:send('{"type": "message", "content": "JSON test"}')
end)

ws:addEventListener("dataReceived", function(data)
    print("✓ Received:", data)
    
    -- Try to parse JSON data
    local success, parsed = pcall(json.decode, data)
    if success then
        print("  JSON:", json.encode(parsed))
    end
end)

ws:addEventListener("error", function(error)
    print("✗ Error:", error)
end)

ws:addEventListener("disconnected", function()
    print("✓ Disconnected")
end)

-- Connect to echo server
ws:connect("wss://echo.websocket.org")

-- Check connection status
setTimeout(function()
    print("Connection open:", ws:isOpen())
    if ws:isOpen() then
        ws:send("Status check message")
    end
end, 1000)

-- Example 2: Secure WebSocket (WebSocketClientTls - identical API)
setTimeout(function()
    print("\n=== WebSocketClientTls Example ===")
    
    local wss = net.WebSocketClientTls()
    
    wss:addEventListener("connected", function()
        print("✓ Secure WebSocket connected")
        wss:send("Hello from secure connection!")
    end)
    
    wss:addEventListener("dataReceived", function(data)
        print("✓ Secure received:", data)
        -- Close after receiving response
        setTimeout(function() wss:close() end, 500)
    end)
    
    wss:connect("wss://echo.websocket.org")
end, 2000)

-- Close the first connection after 4 seconds
setTimeout(function()
    print("Closing first connection...")
    ws:close()
end, 4000)

print("WebSocket example started - will run for 5 seconds")
