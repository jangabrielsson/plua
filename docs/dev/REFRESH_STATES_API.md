# Refresh States and Event Queue Functions

This document describes the new `_PY` functions added to EPLua for handling refresh states polling and event queue management. These functions are particularly useful for Fibaro HC3 integration where you need to monitor device state changes in real-time.

## Overview

The new functions provide:
- **Background polling** of HTTP endpoints (like HC3's `/api/refreshStates`)
- **Event queue management** for storing and processing state changes
- **Thread-safe communication** between background polling threads and Lua scripts

## Function Reference

### Refresh States Polling

#### `_PY.start_refresh_states_polling(url, interval_seconds)`
Starts background polling of a refresh states endpoint.

**Parameters:**
- `url` (string): The HTTP endpoint to poll (e.g., `"http://192.168.1.100/api/refreshStates"`)
- `interval_seconds` (number): Polling interval in seconds (default: 1.0)

**Returns:**
- `true` if polling started successfully, `false` otherwise

**Example:**
```lua
local success = _PY.start_refresh_states_polling("http://192.168.1.100/api/refreshStates", 2.0)
if success then
    print("Started polling every 2 seconds")
end
```

#### `_PY.stop_refresh_states_polling()`
Stops the background polling thread.

**Returns:**
- `true` if stopped successfully, `false` if no polling was active

**Example:**
```lua
local stopped = _PY.stop_refresh_states_polling()
print("Polling stopped:", stopped)
```

#### Global Callback: `onRefreshStatesUpdate(data)`
When polling is active, EPLua will call this global function whenever new data is received.

**Parameters:**
- `data`: The JSON response from the refresh states endpoint, converted to a Lua table

**Example:**
```lua
function onRefreshStatesUpdate(refreshData)
    if refreshData and refreshData.last then
        for deviceId, deviceData in pairs(refreshData.last) do
            print("Device", deviceId, "value:", deviceData.value)
        end
    end
end
```

### Event Queue Management

#### `_PY.create_event_queue(queue_name)`
Creates a new event queue with the specified name.

**Parameters:**
- `queue_name` (string): Unique name for the queue

**Returns:**
- `true` if created successfully, `false` otherwise

**Example:**
```lua
local success = _PY.create_event_queue("device_changes")
```

#### `_PY.add_event_to_queue(queue_name, event_data)`
Adds an event to the specified queue.

**Parameters:**
- `queue_name` (string): Name of the queue
- `event_data` (any): Data to store in the queue (will be converted to Lua-compatible format)

**Returns:**
- `true` if added successfully, `false` otherwise

**Example:**
```lua
local event = {
    type = "device_change",
    deviceId = 123,
    timestamp = _PY.get_time(),
    newValue = "true"
}
_PY.add_event_to_queue("device_changes", event)
```

#### `_PY.get_events_from_queue(queue_name, max_events)`
Retrieves events from the queue (non-blocking).

**Parameters:**
- `queue_name` (string): Name of the queue
- `max_events` (number): Maximum number of events to retrieve (default: 10)

**Returns:**
- Array of events (empty array if no events available)

**Example:**
```lua
local events = _PY.get_events_from_queue("device_changes", 5)
for i, event in ipairs(events) do
    print("Event", i, ":", event.type, event.deviceId)
end
```

#### `_PY.get_queue_size(queue_name)`
Gets the current number of events in the queue.

**Parameters:**
- `queue_name` (string): Name of the queue

**Returns:**
- Number of events in the queue (0 if queue doesn't exist)

**Example:**
```lua
local size = _PY.get_queue_size("device_changes")
print("Queue has", size, "events")
```

#### `_PY.clear_event_queue(queue_name)`
Removes all events from the specified queue.

**Parameters:**
- `queue_name` (string): Name of the queue

**Returns:**
- `true` if cleared successfully, `false` otherwise

**Example:**
```lua
local cleared = _PY.clear_event_queue("device_changes")
```

## Usage Patterns

### Basic Polling Setup
```lua
-- Start polling
_PY.start_refresh_states_polling("http://192.168.1.100/api/refreshStates", 3.0)

-- Handle updates
function onRefreshStatesUpdate(data)
    print("Received update at", os.date())
    -- Process the data...
end

-- Stop when done
_PY.stop_refresh_states_polling()
```

### Event Queue Processing
```lua
-- Create queue
_PY.create_event_queue("my_events")

-- Add events
_PY.add_event_to_queue("my_events", {type="test", message="hello"})

-- Process events periodically
local function processEvents()
    local events = _PY.get_events_from_queue("my_events", 10)
    for _, event in ipairs(events) do
        print("Processing:", event.type, event.message)
    end
end

-- Set up timer to process events every 5 seconds
setTimeout(function()
    processEvents()
end, 5000)
```

### Fibaro Device Monitoring
```lua
local previousStates = {}

function onRefreshStatesUpdate(refreshData)
    if not refreshData or not refreshData.last then return end
    
    for deviceId, deviceData in pairs(refreshData.last) do
        local prev = previousStates[deviceId]
        local current = deviceData.value
        
        if prev and prev ~= current then
            -- Device changed
            local changeEvent = {
                type = "device_change",
                deviceId = tonumber(deviceId),
                oldValue = prev,
                newValue = current,
                timestamp = _PY.get_time()
            }
            
            _PY.add_event_to_queue("device_changes", changeEvent)
        end
        
        previousStates[deviceId] = current
    end
end

-- Process device changes
local function handleDeviceChanges()
    local changes = _PY.get_events_from_queue("device_changes", 20)
    for _, change in ipairs(changes) do
        print(string.format("Device %d: %s -> %s", 
            change.deviceId, change.oldValue, change.newValue))
    end
end
```

## Thread Safety

All functions are thread-safe and can be called from:
- Main Lua thread
- Timer callbacks
- HTTP request callbacks
- Background polling threads

The functions automatically handle conversion between Python data types and Lua tables.

## Error Handling

All functions return `false` or empty results on error and log error messages to the console. Always check return values for critical operations:

```lua
local success = _PY.start_refresh_states_polling(url, interval)
if not success then
    print("Failed to start polling - check HC3 connection")
end
```

## Integration with QuickApps

These functions integrate seamlessly with Fibaro QuickApps. See `examples/fibaro/QA_device_monitor.lua` for a complete example of a QuickApp that monitors device changes using these functions.

## Performance Notes

- Polling creates a background Python thread that doesn't block Lua execution
- Event queues are thread-safe Python Queue objects
- Data conversion between Python and Lua happens automatically
- Memory usage scales with queue size - clear queues regularly if processing many events
- Polling threads are automatically cleaned up when EPLua shuts down
