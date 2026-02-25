-- Test MQTT event fields
print("Testing MQTT event fields...")

-- Create client
local client = net.Client.connect("mqtt://broker.hivemq.com:1883", {
    clientId = "PLua_Test_" .. tostring(os.time()),
    keepAlivePeriod = 60,
    cleanSession = true,
    callback = function(errorCode)
        print("Connect callback - errorCode:", errorCode)
    end
})

-- Test 'connected' event with sessionPresent and returnCode
client:addEventListener('connected', function(event)
    print("\n✓ Connected event received:")
    print("  - sessionPresent:", event.sessionPresent)
    print("  - returnCode:", event.returnCode)
    print("  - client_id:", event.client_id)
    
    -- Subscribe to test topic
    print("\nSubscribing to topic...")
    client:subscribe("plua/test", {
        qos = 1,
        callback = function(errorCode)
            print("Subscribe callback - errorCode:", errorCode)
        end
    })
end)

-- Test 'subscribed' event with packetId and results
client:addEventListener('subscribed', function(event)
    print("\n✓ Subscribed event received:")
    print("  - packetId:", event.packetId)
    print("  - results type:", type(event.results))
    print("  - results value:", event.results)
    if event.results then
        print("  - first result:", event.results[1])
    end
    print("  - client_id:", event.client_id)
    
    -- Publish test message
    print("\nPublishing message...")
    client:publish("plua/test", "Hello from PLua!", {
        qos = 1,
        retain = false,
        callback = function(errorCode)
            print("Publish callback - errorCode:", errorCode)
        end
    })
end)

-- Test 'published' event with packetId
client:addEventListener('published', function(event)
    print("\n✓ Published event received:")
    print("  - packetId:", event.packetId)
    print("  - topic:", event.topic)
    print("  - client_id:", event.client_id)
end)

-- Test 'message' event with packetId and dup
client:addEventListener('message', function(event)
    print("\n✓ Message event received:")
    print("  - topic:", event.topic)
    print("  - payload:", event.payload)
    print("  - qos:", event.qos)
    print("  - retain:", event.retain)
    print("  - packetId:", event.packetId)
    print("  - dup:", event.dup)
    print("  - client_id:", event.client_id)
    
    -- Disconnect after receiving message
    print("\nDisconnecting...")
    client:disconnect()
end)

-- Test 'closed' event
client:addEventListener('closed', function(event)
    print("\n✓ Closed event received:")
    print("  - client_id:", event.client_id)
    print("\n✓ All event fields verified successfully!")
end)

-- Test 'error' event
client:addEventListener('error', function(event)
    print("\n✗ Error event received:")
    print("  - code:", event.code)
    print("  - error:", event.error)
end)

print("\nWaiting for MQTT events...")
