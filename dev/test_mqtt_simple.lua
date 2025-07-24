--
-- Simple MQTT connection test
--

print("=== Simple MQTT Test ===")

-- Check if mqtt module is available
if mqtt then
    print("✓ mqtt module is available")
    print("  QoS constants:", mqtt.QoS.AT_MOST_ONCE, mqtt.QoS.AT_LEAST_ONCE, mqtt.QoS.EXACTLY_ONCE)
else
    print("✗ mqtt module not found")
end

-- Check if _PY functions are available
if _PY.mqtt_client_connect then
    print("✓ _PY.mqtt_client_connect is available")
else
    print("✗ _PY.mqtt_client_connect not found")
end

-- Try to connect
print("\nTrying to connect to test broker...")
local client = mqtt.Client.connect("mqtt://test.mosquitto.org", {
    clientId = "plua_simple_test",
    callback = function(returnCode)
        print("Connection callback received, return code:", returnCode)
    end
})

if client and client.client_id then
    print("✓ Client created with ID:", client.client_id)
else
    print("✗ Failed to create client")
end

setTimeout(function()
    print("Test completed")
end, 3000)
