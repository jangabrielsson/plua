# Fibaro API Functions Documentation

This document lists all the Fibaro HC3 API functions available in the plua Fibaro emulation environment.

## Core Fibaro Functions

### Logging and Debug Functions

#### fibaro.debug(tag, ...)
Debug level logging with tag.
- **Parameters**: 
  - `tag` (string): Log tag identifier
  - `...`: Values to log
- **Usage**: `fibaro.debug("MyTag", "Debug message", value)`

#### fibaro.trace(tag, ...)
Trace level logging with tag.
- **Parameters**: 
  - `tag` (string): Log tag identifier  
  - `...`: Values to log
- **Usage**: `fibaro.trace("MyTag", "Trace message")`

#### fibaro.warning(tag, ...)
Warning level logging with tag.
- **Parameters**: 
  - `tag` (string): Log tag identifier
  - `...`: Values to log
- **Usage**: `fibaro.warning("MyTag", "Warning message")`

#### fibaro.error(tag, ...)
Error level logging with tag.
- **Parameters**: 
  - `tag` (string): Log tag identifier
  - `...`: Values to log
- **Usage**: `fibaro.error("MyTag", "Error message")`

### Device Management Functions

#### fibaro.call(deviceId, action, ...)
Calls an action on a device or multiple devices.
- **Parameters**: 
  - `deviceId` (number|table): Device ID or table of device IDs
  - `action` (string): Action name to call
  - `...`: Arguments to pass to the action
- **Returns**: API call result for single device, nil for multiple devices
- **Usage**: 
  ```lua
  fibaro.call(123, "turnOn")
  fibaro.call({123, 124}, "setValue", 50)
  ```

#### fibaro.callhc3(deviceId, action, ...)
HC3-specific device action call.
- **Parameters**: 
  - `deviceId` (number): Device ID
  - `action` (string): Action name
  - `...`: Action arguments
- **Usage**: `fibaro.callhc3(123, "setValue", 75)`

#### fibaro.get(deviceId, propertyName)
Gets a device property value.
- **Parameters**: 
  - `deviceId` (number): Device ID
  - `propertyName` (string): Property name
- **Returns**: Property value or nil if not found
- **Usage**: `local value = fibaro.get(123, "value")`

#### fibaro.getValue(deviceId, propertyName)
Gets a device property value (alias for fibaro.get).
- **Parameters**: 
  - `deviceId` (number): Device ID
  - `propertyName` (string): Property name
- **Returns**: Property value or nil if not found
- **Usage**: `local value = fibaro.getValue(123, "value")`

#### fibaro.getType(deviceId)
Gets the device type.
- **Parameters**: 
  - `deviceId` (number): Device ID
- **Returns**: Device type string or nil if not found
- **Usage**: `local type = fibaro.getType(123)`

#### fibaro.getName(deviceId)
Gets the device name.
- **Parameters**: 
  - `deviceId` (number): Device ID
- **Returns**: Device name string or nil if not found
- **Usage**: `local name = fibaro.getName(123)`

#### fibaro.getRoomID(deviceId)
Gets the room ID for a device.
- **Parameters**: 
  - `deviceId` (number): Device ID
- **Returns**: Room ID (number) or nil if not found
- **Usage**: `local roomId = fibaro.getRoomID(123)`

#### fibaro.getSectionID(deviceId)
Gets the section ID for a device.
- **Parameters**: 
  - `deviceId` (number): Device ID
- **Returns**: Section ID (number) or nil if not found
- **Usage**: `local sectionId = fibaro.getSectionID(123)`

#### fibaro.getRoomName(roomId)
Gets the room name by room ID.
- **Parameters**: 
  - `roomId` (number): Room ID
- **Returns**: Room name string or nil if not found
- **Usage**: `local roomName = fibaro.getRoomName(5)`

#### fibaro.getRoomNameByDeviceID(deviceId)
Gets the room name for a device.
- **Parameters**: 
  - `deviceId` (number): Device ID
- **Returns**: Room name string or nil if not found
- **Usage**: `local roomName = fibaro.getRoomNameByDeviceID(123)`

#### fibaro.getDevicesID(filter)
Gets device IDs matching a filter.
- **Parameters**: 
  - `filter` (table): Filter criteria (properties, interfaces, etc.)
- **Returns**: Table of device IDs
- **Usage**: 
  ```lua
  local devices = fibaro.getDevicesID({
    interfaces = {"dimmable"},
    properties = {dead = false}
  })
  ```

#### fibaro.getIds(devices)
Extracts IDs from device objects.
- **Parameters**: 
  - `devices` (table): Table of device objects
- **Returns**: Table of device IDs
- **Usage**: `local ids = fibaro.getIds(deviceObjects)`

#### fibaro.wakeUpDeadDevice(deviceID)
Attempts to wake up a dead Z-Wave device.
- **Parameters**: 
  - `deviceID` (number): Device ID
- **Usage**: `fibaro.wakeUpDeadDevice(123)`

### Global Variables

