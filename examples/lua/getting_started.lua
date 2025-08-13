-- EPLua Getting Started Guide
-- Your first steps with EPLua's user-friendly APIs

print("Welcome to EPLua!")
print("This guide shows you the main features available to end users.")

-- 1. Basic Timers
print("\n=== 1. Timers ===")
print("EPLua provides setTimeout and setInterval functions:")

setTimeout(function()
    print("  ✓ This runs after 1 second")
end, 1000)

setTimeout(function()
    print("  ✓ This runs after 2 seconds")
end, 2000)

local counter = 0
local id = setInterval(function()
    counter = counter + 1
    print("  ✓ Interval tick:", counter)
    if counter >= 3 then
        clearInterval(id)
        print("  ✓ Interval cleared")
    end
end, 800)

-- 2. HTTP Requests
setTimeout(function()
    print("\n=== 2. HTTP Requests ===")
    print("Use net.HTTPClient() for web requests:")
    
    local client = net.HTTPClient()
    client:request("https://httpbin.org/json", {
        options = { method = "GET" },
        success = function(response)
            print("  ✓ HTTP request successful!")
            print("    Status:", response.status)
            print("    Response length:", string.len(response.data))
        end,
        error = function(error)
            print("  ❌ HTTP request failed:", error)
        end
    })
end, 3000)

-- 3. Real-time Communication
setTimeout(function()
    print("\n=== 3. WebSocket Communication ===")
    print("Use net.WebSocketClient() for real-time data:")
    
    local ws = net.WebSocketClient()
    
    ws:addEventListener("connected", function()
        print("  ✓ WebSocket connected to echo server")
        ws:send("Hello from EPLua!")
    end)
    
    ws:addEventListener("message", function(event)
        print("  ✓ Echo received:", event.data)
        ws:close()
    end)
    
    ws:addEventListener("disconnected", function()
        print("  ✓ WebSocket connection closed")
    end)
    
    ws:connect("wss://echo.websocket.org/")
end, 4000)

-- 4. IoT Communication
setTimeout(function()
    print("\n=== 4. MQTT for IoT ===")
    print("Use net.MQTTClient() for IoT messaging:")
    
    local mqtt = net.MQTTClient()
    
    mqtt:addEventListener("connected", function()
        print("  ✓ MQTT connected to public broker")
        mqtt:subscribe("eplua/getting-started")
        mqtt:publish("eplua/getting-started", "Hello IoT world!")
    end)
    
    mqtt:addEventListener("message", function(event)
        print("  ✓ MQTT message:", event.payload)
        mqtt:disconnect()
    end)
    
    mqtt:connect("mqtt://broker.emqx.io")
end, 5000)

-- 5. TCP/UDP Sockets
setTimeout(function()
    print("\n=== 5. Low-level Networking ===")
    print("Use net.TCPSocket() and net.UDPSocket() for custom protocols")
    print("  - TCP for reliable, ordered data")
    print("  - UDP for fast, lightweight messaging")
    print("\nSee network_demo.lua for detailed examples!")
end, 6000)

-- Completion message
setTimeout(function()
    print("\n🎉 Getting Started Guide Complete!")
    print("\nNext steps:")
    print("  - Try network_demo.lua for more network examples")
    print("  - Check the examples/lua/ directory for more samples")
    print("  - Visit the documentation for advanced features")
    os.exit()
end, 8000)
