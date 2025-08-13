-- Example: Fibaro HC3 Refresh States Integration with Single Event Queue
-- This demonstrates how to use the new refresh states and event queue functions
-- in a real Fibaro QuickApp scenario

print("🔄 Fibaro Refresh States Integration Demo")
print("=========================================")

-- Configuration
local HC3_IP = "192.168.1.100"  -- Replace with your HC3 IP
local POLL_INTERVAL = 2.0        -- Poll every 2 seconds

-- Initialize the global event queue
local success = _PY.init_event_queue()
print("📦 Initialized global event queue:", success and "✅ Success" or "❌ Failed")

-- Track previous device states to detect changes
local previousStates = {}

-- Callback function that gets called when refresh states are received
function onRefreshStatesUpdate(refreshData)
    print("📡 Received refresh states update at", os.date("%H:%M:%S"))
    
    if not refreshData or not refreshData.last then
        print("⚠️  Invalid refresh data received")
        return
    end
    
    local changedDevices = 0
    
    -- Process each device in the refresh states
    for deviceId, deviceData in pairs(refreshData.last) do
        local deviceIdStr = tostring(deviceId)
        
        -- Check if this device state has changed
        local previousState = previousStates[deviceIdStr]
        local currentState = {
            value = deviceData.value,
            modified = deviceData.modified,
            dead = deviceData.dead
        }
        
        -- Detect changes
        if not previousState or 
           previousState.value ~= currentState.value or
           previousState.dead ~= currentState.dead then
            
            -- Create change event and add to global queue
            local changeEvent = {
                type = "device_change",
                source = "hc3_refresh",
                deviceId = tonumber(deviceId),
                timestamp = _PY.get_time(),
                oldState = previousState,
                newState = currentState,
                changeType = not previousState and "initial" or 
                           (previousState.value ~= currentState.value and "value") or
                           (previousState.dead ~= currentState.dead and "availability") or
                           "unknown"
            }
            
            -- Add to global event queue
            _PY.add_event(changeEvent)
            changedDevices = changedDevices + 1
            
            print(string.format("🔄 Device %s changed: %s -> %s (%s)", 
                deviceId, 
                previousState and tostring(previousState.value) or "nil",
                tostring(currentState.value),
                changeEvent.changeType
            ))
        end
        
        -- Update previous state
        previousStates[deviceIdStr] = currentState
    end
    
    if changedDevices > 0 then
        print(string.format("📊 Total changes detected: %d", changedDevices))
        print(string.format("📦 Queue size: %d events", _PY.get_event_count()))
    end
end

-- Function to process events from the global queue
function processDeviceChangeEvents()
    local events = _PY.get_events(10)
    
    if #events > 0 then
        print(string.format("⚡ Processing %d events:", #events))
        
        for i, event in ipairs(events) do
            print(string.format("  Event %d: %s from %s", 
                i, 
                event.type,
                event.source or "unknown"
            ))
            
            if event.type == "device_change" then
                print(string.format("    Device %d (%s): %s", 
                    event.deviceId, 
                    event.changeType,
                    event.newState and tostring(event.newState.value) or "unknown"
                ))
                
                -- Handle specific device changes
                if event.changeType == "value" and event.deviceId == 123 then
                    print("    💡 Light sensor changed - adjusting lighting")
                elseif event.changeType == "availability" then
                    print("    🔌 Device availability changed - checking network")
                end
            elseif event.type == "emulated_action" then
                print(string.format("    Emulated action: %s on device %d", 
                    event.action, event.deviceId))
            end
        end
    end
end

-- Function to add emulated events (for the emulator to use)
function addEmulatedEvent(deviceId, action, value)
    local event = {
        type = "emulated_action",
        source = "emulator",
        deviceId = deviceId,
        action = action,
        value = value,
        timestamp = _PY.get_time()
    }
    
    _PY.add_event(event)
    print(string.format("🎮 Added emulated event: %s on device %d", action, deviceId))
end

-- Demonstration functions
function startPolling()
    local url = string.format("http://%s/api/refreshStates", HC3_IP)
    print(string.format("🚀 Starting refresh states polling: %s", url))
    print(string.format("⏱️  Poll interval: %.1f seconds", POLL_INTERVAL))
    
    local success = _PY.start_refresh_states_polling(url, POLL_INTERVAL)
    if success then
        print("✅ Polling started successfully")
        return true
    else
        print("❌ Failed to start polling")
        return false
    end
end

function stopPolling()
    print("🛑 Stopping refresh states polling...")
    local success = _PY.stop_refresh_states_polling()
    if success then
        print("✅ Polling stopped successfully")
    else
        print("❌ Failed to stop polling")
    end
    return success
end

function showQueueStatus()
    local size = _PY.get_event_count()
    print(string.format("📦 Current queue size: %d events", size))
    return size
end

function clearQueue()
    local success = _PY.clear_events()
    print("🗑️  Queue cleared:", success and "✅ Success" or "❌ Failed")
    return success
end

-- Timer-based event processing (every 5 seconds)
local function setupEventProcessor()
    _PY.set_timeout(_G._CALLBACK_COUNTER + 1000, 5000)
    _G._CALLBACK_COUNTER = _G._CALLBACK_COUNTER + 1000
    
    -- Register callback for event processing
    _G["callback_" .. (_G._CALLBACK_COUNTER)] = function()
        processDeviceChangeEvents()
        
        -- Schedule next processing
        setupEventProcessor()
    end
end

-- Initialize
print("\n🎮 Demo Commands:")
print("  startPolling()     - Start monitoring device changes")
print("  stopPolling()      - Stop monitoring")
print("  showQueueStatus()  - Show current queue size")
print("  clearQueue()       - Clear all events")
print("  processDeviceChangeEvents() - Manually process events")
print("  addEmulatedEvent(deviceId, action, value) - Add emulated event")

print("\n💡 To start monitoring, run: startPolling()")
print("   Note: Update HC3_IP variable with your actual HC3 IP address")

-- Initialize callback counter if not exists
if not _G._CALLBACK_COUNTER then
    _G._CALLBACK_COUNTER = 1000
end

-- Start event processor
setupEventProcessor()

print("\n✅ Refresh states integration demo ready!")
