# Fibaro API Functions Documentation

This document lists all the Fibaro HC3 API functions available in the plua Fibaro emulation environment.

## Function Index

### Logging and Debug Functions
- [`fibaro.debug(tag, ...)`](#fibarodebugtag-) - Debug level logging with tag
- [`fibaro.trace(tag, ...)`](#fibarotracetag-) - Trace level logging with tag
- [`fibaro.warning(tag, ...)`](#fibarowarningtag-) - Warning level logging with tag
- [`fibaro.error(tag, ...)`](#fibaroerrortag-) - Error level logging with tag

### Device Management Functions
- [`fibaro.call(deviceId, action, ...)`](#fibarocalldeviceid-action-) - Execute action on device(s)
- [`fibaro.callhc3(deviceId, action, ...)`](#fibarocallhc3deviceid-action-) - HC3-specific device action call
- [`fibaro.get(deviceId, propertyName)`](#fibarogetdeviceid-propertyname) - Get device property value
- [`fibaro.getValue(deviceId, propertyName)`](#fibarogetvaluedeviceid-propertyname) - Get device property value (alias)
- [`fibaro.getType(deviceId)`](#fibarogettypedeviceid) - Get device type
- [`fibaro.getName(deviceId)`](#fibarogetnamedeviceid) - Get device name
- [`fibaro.getRoomID(deviceId)`](#fibarogetroomiddeviceid) - Get room ID for device
- [`fibaro.getSectionID(deviceId)`](#fibarogetsectioniddeviceid) - Get section ID for device
- [`fibaro.getRoomName(roomId)`](#fibarogetroomnameroomid) - Get room name by room ID
- [`fibaro.getRoomNameByDeviceID(deviceId)`](#fibarogetroomnamebydeviceiddeviceid) - Get room name for device
- [`fibaro.getDevicesID(filter)`](#fibarogetdevicesidfilter) - Get device IDs matching filter
- [`fibaro.getIds(devices)`](#fibarogetidsdevices) - Extract IDs from device objects
- [`fibaro.wakeUpDeadDevice(deviceID)`](#fibarowakeupdeaddevicedeviceid) - Wake up dead Z-Wave device

### Global Variables
- [`fibaro.getGlobalVariable(name)`](#fibarogetglobalvariablename) - Get global variable value and timestamp
- [`fibaro.setGlobalVariable(name, value)`](#fibarosetglobalvariablename-value) - Set global variable value

### Scene Variables
- [`fibaro.getSceneVariable(name)`](#fibarogetscenevariablename) - Get scene variable value
- [`fibaro.setSceneVariable(name, value)`](#fibarosetscenevariablename-value) - Set scene variable value

### Scene and Profile Management
- [`fibaro.scene(action, ids)`](#fibarosceneaction-ids) - Execute or kill scenes
- [`fibaro.profile(action, id)`](#fibaroprofileaction-id) - Activate user profile

### Security and Alarms
- [`fibaro.alarm(partitionId, action)`](#fibaroalarmpartitionid-action) - Control alarm partitions
- [`fibaro.getPartitions()`](#fibarogetpartitions) - Get all alarm partitions
- [`fibaro.isHomeBreached()`](#fibaroisbreached) - Check if home security is breached
- [`fibaro.isPartitionBreached(partitionId)`](#fibaroispartitionbreachedpartitionid) - Check if partition is breached
- [`fibaro.getPartitionArmState(partitionId)`](#fibarogetpartitionarmstatepartitionid) - Get partition arm state
- [`fibaro.getHomeArmState()`](#fibarogethomearmstate) - Get overall home arm state
- [`fibaro.alert(alertType, ids, notification)`](#fibaroalertalerttype-ids-notification) - Send alerts to devices

### Events and Actions
- [`fibaro.emitCustomEvent(name)`](#fibaroemitcustomeventname) - Emit custom event
- [`fibaro.callGroupAction(actionName, actionData)`](#fibarocallgroupactionactionname-actiondata) - Call group action

### Timing Functions
- [`fibaro.setTimeout(timeout, action, errorHandler)`](#fibarosettimeouttimeout-action-errorhandler) - Set timeout for delayed execution
- [`fibaro.clearTimeout(ref)`](#fibarocleartimeoutref) - Clear timeout
- [`fibaro.sleep(ms)`](#fibarosleepms) - Sleep current coroutine
- [`fibaro.useAsyncHandler(value)`](#fibarouseasynchandlervalue) - Control async handler behavior

### Global Functions
- [`print(...)`](#print-) - Enhanced print function
- [`class(name)`](#classname) - Create new class
- [`setTimeout(func, ms)`](#settimeoutfunc-ms) - Global setTimeout function
- [`setInterval(func, ms)`](#setintervalfunc-ms) - Global setInterval function
- [`onAction(id, event)`](#onactionid-event) - QuickApp action handler
- [`onUIEvent(id, event)`](#onuieventid-event) - QuickApp UI event handler

### Utility Functions
- [`urlencode(str)`](#urlencodestr) - URL encode string
- [`table.copy(obj)`](#tablecopyobj) - Deep copy table
- [`table.equal(e1, e2)`](#tableequale1-e2) - Compare tables for equality
- [`table.merge(a, b)`](#tablemergea-b) - Merge two tables

---

## Core Fibaro Functions

### Logging and Debug Functions

#### fibaro.debug(tag, ...)
Outputs a debug-level log message with the specified tag for troubleshooting and development purposes.

- **Parameters**: 
  - `tag` (string): Log tag identifier for categorizing and filtering log messages
  - `...`: Variable number of arguments to be logged (strings, numbers, tables, etc.)
- **Usage**: 
  ```lua
  fibaro.debug("MyTag", "Debug message", value)
  ```

#### fibaro.trace(tag, ...)
Outputs a trace-level log message with the specified tag for detailed execution tracking.

- **Parameters**: 
  - `tag` (string): Log tag identifier for categorizing and filtering log messages
  - `...`: Variable number of arguments to be logged (strings, numbers, tables, etc.)
- **Usage**: 
  ```lua
  fibaro.trace("MyTag", "Trace message")
  ```

#### fibaro.warning(tag, ...)
Outputs a warning-level log message with the specified tag for non-critical issues and alerts.

- **Parameters**: 
  - `tag` (string): Log tag identifier for categorizing and filtering log messages
  - `...`: Variable number of arguments to be logged (strings, numbers, tables, etc.)
- **Usage**: 
  ```lua
  fibaro.warning("MyTag", "Warning message")
  ```

#### fibaro.error(tag, ...)
Outputs an error-level log message with the specified tag for critical issues and failures.

- **Parameters**: 
  - `tag` (string): Log tag identifier for categorizing and filtering log messages
  - `...`: Variable number of arguments to be logged (strings, numbers, tables, etc.)
- **Usage**: 
  ```lua
  fibaro.error("MyTag", "Error message")
  ```

### Device Management Functions

#### fibaro.call(deviceId, action, ...)
Executes an action on a single device or multiple devices simultaneously.

- **Parameters**: 
  - `deviceId` (number|table): Device ID or table of device IDs to target
  - `action` (string): Name of the action to execute (e.g., "turnOn", "setValue", "turnOff")
  - `...`: Variable number of arguments to pass to the action method
- **Returns**: API call result for single device, nil for multiple devices
- **Usage**: 
  ```lua
  fibaro.call(123, "turnOn")
  fibaro.call({123, 124}, "setValue", 50)
  ```

#### fibaro.callhc3(deviceId, action, ...)
Executes an HC3-specific device action call with enhanced functionality.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the target device
  - `action` (string): Name of the action to execute
  - `...`: Variable number of arguments to pass to the action method
- **Usage**: 
  ```lua
  fibaro.callhc3(123, "setValue", 75)
  ```

#### fibaro.get(deviceId, propertyName)
Retrieves a specific property value from a device in the HC3 system.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the device
  - `propertyName` (string): The name of the property to retrieve (e.g., "value", "state", "name")
- **Returns**: The current value of the specified property or nil if not found
- **Usage**: 
  ```lua
  local value = fibaro.get(123, "value")
  ```

#### fibaro.getValue(deviceId, propertyName)
Retrieves a device property value (alias for fibaro.get with identical functionality).

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the device
  - `propertyName` (string): The name of the property to retrieve (e.g., "value", "state", "name")
- **Returns**: The current value of the specified property or nil if not found
- **Usage**: 
  ```lua
  local value = fibaro.getValue(123, "value")
  ```

#### fibaro.getType(deviceId)
Retrieves the device type identifier from the HC3 system.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the device
- **Returns**: Device type string (e.g., "com.fibaro.binarySwitch") or nil if not found
- **Usage**: 
  ```lua
  local type = fibaro.getType(123)
  ```

#### fibaro.getName(deviceId)
Retrieves the display name of a device from the HC3 system.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the device
- **Returns**: Device name string or nil if not found
- **Usage**: 
  ```lua
  local name = fibaro.getName(123)
  ```

#### fibaro.getRoomID(deviceId)
Retrieves the room identifier where a device is located.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the device
- **Returns**: Room ID (number) or nil if not found
- **Usage**: 
  ```lua
  local roomId = fibaro.getRoomID(123)
  ```

#### fibaro.getSectionID(deviceId)
Retrieves the section identifier where a device is located.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the device
- **Returns**: Section ID (number) or nil if not found
- **Usage**: 
  ```lua
  local sectionId = fibaro.getSectionID(123)
  ```

#### fibaro.getRoomName(roomId)
Retrieves the display name of a room by its identifier.

- **Parameters**: 
  - `roomId` (number): The unique identifier of the room
- **Returns**: Room name string or nil if not found
- **Usage**: 
  ```lua
  local roomName = fibaro.getRoomName(5)
  ```

#### fibaro.getRoomNameByDeviceID(deviceId)
Retrieves the room name for a specific device by looking up its room association.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the device
- **Returns**: Room name string or nil if not found
- **Usage**: 
  ```lua
  local roomName = fibaro.getRoomNameByDeviceID(123)
  ```

#### fibaro.getDevicesID(filter)
Retrieves device IDs that match the specified filter criteria.

- **Parameters**: 
  - `filter` (table): Filter criteria table containing properties, interfaces, roomID, etc.
    - `interfaces` (table, optional): Array of interface names to match
    - `properties` (table, optional): Property values to match
    - `roomID` (number, optional): Specific room ID to filter by
- **Returns**: Table of device IDs that match the filter criteria
- **Usage**: 
  ```lua
  local devices = fibaro.getDevicesID({
    interfaces = {"dimmable"},
    properties = {dead = false}
  })
  ```

#### fibaro.getIds(devices)
Extracts device IDs from a table of device objects.

- **Parameters**: 
  - `devices` (table): Table of device objects containing device information
- **Returns**: Table of device IDs extracted from the device objects
- **Usage**: 
  ```lua
  local ids = fibaro.getIds(deviceObjects)
  ```

#### fibaro.wakeUpDeadDevice(deviceID)
Attempts to wake up a dead Z-Wave device by sending wake-up commands.

- **Parameters**: 
  - `deviceID` (number): The unique identifier of the Z-Wave device to wake up
- **Usage**: 
  ```lua
  fibaro.wakeUpDeadDevice(123)
  ```

### Global Variables

#### fibaro.getGlobalVariable(name)
Retrieves a global variable value and its last modification timestamp.

- **Parameters**: 
  - `name` (string): The name of the global variable to retrieve
- **Returns**: Variable value and modification timestamp (value, modified)
- **Usage**: 
  ```lua
  local value, modified = fibaro.getGlobalVariable("MyVar")
  ```

#### fibaro.setGlobalVariable(name, value)
Creates or updates a global variable with the specified name and value.

- **Parameters**: 
  - `name` (string): The name of the global variable to set
  - `value` (string): The new value to assign to the variable
- **Returns**: API call result indicating success or failure
- **Usage**: 
  ```lua
  fibaro.setGlobalVariable("MyVar", "NewValue")
  ```

### Scene Variables

#### fibaro.getSceneVariable(name)
Retrieves the current value of a scene variable.

- **Parameters**: 
  - `name` (string): The name of the scene variable to retrieve
- **Returns**: The current value of the scene variable
- **Usage**: 
  ```lua
  local value = fibaro.getSceneVariable("counter")
  ```

#### fibaro.setSceneVariable(name, value)
Creates or updates a scene variable with the specified name and value.

- **Parameters**: 
  - `name` (string): The name of the scene variable to set
  - `value`: The new value to assign to the variable (can be string, number, boolean, or table)
- **Usage**: 
  ```lua
  fibaro.setSceneVariable("counter", 5)
  ```

### Scene and Profile Management

#### fibaro.scene(action, ids)
Executes or terminates scenes based on the specified action.

- **Parameters**: 
  - `action` (string): Action to perform - "execute" to start scenes or "kill" to stop them
  - `ids` (table): Table of scene IDs to target
- **Usage**: 
  ```lua
  fibaro.scene("execute", {101, 102})
  fibaro.scene("kill", {103})
  ```

#### fibaro.profile(action, id)
Activates a specific user profile in the HC3 system.

- **Parameters**: 
  - `action` (string): Must be "activeProfile" to activate a profile
  - `id` (number): The unique identifier of the profile to activate
- **Returns**: API call result indicating success or failure
- **Usage**: 
  ```lua
  fibaro.profile("activeProfile", 1)
  ```

### Security and Alarms

#### fibaro.alarm(partitionId, action)
Controls alarm partition states and operations.

- **Parameters**: 
  - `partitionId` (number): Partition ID (0 for all partitions, 1+ for specific partitions)
  - `action` (string): Action to perform - "arm", "disarm", or "armDelay"
- **Usage**: 
  ```lua
  fibaro.alarm(1, "arm")
  fibaro.alarm(0, "disarm") -- All partitions
  ```

#### fibaro.getPartitions()
Retrieves all alarm partitions and their current states.

- **Returns**: Table of partition objects containing partition information and states
- **Usage**: 
  ```lua
  local partitions = fibaro.getPartitions()
  ```

#### fibaro.isHomeBreached()
Checks if the home security system has been breached.

- **Returns**: Boolean indicating whether the home security is currently breached
- **Usage**: 
  ```lua
  local breached = fibaro.isHomeBreached()
  ```

#### fibaro.isPartitionBreached(partitionId)
Checks if a specific alarm partition has been breached.

- **Parameters**: 
  - `partitionId` (number): The unique identifier of the partition to check
- **Returns**: Boolean indicating whether the specified partition is breached
- **Usage**: 
  ```lua
  local breached = fibaro.isPartitionBreached(1)
  ```

#### fibaro.getPartitionArmState(partitionId)
Retrieves the current arm state of a specific alarm partition.

- **Parameters**: 
  - `partitionId` (number): The unique identifier of the partition
- **Returns**: Arm state string (e.g., "armed", "disarmed", "arming")
- **Usage**: 
  ```lua
  local state = fibaro.getPartitionArmState(1)
  ```

#### fibaro.getHomeArmState()
Retrieves the overall home security arm state.

- **Returns**: Arm state string representing the overall home security status
- **Usage**: 
  ```lua
  local state = fibaro.getHomeArmState()
  ```

#### fibaro.alert(alertType, ids, notification)
Sends alerts and notifications to specified devices.

- **Parameters**: 
  - `alertType` (string): Type of alert (e.g., "critical", "warning", "info")
  - `ids` (table): Table of device IDs to receive the alert
  - `notification` (table): Notification details containing title, text, and other properties
- **Usage**: 
  ```lua
  fibaro.alert("critical", {123}, {
    title = "Alert",
    text = "Emergency!"
  })
  ```

### Events and Actions

#### fibaro.emitCustomEvent(name)
Emits a custom event that can be listened to by other scripts and scenes.

- **Parameters**: 
  - `name` (string): The name of the custom event to emit
- **Usage**: 
  ```lua
  fibaro.emitCustomEvent("MyCustomEvent")
  ```

#### fibaro.callGroupAction(actionName, actionData)
Executes a group action across multiple devices or scenes.

- **Parameters**: 
  - `actionName` (string): The name of the group action to execute
  - `actionData`: Data or parameters to pass to the group action
- **Usage**: 
  ```lua
  fibaro.callGroupAction("allLightsOff", {})
  ```

### Timing Functions

#### fibaro.setTimeout(timeout, action, errorHandler)
Sets a timeout for delayed execution of a function.

- **Parameters**: 
  - `timeout` (number): Timeout duration in milliseconds
  - `action` (function): Function to execute when the timeout expires
  - `errorHandler` (function, optional): Function to handle any errors during execution
- **Returns**: Timer reference that can be used to cancel the timeout
- **Usage**: 
  ```lua
  local timer = fibaro.setTimeout(5000, function()
    print("5 seconds elapsed")
  end)
  ```

#### fibaro.clearTimeout(ref)
Cancels a previously set timeout before it executes.

- **Parameters**: 
  - `ref`: Timer reference returned from fibaro.setTimeout
- **Usage**: 
  ```lua
  fibaro.clearTimeout(timer)
  ```

#### fibaro.sleep(ms)
Suspends the current coroutine for the specified number of milliseconds.

- **Parameters**: 
  - `ms` (number): Number of milliseconds to sleep
- **Usage**: 
  ```lua
  fibaro.sleep(1000) -- Sleep 1 second
  ```

#### fibaro.useAsyncHandler(value)
Controls the behavior of asynchronous handlers in the system.

- **Parameters**: 
  - `value` (boolean): True to enable async handlers, false to disable them
- **Returns**: Boolean indicating the current async handler state
- **Usage**: 
  ```lua
  fibaro.useAsyncHandler(true)
  ```

## Global Functions

### print(...)
Enhanced print function that uses fibaro.debug for consistent logging.

- **Parameters**: `...`: Variable number of arguments to print (strings, numbers, tables, etc.)
- **Usage**: 
  ```lua
  print("Hello", "World", 42)
  ```

### class(name)
Creates a new class constructor for object-oriented QuickApp development.

- **Parameters**: 
  - `name` (string): The name of the class to create
- **Returns**: Class constructor function
- **Usage**: 
  ```lua
  local MyClass = class("MyClass")
  function MyClass:new()
    -- Constructor
  end
  ```

### setTimeout(func, ms)
Global setTimeout function for QuickApps to schedule delayed execution.

- **Parameters**: 
  - `func` (function): Function to execute after the delay
  - `ms` (number): Delay duration in milliseconds
- **Returns**: Timer reference that can be used to cancel the timeout
- **Usage**: 
  ```lua
  setTimeout(function()
    print("Timer fired!")
  end, 3000)
  ```

### setInterval(func, ms)
Global setInterval function for QuickApps to schedule repeated execution.

- **Parameters**: 
  - `func` (function): Function to execute repeatedly at the specified interval
  - `ms` (number): Interval duration in milliseconds
- **Returns**: Interval reference that can be used to stop the interval
- **Usage**: 
  ```lua
  local interval = setInterval(function()
    print("Every 2 seconds")
  end, 2000)
  ```

### onAction(id, event)
Global QuickApp action handler that processes device action events.

- **Parameters**: 
  - `id` (number): The device ID where the action was triggered
  - `event` (table): Action event data containing action details and parameters
- **Usage**: 
  ```lua
  function onAction(id, event)
    print("Action:", event.actionName)
  end
  ```

### onUIEvent(id, event)
Global QuickApp UI event handler that processes user interface events.

- **Parameters**: 
  - `id` (number): The device ID where the UI event occurred
  - `event` (table): UI event data containing element information and event details
- **Usage**: 
  ```lua
  function onUIEvent(id, event)
    print("UI Event:", event.elementName)
  end
  ```

## Utility Functions

### urlencode(str)
URL encodes a string for safe transmission in HTTP requests.

- **Parameters**: 
  - `str` (string): The string to URL encode
- **Returns**: URL-encoded string with special characters properly escaped
- **Usage**: 
  ```lua
  local encoded = urlencode("hello world")
  ```

### table.copy(obj)
Creates a deep copy of a table, including nested tables and structures.

- **Parameters**: 
  - `obj` (table): The table to create a deep copy of
- **Returns**: A completely independent copy of the original table
- **Usage**: 
  ```lua
  local copy = table.copy(originalTable)
  ```

### table.equal(e1, e2)
Compares two tables for deep equality, checking all nested values.

- **Parameters**: 
  - `e1`, `e2`: The tables to compare for equality
- **Returns**: Boolean indicating whether the tables are deeply equal
- **Usage**: 
  ```lua
  local same = table.equal(table1, table2)
  ```

### table.merge(a, b)
Merges two tables, with values from table b taking precedence over table a.

- **Parameters**: 
  - `a`, `b` (table): The tables to merge together
- **Returns**: A new table containing the merged contents of both input tables
- **Usage**: 
  ```lua
  local merged = table.merge(table1, table2)
  ```

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
