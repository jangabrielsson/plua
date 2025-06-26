-- Simple MQTT test
require('fibaro')
net = require('plua.net')

print("=== Simple MQTT Test ===")

-- Create MQTT client
local mqtt = net.MQTTClient()

-- Set up basic event listeners
mqtt:addEventListener('connected', function(event)
    print("✓ Connected to MQTT broker!")
    print("  Return code:", event.returnCode)
    
    -- Subscribe to a test topic
    local packet_id = mqtt:subscribe("test/plua", { qos = net.QoS.AT_MOST_ONCE })
    print("✓ Subscribed with packet ID:", packet_id)
end)

mqtt:addEventListener('subscribed', function(event)
    print("✓ Subscription confirmed, packet ID:", event.packetId)
    
    -- Publish a test message
    local packet_id = mqtt:publish("test/plua", "Hello from PLua!", { 
        qos = net.QoS.AT_MOST_ONCE,
        retain = false
    })
    print("✓ Published message with packet ID:", packet_id)
end)

mqtt:addEventListener('published', function(event)
    print("✓ Publish confirmed, packet ID:", event.packetId)
    
    -- Disconnect after successful publish
    setTimeout(function()
        print("✓ Disconnecting...")
        mqtt:disconnect()
    end, 1000)
end)

mqtt:addEventListener('disconnected', function(event)
    print("✓ Disconnected from MQTT broker")
    print("✓ MQTT test completed successfully!")
end)

mqtt:addEventListener('error', function(event)
    print("✗ MQTT error:", event.message)
end)

-- Connect to test broker
print("Connecting to test.mosquitto.org...")
mqtt:connect("mqtt://test.mosquitto.org", {
    clientId = "plua_test_" .. os.time(),
    keepAlivePeriod = 30,
    cleanSession = true
})

-- Timeout after 10 seconds
setTimeout(function()
    print("✗ Test timeout reached")
    mqtt:disconnect()
end, 10000) 