#### fibaro.getGlobalVariable(name)
Gets global variable value and modification time.
- **Parameters**: 
  - `name` (string): Variable name
- **Returns**: Variable value, modification timestamp
- **Usage**: 
  ```lua
  local value, modified = fibaro.getGlobalVariable("MyVar")
  ```

#### fibaro.setGlobalVariable(name, value)
Sets global variable value.
- **Parameters**: 
  - `name` (string): Variable name
  - `value` (string): New value
- **Returns**: API call result
- **Usage**: `fibaro.setGlobalVariable("MyVar", "NewValue")`

### Scene Variables

#### fibaro.getSceneVariable(name)
Gets scene variable value.
- **Parameters**: 
  - `name` (string): Variable name
- **Returns**: Variable value
- **Usage**: `local value = fibaro.getSceneVariable("counter")`

#### fibaro.setSceneVariable(name, value)
Sets scene variable value.
- **Parameters**: 
  - `name` (string): Variable name
  - `value`: New value
- **Usage**: `fibaro.setSceneVariable("counter", 5)`

### Scene and Profile Management

#### fibaro.scene(action, ids)
Executes or kills scenes.
- **Parameters**: 
  - `action` (string): "execute" or "kill"
  - `ids` (table): Table of scene IDs
- **Usage**: 
  ```lua
  fibaro.scene("execute", {101, 102})
  fibaro.scene("kill", {103})
  ```

#### fibaro.profile(action, id)
Activates a user profile.
- **Parameters**: 
  - `action` (string): Must be "activeProfile"
  - `id` (number): Profile ID
- **Returns**: API call result
- **Usage**: `fibaro.profile("activeProfile", 1)`

### Security and Alarms

#### fibaro.alarm(partitionId, action)
Controls alarm partitions.
- **Parameters**: 
  - `partitionId` (number): Partition ID (0 for all partitions)
  - `action` (string): "arm", "disarm", "armDelay"
- **Usage**: 
  ```lua
  fibaro.alarm(1, "arm")
  fibaro.alarm(0, "disarm") -- All partitions
  ```

#### fibaro.getPartitions()
Gets all alarm partitions.
- **Returns**: Table of partition objects
- **Usage**: `local partitions = fibaro.getPartitions()`

#### fibaro.isHomeBreached()
Checks if home security is breached.
- **Returns**: Boolean indicating breach status
- **Usage**: `local breached = fibaro.isHomeBreached()`

#### fibaro.isPartitionBreached(partitionId)
Checks if specific partition is breached.
- **Parameters**: 
  - `partitionId` (number): Partition ID
- **Returns**: Boolean indicating breach status
- **Usage**: `local breached = fibaro.isPartitionBreached(1)`

#### fibaro.getPartitionArmState(partitionId)
Gets partition arm state.
- **Parameters**: 
  - `partitionId` (number): Partition ID
- **Returns**: Arm state string
- **Usage**: `local state = fibaro.getPartitionArmState(1)`

#### fibaro.getHomeArmState()
Gets overall home arm state.
- **Returns**: Arm state string
- **Usage**: `local state = fibaro.getHomeArmState()`

#### fibaro.alert(alertType, ids, notification)
Sends alerts to devices.
- **Parameters**: 
  - `alertType` (string): Type of alert
  - `ids` (table): Device IDs to alert
  - `notification` (table): Notification details
- **Usage**: 
  ```lua
  fibaro.alert("critical", {123}, {
    title = "Alert",
    text = "Emergency!"
  })
  ```

### Events and Actions

#### fibaro.emitCustomEvent(name)
Emits a custom event.
- **Parameters**: 
  - `name` (string): Event name
- **Usage**: `fibaro.emitCustomEvent("MyCustomEvent")`

#### fibaro.callGroupAction(actionName, actionData)
Calls a group action.
- **Parameters**: 
  - `actionName` (string): Action name
  - `actionData`: Action data
- **Usage**: `fibaro.callGroupAction("allLightsOff", {})`

### Timing Functions

#### fibaro.setTimeout(timeout, action, errorHandler)
Sets a timeout for delayed execution.
- **Parameters**: 
  - `timeout` (number): Timeout in milliseconds
  - `action` (function): Function to execute
  - `errorHandler` (function): Error handler function
- **Returns**: Timer reference
- **Usage**: 
  ```lua
  local timer = fibaro.setTimeout(5000, function()
    print("5 seconds elapsed")
  end)
  ```

#### fibaro.clearTimeout(ref)
Clears a timeout.
- **Parameters**: 
  - `ref`: Timer reference from setTimeout
- **Usage**: `fibaro.clearTimeout(timer)`

#### fibaro.sleep(ms)
Sleeps current coroutine for specified milliseconds.
- **Parameters**: 
  - `ms` (number): Milliseconds to sleep
- **Usage**: `fibaro.sleep(1000) -- Sleep 1 second`

#### fibaro.useAsyncHandler(value)
Controls async handler behavior.
- **Parameters**: 
  - `value` (boolean): Enable/disable async handlers
