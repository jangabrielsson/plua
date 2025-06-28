-- MQTT Client Demo
-- Demonstrates MQTT client functionality with event handling
require('fibaro')
net = require('plua.net')

print("=== MQTT Client Demo ===")

-- Create MQTT client
local mqtt = net.MQTTClient()

-- Set up event listeners
mqtt:addEventListener('connected', function(event)
    print("Connected to MQTT broker!")
    print("  Session present:", event.sessionPresent)
    print("  Return code:", event.returnCode)
    
    -- Subscribe to a topic after connection
    local packet_id = mqtt:subscribe("test/topic", { qos = net.QoS.AT_LEAST_ONCE })
    print("Subscribed to test/topic with packet ID:", packet_id)
end)

mqtt:addEventListener('disconnected', function(event)
    print("Disconnected from MQTT broker")
end)

mqtt:addEventListener('message', function(event)
    print("Received message:")
    print("  Topic:", event.topic)
    print("  Payload:", event.payload)
    print("  QoS:", event.qos)
    print("  Retain:", event.retain)
end)

mqtt:addEventListener('subscribed', function(event)
    print("Subscription confirmed:")
    print("  Packet ID:", event.packetId)
    print("  Results:", table.concat(event.results, ", "))
    
    -- Publish a test message after subscription
    local packet_id = mqtt:publish("test/topic", "Hello from PLua MQTT client!", { 
        qos = net.QoS.AT_LEAST_ONCE,
        retain = false
    })
    print("Published message with packet ID:", packet_id)
end)

mqtt:addEventListener('unsubscribed', function(event)
    print("Unsubscription confirmed:")
    print("  Packet ID:", event.packetId)
end)

mqtt:addEventListener('published', function(event)
    print("Publish confirmed:")
    print("  Packet ID:", event.packetId)
    
    -- Wait a bit then disconnect
    setTimeout(function()
        print("Disconnecting from MQTT broker...")
        mqtt:disconnect()
    end, 2000)
end)

mqtt:addEventListener('error', function(event)
    print("MQTT error:")
    print("  Code:", event.code)
    print("  Message:", event.message)
end)

-- Connect to a public MQTT broker for testing
-- Using test.mosquitto.org (no authentication required)
print("Connecting to test.mosquitto.org...")
mqtt:connect("mqtt://test.mosquitto.org", {
    clientId = "plua_mqtt_demo_" .. os.time(),
    keepAlivePeriod = 60,
    cleanSession = true,
    callback = function(errorCode)
        if errorCode == 0 then
            print("Connection callback: Success")
        else
            print("Connection callback: Error code", errorCode)
        end
    end
})

print("MQTT demo started. Waiting for events...")
print("Press Ctrl+C to stop")

-- Keep the script running to receive events
setTimeout(function()
    print("Demo timeout reached. Disconnecting...")
    mqtt:disconnect()
end, 10000) 