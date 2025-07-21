-- Simple demo fibaro_api_hook that logs method and path
-- This demonstrates the simplified API approach

print("Setting up demo Fibaro API hook...")

_PY.fibaro_api_hook = function(method, path, data)
    print("=== FIBARO API HOOK ===")
    print("Method:", method)
    print("Path:", path)
    if data and data ~= "" then
        print("Data:", data)
    else
        print("Data: (empty)")
    end
    print("=======================")
    
    -- Return some demo data based on the path
    if path:match("^/api/devices$") then
        return {
            {id = 1, name = "Demo Light", type = "com.fibaro.binarySwitch", roomID = 1},
            {id = 2, name = "Demo Sensor", type = "com.fibaro.temperatureSensor", roomID = 2}
        }
    elseif path:match("^/api/devices/(%d+)$") then
        local deviceId = path:match("^/api/devices/(%d+)$")
        return {
            id = tonumber(deviceId),
            name = "Demo Device " .. deviceId,
            type = "com.fibaro.device",
            roomID = 1,
            properties = {
                value = "42",
                unit = "units"
            }
        }
    elseif path:match("^/api/rooms$") then
        return {
            {id = 1, name = "Living Room", icon = "room"},
            {id = 2, name = "Kitchen", icon = "room"}
        }
    elseif path:match("^/api/rooms/(%d+)$") then
        local roomId = path:match("^/api/rooms/(%d+)$")
        return {
            id = tonumber(roomId),
            name = "Demo Room " .. roomId,
            icon = "room"
        }
    else
        -- Default response for unhandled paths
        return {
            message = "Demo API response",
            method = method,
            path = path,
            status = "success"
        }
    end
end

print("Demo Fibaro API hook installed!")
print("Try making requests to /api/devices, /api/devices/123, /api/rooms, etc.")
