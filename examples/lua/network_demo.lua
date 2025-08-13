-- EPLua Network Demo - User-Friendly API
-- Demonstrates the net.* modules for end users

print("=== EPLua Network Demo ===")

-- Test 1: HTTP Client
print("\n1. HTTP Client Examples:")

local http = net.HTTPClient()

-- Simple GET request
http:request("https://api.github.com/", {
    options = { method = "GET" },
    success = function(response)
        print("  ✓ GitHub API Status:", response.status)
    end,
    error = function(error)
        print("  ❌ GitHub API Error:", error)
    end
})

-- POST request with data
http:request("https://httpbin.org/post", {
    options = { 
        method = "POST",
        headers = { ["Content-Type"] = "application/json" },
        data = '{"message": "Hello from EPLua!"}'
    },
    success = function(response)
        print("  ✓ POST request successful:", response.status)
    end,
    error = function(error)
        print("  ❌ POST request failed:", error)
    end
})

-- Test 2: TCP Socket
print("\n2. TCP Socket Example:")

local tcp = net.TCPSocket()
tcp:addEventListener("connected", function(event)
    print("  ✓ TCP connected to", event.host)
    tcp:send("GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
end)

tcp:addEventListener("data", function(event)
    print("  ✓ TCP data received:", string.len(event.data), "bytes")
    tcp:close()
end)

tcp:addEventListener("disconnected", function(event)
    print("  ✓ TCP disconnected")
end)

tcp:addEventListener("error", function(event)
    print("  ❌ TCP error:", event.error)
end)

tcp:connect("example.com", 80)

-- Test 3: UDP Socket
print("\n3. UDP Socket Example:")

local udp = net.UDPSocket()
udp:addEventListener("message", function(event)
    print("  ✓ UDP message from", event.host .. ":" .. event.port)
    print("    Data:", event.data)
    udp:close()
end)

udp:addEventListener("error", function(event)
    print("  ❌ UDP error:", event.error)
end)

udp:bind(0) -- Bind to any available port
udp:send("Hello UDP!", "8.8.8.8", 53) -- Send to Google DNS

-- Test 4: MQTT Client
print("\n4. MQTT Client Example:")

local mqtt = net.MQTTClient()
mqtt:addEventListener("connected", function(event)
    print("  ✓ MQTT connected")
    mqtt:subscribe("eplua/test/demo")
    mqtt:publish("eplua/test/demo", "Hello from EPLua MQTT!")
end)

mqtt:addEventListener("message", function(event)
    print("  ✓ MQTT message on", event.topic .. ":", event.payload)
    mqtt:disconnect()
end)

mqtt:addEventListener("disconnected", function(event)
    print("  ✓ MQTT disconnected")
end)

mqtt:addEventListener("error", function(event)
    print("  ❌ MQTT error:", event.error)
end)

mqtt:connect("mqtt://broker.emqx.io", {
    clientId = "eplua_demo_" .. math.random(1000, 9999)
})

-- Keep the script running
setTimeout(function()
    print("\n=== Network Demo completed ===")
end, 10000)
