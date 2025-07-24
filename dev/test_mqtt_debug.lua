--
-- MQTT Debug Test
--

print("=== MQTT Debug Test ===")

-- Create client with debug
local client = mqtt.Client.connect("mqtt://test.mosquitto.org", {
    clientId = "plua_debug_test",
    keepAlivePeriod = 60,
    cleanSession = true,
    callback = function(returnCode)
        print("*** Connection callback received ***")
        print("Return code:", returnCode)
        if returnCode == 0 then
            print("✓ Connection successful!")
        else
            print("✗ Connection failed with code:", returnCode)
        end
    end
})

print("Client ID:", client.client_id)

-- Add event listeners
client:addEventListener('connected', function(event)
    print("*** Connected event ***")
    print("Session present:", event.sessionPresent)
    print("Return code:", event.returnCode)
end)

client:addEventListener('closed', function(event)
    print("*** Connection closed ***")
end)

client:addEventListener('error', function(event)
    print("*** Error event ***")
    print("Error code:", event.code)
end)

-- Check status periodically
setTimeout(function()
    print("Status check 1 - Connected:", client:isConnected())
end, 1000)

setTimeout(function()
    print("Status check 2 - Connected:", client:isConnected())
end, 3000)

setTimeout(function()
    print("Status check 3 - Connected:", client:isConnected())
    print("Final test completed")
end, 5000)
