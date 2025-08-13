   -- EPLua Basic Example - User-Friendly API
-- This example shows how to use EPLua's high-level APIs
-- Uses setTimeout, setInterval, and net.* functions

print("=== EPLua Basic Example ===")
print("Using setTimeout, setInterval, and net.* APIs")

-- Test basic timers
print("\n1. Testing Timers:")

setTimeout(function()
    print("  ✓ Simple timeout after 1 second")
end, 1000)

setTimeout(function()
    print("  ✓ Another timeout after 2 seconds")
end, 2000)

-- Test interval
print("\n2. Testing Intervals:")
local count = 0
local intervalId = setInterval(function()
    count = count + 1
    print("  ✓ Interval tick:", count)
    
    if count >= 3 then
        print("  ✓ Clearing interval")
        clearInterval(intervalId)
    end
end, 1500)

-- Test HTTP client
print("\n3. Testing HTTP Client:")

local http = net.HTTPClient()
http:request("https://httpbin.org/get", {
    options = { 
        method = "GET",
        timeout = 10000 
    },
    success = function(response)
        print("  ✓ HTTP GET successful")
        print("    Status:", response.status)
        print("    Data length:", string.len(response.data))
    end,
    error = function(error)
        print("  ❌ HTTP GET failed:", error)
    end
})

-- Test WebSocket client
print("\n4. Testing WebSocket Client:")

local ws = net.WebSocketClient()
ws:addEventListener("connected", function(event)
    print("  ✓ WebSocket connected")
    ws:send("Hello WebSocket!")
end)

ws:addEventListener("message", function(event)
    print("  ✓ WebSocket message received:", event.data)
    ws:close()
end)

ws:addEventListener("disconnected", function(event)
    print("  ✓ WebSocket disconnected")
end)

ws:addEventListener("error", function(event)
    print("  ❌ WebSocket error:", event.error)
end)

-- Connect to a WebSocket echo server
ws:connect("wss://echo.websocket.org/")

-- Keep the script running for a while
setTimeout(function()
    print("\n=== Example completed ===")
    os.exit()
end, 8000)
