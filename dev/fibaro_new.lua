-- Fibaro HC3 API support for plua2
-- This file sets up the main_file_hook and fibaro_api_hook

print("Loading Fibaro support...")

-- Set up main file hook for preprocessing Fibaro scripts
function _PY.main_file_hook(filename)
    print("Fibaro main_file_hook processing:", filename)
    
    -- Read the file content
    local file = io.open(filename, "r")
    if not file then
        error("Could not open file: " .. filename)
    end
    
    local content = file:read("*all")
    file:close()
    
    -- Simple preprocessing - could add Fibaro-specific transformations here
    print("Preprocessing Fibaro script (", #content, "bytes )")
    
    -- For now, just execute the content as-is
    -- In a real implementation, this could add Fibaro-specific globals,
    -- transform fibaro:* calls, inject debugging, etc.
    local processed_content = "-- Processed by Fibaro hook\n" .. content
    
    -- Execute the processed content
    local func, err = (loadstring or load)(processed_content, "@" .. filename)
    if func then
        coroutine.wrap(func)()
    else
        error("Failed to load processed script: " .. tostring(err))
    end
end

-- Mock Fibaro device and room data
local mock_devices = {
    {id = 1, name = "Living Room Light", type = "light", roomID = 1, value = "false"},
    {id = 2, name = "Kitchen Light", type = "light", roomID = 2, value = "true"},
    {id = 3, name = "Temperature Sensor", type = "temperature", roomID = 1, value = "22.5"}
}

local mock_rooms = {
    {id = 1, name = "Living Room"},
    {id = 2, name = "Kitchen"},
    {id = 3, name = "Bedroom"}
}

local mock_sections = {
    {id = 1, name = "Ground Floor"},
    {id = 2, name = "Upper Floor"}
}

local mock_variables = {
    weather = "sunny",
    temperature = "22",
    last_motion = "2025-01-18 10:30:00"
}

-- Set up Fibaro API hook
function _PY.fibaro_api_hook(method, path, data)
    print(string.format("Fibaro API: %s %s", method, path))
    if data and next(data) then
        print("  Data:", json.encode(data))
    end
    
    -- Parse the path and handle different endpoints
    if path == "/devices" and method == "GET" then
        return mock_devices, 200
        
    elseif path:match("^/devices/(%d+)$") and method == "GET" then
        local device_id = tonumber(path:match("^/devices/(%d+)$"))
        for _, device in ipairs(mock_devices) do
            if device.id == device_id then
                return device, 200
            end
        end
        return {error = "Device not found"}, 404
        
    elseif path:match("^/devices/(%d+)/action/") and method == "POST" then
        local device_id = tonumber(path:match("^/devices/(%d+)/action/"))
        local action = path:match("/action/(.+)$")
        
        -- Find device and simulate action
        for _, device in ipairs(mock_devices) do
            if device.id == device_id then
                print(string.format("Executing action '%s' on device %d (%s)", action, device_id, device.name))
                
                -- Simulate action effects
                if action == "turnOn" and device.type == "light" then
                    device.value = "true"
                elseif action == "turnOff" and device.type == "light" then
                    device.value = "false"
                end
                
                return {success = true, action = action, device = device}, 200
            end
        end
        return {error = "Device not found"}, 404
        
    elseif path == "/rooms" and method == "GET" then
        return mock_rooms, 200
        
    elseif path == "/sections" and method == "GET" then
        return mock_sections, 200
        
    elseif path == "/variables" and method == "GET" then
        return mock_variables, 200
        
    elseif path:match("^/variables/(.+)$") and method == "GET" then
        local var_name = path:match("^/variables/(.+)$")
        local value = mock_variables[var_name]
        if value then
            return {name = var_name, value = value}, 200
        else
            return {error = "Variable not found"}, 404
        end
        
    elseif path:match("^/variables/(.+)$") and method == "PUT" then
        local var_name = path:match("^/variables/(.+)$")
        if data and data.value then
            mock_variables[var_name] = data.value
            return {name = var_name, value = data.value}, 200
        else
            return {error = "Invalid request data"}, 400
        end
        
    else
        return {error = "Endpoint not implemented", method = method, path = path}, 501
    end
end

print("Fibaro hooks installed successfully!")
print("  - main_file_hook: Enabled for Fibaro script preprocessing")
print("  - fibaro_api_hook: Enabled for Fibaro API simulation")

-- Expose some Fibaro-like globals for scripts
fibaro = {
    call = function(deviceId, action)
        print(string.format("fibaro:call(%d, %s)", deviceId, action))
        return "OK"
    end,
    
    get = function(deviceId, property)
        print(string.format("fibaro:get(%d, %s)", deviceId, property))
        for _, device in ipairs(mock_devices) do
            if device.id == deviceId then
                return device[property] or device.value
            end
        end
        return nil
    end,
    
    setGlobalVariable = function(name, value)
        print(string.format("fibaro:setGlobalVariable(%s, %s)", name, value))
        mock_variables[name] = value
    end,
    
    getGlobalVariable = function(name)
        print(string.format("fibaro:getGlobalVariable(%s)", name))
        return mock_variables[name]
    end
}

return "Fibaro support loaded"
