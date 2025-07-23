--
-- Simple WebSocket test to debug message receiving
--

print("=== Simple WebSocket Test ===")

local ws = net.WebSocketClient()

ws:addEventListener("connected", function()
    print("Connected! Sending 'Hello World'")
    ws:send("Hello World")
end)

ws:addEventListener("dataReceived", function(data)
    print("*** RECEIVED:", data)
end)

ws:addEventListener("error", function(error)
    print("ERROR:", error)
end)

ws:addEventListener("disconnected", function()
    print("Disconnected")
end)

ws:connect("wss://echo.websocket.org")

-- Close after 3 seconds
setTimeout(function()
    print("Closing...")
    ws:close()
end, 3000)

print("Waiting for echo...")
