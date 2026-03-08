-- Test MQTT client with TLS certificate verification options
-- This demonstrates how to connect to MQTT brokers with self-signed certificates

-- Example 1: Using allowUnauthorized=true (Fibaro HC3 style)
local options1 = {
    tls = {
        allowUnauthorized = true  -- Allow self-signed certificates
    }
}

-- Example 2: Using rejectUnauthorized=false (Alternative Fibaro HC3 style)
local options2 = {
    tls = {
        rejectUnauthorized = false  -- Don't reject unauthorized certificates
    }
}

-- Example 3: Default behavior (verify certificates)
local options3 = {}

-- Example 4: Explicitly require certificate verification
local options4 = {
    tls = {
        rejectUnauthorized = true  -- Default: verify certificates
    }
}

print("MQTT TLS Options Test")
print("====================")
print()
print("Option 1 (allowUnauthorized=true):")
print("  - Disables certificate verification")
print("  - Use for self-signed certificates")
print()
print("Option 2 (rejectUnauthorized=false):")
print("  - Same as option 1, alternative syntax")
print("  - Use for self-signed certificates")
print()
print("Option 3 (default):")
print("  - Verifies certificates")
print("  - Secure default behavior")
print()
print("Option 4 (rejectUnauthorized=true):")
print("  - Explicitly verifies certificates")
print()

-- Example connection to MQTT broker with self-signed certificate:
-- local client = mqtt.Client.connect("mqtts://192.168.1.100:8883", {
--     tls = {allowUnauthorized = true}
-- })
--
-- client:on("connected", function(event)
--     print("Connected to MQTT broker")
-- end)
--
-- client:on("error", function(event)
--     print("Error: " .. event.error)
-- end)

print("Test completed - options defined successfully")
