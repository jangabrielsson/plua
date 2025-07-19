-- fibaro.lua - Test implementation of Fibaro API support using plua2 hooks

print("Loading Fibaro API support...")

-- Test main_file_hook functionality
print("Setting up custom Fibaro main_file_hook...")

-- Override the default hook with Fibaro preprocessing
function _PY.main_file_hook(filename)
    print("Fibaro main_file_hook called with: " .. filename)
    
    -- Read the file content
    local file = io.open(filename, "r")
    if not file then
        error("Cannot open file: " .. filename)
    end
    
    local content = file:read("*all")
    file:close()
    
    -- Preprocess the content (for Fibaro, we might add API imports, etc.)
    local preprocessed = [[
-- Fibaro API preprocessing applied
print("File preprocessed by Fibaro hook: ]] .. filename .. [[")
]] .. content
    
    -- Execute the preprocessed content
    local func, err = load(preprocessed, "@" .. filename)
    if func then
        coroutine.wrap(func)()
    else
        error("Failed to load preprocessed script: " .. tostring(err))
    end
end

print("Custom Fibaro main_file_hook installed successfully")

-- Test fibaro_api_hook functionality
print("Setting up Fibaro API hook...")

-- Set up the single Fibaro API handler function
_PY.fibaro_api_hook = function(method, path, path_params, query_params, body_data)
    print("Fibaro API hook called:")
    print("  Method: " .. method)
    print("  Path: " .. path)
    
    -- Simple Fibaro API simulation
    if path == "/api/devices" and method == "GET" then
        return {
            devices = {
                {id = 1, name = "Light 1", type = "binarySwitch", value = true},
                {id = 2, name = "Sensor 1", type = "sensor", value = 23.5},
                {id = 3, name = "Dimmer 1", type = "multilevelSwitch", value = 75}
            }
        }, 200
        
    elseif path == "/api/devices/{deviceID}" and method == "GET" then
        -- Extract device ID from path parameters
        local device_id = path_params and path_params.deviceID
        if device_id then
            device_id = tonumber(device_id)
            return {
                id = device_id,
                name = "Device " .. device_id,
                type = "binarySwitch", 
                value = device_id % 2 == 0
            }, 200
        else
            return {error = "Device ID not found"}, 400
        end
        
    elseif path == "/api/devices/{deviceID}" and method == "POST" then
        -- Extract device ID from path parameters
        local device_id = path_params and path_params.deviceID
        if device_id then
            device_id = tonumber(device_id)
            return {
                success = true,
                message = "Device " .. device_id .. " updated",
                device_id = device_id,
                new_value = body_data and body_data.value or "unknown"
            }, 200
        else
            return {error = "Device ID not found"}, 400
        end
        
    elseif path == "/api/categories" and method == "GET" then
        return {
            {id = 1, name = "Lighting", icon = "light"},
            {id = 2, name = "Security", icon = "shield"},
            {id = 3, name = "Climate", icon = "thermometer"},
            {id = 4, name = "Multimedia", icon = "speaker"}
        }, 200
        
    elseif path == "/api/rooms" and method == "GET" then
        return {
            {id = 1, name = "Living Room", sectionID = 1},
            {id = 2, name = "Kitchen", sectionID = 1},
            {id = 3, name = "Bedroom", sectionID = 2},
            {id = 4, name = "Bathroom", sectionID = 2}
        }, 200
        
    elseif path == "/api/sections" and method == "GET" then
        return {
            {id = 1, name = "Ground Floor"},
            {id = 2, name = "First Floor"},
            {id = 3, name = "Basement"}
        }, 200
        
    elseif path == "/api/info" and method == "GET" then
        -- Extract device ID from path parameters
        local device_id = path_params and path_params.deviceID
        if device_id then
            device_id = tonumber(device_id)
            return {
                success = true,
                message = "Device " .. device_id .. " updated",
                device_id = device_id,
                new_value = body_data and body_data.value or "unknown"
            }, 200
        else
            return {error = "Device ID not found"}, 400
        end
        
    elseif path == "/api/info" and method == "GET" then
        return {
            system = "Fibaro Home Center",
            version = "5.0.0",
            api_version = "1.0",
            status = "online",
            time = os.time()
        }, 200
        
    else
        return {
            error = "Not found",
            message = "Unknown Fibaro API endpoint: " .. method .. " " .. path
        }, 404
    end
end

print("Fibaro API hook installed successfully")
print("Available endpoints:")
print("  GET /api/devices - List all devices")
print("  GET /api/devices/{id} - Get specific device")
print("  POST /api/devices/{id} - Update device")
print("  GET /api/info - Get system info")

return "Fibaro API support loaded successfully"
