--[[
%% properties
%% events
%% globals
--]]

--%%u:{label="status",text="Device Monitor - Starting..."}
--%%u:{{button="startBtn",text="Start Monitor",onReleased="startMonitoring"},{button="stopBtn",text="Stop Monitor",onReleased="stopMonitoring"}}
--%%u:{{button="statusBtn",text="Show Status",onReleased="showStatus"},{button="clearBtn",text="Clear Events",onReleased="clearEvents"}}
--%%u:{label="stats",text="No events yet"}

-- Device Change Monitor QuickApp
-- Uses the new refresh states polling and event queue functions

local QuickApp = QuickApp or {}
QuickApp.__index = QuickApp

function QuickApp:new(o)
    o = o or {}
    setmetatable(o, self)
    return o
end

function QuickApp:onInit()
    self.name = "Device Monitor"
    self.version = "1.0"
    
    self.monitoring = false
    self.eventQueue = "device_monitor"
    self.pollInterval = 3.0  -- 3 seconds
    self.totalEvents = 0
    self.deviceStates = {}
    
    -- Initialize event queue
    _PY.create_event_queue(self.eventQueue)
    
    -- Setup event processor timer
    self:setupEventProcessor()
    
    self:updateView("status", "text", "Device Monitor - Ready")
    self:log("Device Monitor QuickApp initialized")
end

function QuickApp:setupEventProcessor()
    -- Process events every 2 seconds
    setTimeout(function()
        self:processEvents()
        self:setupEventProcessor()  -- Reschedule
    end, 2000)
end

function QuickApp:processEvents()
    if not self.monitoring then return end
    
    local events = _PY.get_events_from_queue(self.eventQueue, 20)
    
    if #events > 0 then
        self.totalEvents = self.totalEvents + #events
        
        for _, event in ipairs(events) do
            self:handleDeviceChange(event)
        end
        
        self:updateStats()
    end
end

function QuickApp:handleDeviceChange(event)
    local deviceId = event.deviceId
    local changeType = event.changeType
    local newValue = event.newState and event.newState.value
    
    self:log(string.format("Device %d changed (%s): %s", 
        deviceId, changeType, tostring(newValue)))
    
    -- Track device states
    self.deviceStates[deviceId] = {
        lastValue = newValue,
        lastChange = event.timestamp,
        changeCount = (self.deviceStates[deviceId] and self.deviceStates[deviceId].changeCount or 0) + 1
    }
    
    -- Handle specific device types or IDs
    self:handleSpecificDevice(deviceId, event)
end

function QuickApp:handleSpecificDevice(deviceId, event)
    -- Example: React to specific devices
    if deviceId == 123 then
        -- Motion sensor
        if event.newState and event.newState.value == "true" then
            self:log("Motion detected!")
        end
    elseif deviceId == 456 then
        -- Temperature sensor
        local temp = tonumber(event.newState and event.newState.value)
        if temp and temp > 25 then
            self:log("High temperature detected: " .. temp .. "°C")
        end
    end
end

function QuickApp:updateStats()
    local queueSize = _PY.get_queue_size(self.eventQueue)
    local activeDevices = 0
    for _ in pairs(self.deviceStates) do
        activeDevices = activeDevices + 1
    end
    
    local statsText = string.format(
        "Events: %d | Queue: %d | Devices: %d",
        self.totalEvents, queueSize, activeDevices
    )
    
    self:updateView("stats", "text", statsText)
end

-- Global callback for refresh states
function onRefreshStatesUpdate(refreshData)
    local qa = _G.quickApp
    if not qa or not qa.monitoring then return end
    
    if not refreshData or not refreshData.last then
        qa:log("Invalid refresh data received")
        return
    end
    
    -- Process device changes
    for deviceId, deviceData in pairs(refreshData.last) do
        local deviceIdNum = tonumber(deviceId)
        if deviceIdNum then
            local previousState = qa.deviceStates[deviceIdNum]
            local currentState = {
                value = deviceData.value,
                modified = deviceData.modified,
                dead = deviceData.dead
            }
            
            -- Check for changes
            if not previousState or 
               (previousState.lastValue ~= currentState.value) or
               (previousState.dead ~= currentState.dead) then
                
                local changeEvent = {
                    type = "device_change",
                    deviceId = deviceIdNum,
                    timestamp = _PY.get_time(),
                    oldState = previousState,
                    newState = currentState,
                    changeType = not previousState and "initial" or 
                               (previousState.lastValue ~= currentState.value and "value") or
                               (previousState.dead ~= currentState.dead and "availability") or
                               "unknown"
                }
                
                _PY.add_event_to_queue(qa.eventQueue, changeEvent)
            end
        end
    end
end

-- UI Button Callbacks
function startMonitoring()
    local qa = _G.quickApp
    if qa.monitoring then
        qa:log("Already monitoring")
        return
    end
    
    qa.monitoring = true
    qa:updateView("status", "text", "Device Monitor - Starting...")
    
    -- Start refresh states polling
    local hc3Ip = "192.168.1.100"  -- Configure your HC3 IP
    local url = string.format("http://%s/api/refreshStates", hc3Ip)
    
    local success = _PY.start_refresh_states_polling(url, qa.pollInterval)
    
    if success then
        qa:updateView("status", "text", "Device Monitor - Active")
        qa:log("Started monitoring device changes")
    else
        qa.monitoring = false
        qa:updateView("status", "text", "Device Monitor - Failed to start")
        qa:log("Failed to start monitoring")
    end
end

function stopMonitoring()
    local qa = _G.quickApp
    if not qa.monitoring then
        qa:log("Not currently monitoring")
        return
    end
    
    qa.monitoring = false
    _PY.stop_refresh_states_polling()
    
    qa:updateView("status", "text", "Device Monitor - Stopped")
    qa:log("Stopped monitoring device changes")
end

function showStatus()
    local qa = _G.quickApp
    local queueSize = _PY.get_queue_size(qa.eventQueue)
    local status = qa.monitoring and "Active" or "Stopped"
    
    qa:log(string.format("Status: %s | Queue: %d | Total Events: %d", 
        status, queueSize, qa.totalEvents))
    
    -- Show top 5 most active devices
    local deviceList = {}
    for deviceId, state in pairs(qa.deviceStates) do
        table.insert(deviceList, {id = deviceId, changes = state.changeCount})
    end
    
    table.sort(deviceList, function(a, b) return a.changes > b.changes end)
    
    qa:log("Most active devices:")
    for i = 1, math.min(5, #deviceList) do
        local device = deviceList[i]
        qa:log(string.format("  Device %d: %d changes", device.id, device.changes))
    end
end

function clearEvents()
    local qa = _G.quickApp
    _PY.clear_event_queue(qa.eventQueue)
    qa.totalEvents = 0
    qa.deviceStates = {}
    qa:updateStats()
    qa:log("Cleared all events and device states")
end

-- Utility functions
function QuickApp:log(message)
    print(string.format("[%s] %s", os.date("%H:%M:%S"), message))
end

function QuickApp:updateView(elementName, propertyName, value)
    -- Emulated updateView function
    if _PY and _PY.broadcast_view_update then
        _PY.broadcast_view_update(self.id or 5555, elementName, propertyName, value)
    end
end

-- Initialize QuickApp
_G.quickApp = QuickApp:new()
_G.quickApp:onInit()

print("🖥️  Device Monitor QuickApp loaded")
print("   Use the UI buttons to control monitoring")
print("   Configure HC3 IP address in startMonitoring() function")