- **Returns**: Boolean indicating current state
- **Usage**: `fibaro.useAsyncHandler(true)`

## Global Functions

### print(...)
Enhanced print function using fibaro.debug.
- **Parameters**: `...`: Values to print
- **Usage**: `print("Hello", "World", 42)`

### class(name)
Creates a new class (QuickApp development).
- **Parameters**: 
  - `name` (string): Class name
- **Returns**: Class constructor
- **Usage**: 
  ```lua
  local MyClass = class("MyClass")
  function MyClass:new()
    -- Constructor
  end
  ```

### setTimeout(func, ms)
Global setTimeout function for QuickApps.
- **Parameters**: 
  - `func` (function): Function to execute
  - `ms` (number): Delay in milliseconds
- **Returns**: Timer reference
- **Usage**: 
  ```lua
  setTimeout(function()
    print("Timer fired!")
  end, 3000)
  ```

### setInterval(func, ms)
Global setInterval function for repeated execution.
- **Parameters**: 
  - `func` (function): Function to execute repeatedly
  - `ms` (number): Interval in milliseconds
- **Returns**: Interval reference
- **Usage**: 
  ```lua
  local interval = setInterval(function()
    print("Every 2 seconds")
  end, 2000)
  ```

### onAction(id, event)
QuickApp action handler.
- **Parameters**: 
  - `id` (number): Device ID
  - `event` (table): Action event data
- **Usage**: 
  ```lua
  function onAction(id, event)
    print("Action:", event.actionName)
  end
  ```

### onUIEvent(id, event)
QuickApp UI event handler.
- **Parameters**: 
  - `id` (number): Device ID
  - `event` (table): UI event data
- **Usage**: 
  ```lua
  function onUIEvent(id, event)
    print("UI Event:", event.elementName)
  end
  ```

## Utility Functions

### urlencode(str)
URL encodes a string.
- **Parameters**: 
  - `str` (string): String to encode
- **Returns**: URL-encoded string
- **Usage**: `local encoded = urlencode("hello world")`

### table.copy(obj)
Deep copies a table.
- **Parameters**: 
  - `obj` (table): Table to copy
- **Returns**: Deep copy of the table
- **Usage**: `local copy = table.copy(originalTable)`

### table.equal(e1, e2)
Compares two tables for equality.
- **Parameters**: 
  - `e1`, `e2`: Tables to compare
- **Returns**: Boolean indicating equality
- **Usage**: `local same = table.equal(table1, table2)`

### table.merge(a, b)
Merges two tables.
- **Parameters**: 
  - `a`, `b` (table): Tables to merge
- **Returns**: Merged table
- **Usage**: `local merged = table.merge(table1, table2)`

## Usage Examples

### Basic Device Control
```lua
-- Turn on a light
fibaro.call(123, "turnOn")

-- Set dimmer value
fibaro.call(124, "setValue", 75)

-- Get device status
local value = fibaro.getValue(123, "value")
local state = fibaro.getValue(123, "state")
```

### Working with Global Variables
```lua
-- Read a global variable
local temperature, modified = fibaro.getGlobalVariable("OutdoorTemp")
print("Temperature:", temperature, "Modified:", modified)

-- Set a global variable
fibaro.setGlobalVariable("LastUpdate", os.date())
```

### Scene Management
```lua
-- Execute scenes
fibaro.scene("execute", {101, 102})

-- Kill a running scene
fibaro.scene("kill", {103})
```

### Security System
```lua
-- Check if system is breached
if fibaro.isHomeBreached() then
    fibaro.debug("SECURITY", "Home is breached!")
end

-- Arm partition 1
fibaro.alarm(1, "arm")

-- Get all partitions
local partitions = fibaro.getPartitions()
for _, partition in ipairs(partitions) do
    print("Partition:", partition.id, "State:", partition.state)
end
```

### Advanced Device Filtering
```lua
-- Find all dimmable lights that are not dead
local devices = fibaro.getDevicesID({
    interfaces = {"dimmable"},
    properties = {
        dead = false,
        deviceIcon = 1001  -- Light bulb icon
    },
    roomID = 5  -- Specific room
})

-- Turn them all on
for _, deviceId in ipairs(devices) do
    fibaro.call(deviceId, "turnOn")
end
```

### Timer and Async Operations
```lua
-- Delayed action
fibaro.setTimeout(5000, function()
    fibaro.call(123, "turnOff")
end)

-- Using sleep in coroutines
function delayedSequence()
    fibaro.call(123, "turnOn")
    fibaro.sleep(2000)  -- Wait 2 seconds
    fibaro.call(124, "turnOn")
    fibaro.sleep(2000)  -- Wait 2 seconds
    fibaro.call(125, "turnOn")
end

-- Start the sequence
delayedSequence()
```

This documentation covers all the main Fibaro API functions available in the plua Fibaro emulation environment. These functions provide comprehensive control over devices, scenes, security systems, and other HC3 features.
