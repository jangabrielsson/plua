# QuickApp Documentation

This document covers the QuickApp framework classes and methods available in the plua Fibaro emulation environment for developing QuickApp plugins.

## Function Index

### Plugin Namespace Functions
- [`plugin.getDevice(deviceId)`](#plugingetdevicedeviceid) - Retrieve device by ID
- [`plugin.deleteDevice(deviceId)`](#plugindeletedevicedeviceid) - Delete device by ID
- [`plugin.getProperty(deviceId, propertyName)`](#plugingetpropertydeviceid-propertyname) - Get device property value
- [`plugin.getChildDevices(deviceId)`](#plugingetchilddevicesdeviceid) - Get child devices of parent device
- [`plugin.createChildDevice(opts)`](#plugincreatechilddeviceopts) - Create new child device
- [`plugin.restart(id)`](#pluginrestartid) - Restart QuickApp plugin

### QuickAppBase Class Methods

#### Constructor
- [`QuickAppBase:__init(dev)`](#quickappbase__initdev) - Initialize QuickAppBase instance

#### Logging Methods
- [`QuickAppBase:debug(...)`](#quickappbasedebug-) - Log debug message with device tag
- [`QuickAppBase:trace(...)`](#quickappbasetrace-) - Log trace message with device tag
- [`QuickAppBase:warning(...)`](#quickappbasewarning-) - Log warning message with device tag
- [`QuickAppBase:error(...)`](#quickappbaseerror-) - Log error message with device tag

#### UI Management Methods
- [`QuickAppBase:registerUICallback(elm, typ, fun)`](#quickappbaseregisteruicallbackelm-typ-fun) - Register UI callback function
- [`QuickAppBase:setupUICallbacks()`](#quickappbasesetupuicallbacks) - Setup UI callbacks from device properties
- [`QuickAppBase:updateView(elm, prop, value)`](#quickappbaseupdateviewelm-prop-value) - Update UI view element property
- [`QuickAppBase:UIAction(eventType, elementName, arg)`](#quickappbaseuiactioneventtype-elementname-arg) - Trigger UI action programmatically

#### Device Management Methods
- [`QuickAppBase:callAction(name, ...)`](#quickappbasecallactionname-) - Call action method on QuickApp
- [`QuickAppBase:updateProperty(name, value)`](#quickappbaseupdatepropertyname-value) - Update device property
- [`QuickAppBase:hasInterface(name)`](#quickappbasehasinterfacename) - Check if device has interface
- [`QuickAppBase:addInterfaces(values)`](#quickappbaseaddinterfacesvalues) - Add interfaces to device
- [`QuickAppBase:deleteInterfaces(values)`](#quickappbasedeleteinterfacesvalues) - Remove interfaces from device
- [`QuickAppBase:setName(name)`](#quickappbasesetnamename) - Set device name
- [`QuickAppBase:setEnabled(enabled)`](#quickappbasesetenabledenabled) - Set device enabled state
- [`QuickAppBase:setVisible(visible)`](#quickappbasesetvisiblevisible) - Set device visibility

#### Variable Management Methods
- [`QuickAppBase:setVariable(name, value)`](#quickappbasesetvariablename-value) - Set QuickApp variable value
- [`QuickAppBase:getVariable(name)`](#quickappbasegetvariablename) - Get QuickApp variable value

#### Internal Storage Methods
- [`QuickAppBase:internalStorageSet(key, val, hidden)`](#quickappbaseinternalstoragesetkey-val-hidden) - Set value in internal storage
- [`QuickAppBase:internalStorageGet(key)`](#quickappbaseinternalstoragegetkey) - Get value from internal storage
- [`QuickAppBase:internalStorageRemove(key)`](#quickappbaseinternalstorageremovekey) - Remove variable from internal storage
- [`QuickAppBase:internalStorageClear()`](#quickappbaseinternalstorageclear) - Clear all variables from internal storage

### QuickApp Class Methods

#### Constructor
- [`QuickApp:__init(dev)`](#quickapp__initdev) - Initialize main QuickApp instance

#### Child Device Management
- [`QuickApp:initChildDevices(map)`](#quickappinitchilddevicesmap) - Initialize child devices with optional class mappings
- [`QuickApp:createChildDevice(options, classRepresentation)`](#quickappcreatechilddeviceoptions-classrepresentation) - Create new child device instance

### QuickAppChild Class Methods

#### Constructor
- [`QuickAppChild:__init(dev)`](#quickappchild__initdev) - Initialize child device instance

### RefreshStateSubscriber Class Methods

#### Constructor
- [`RefreshStateSubscriber:__init()`](#refreshstatesubscriber__init) - Initialize refresh state subscriber

#### Subscription Methods
- [`RefreshStateSubscriber:subscribe(filter, handler)`](#refreshstatesubscribersubscribefilter-handler) - Subscribe to refresh state events
- [`RefreshStateSubscriber:unsubscribe(subscription)`](#refreshstatesubscriberunsubscribesubscription) - Unsubscribe from refresh state events
- [`RefreshStateSubscriber:run()`](#refreshstatesubscriberrun) - Start refresh state subscriber
- [`RefreshStateSubscriber:stop()`](#refreshstatesubscriberstop) - Stop refresh state subscriber

### Global Event Handlers
- [`onAction(id, event)`](#onactionid-event) - Global device action handler
- [`onUIEvent(id, event)`](#onuieventid-event) - Global UI event handler

---

## Plugin Namespace Functions

The `plugin` namespace provides utility functions for device and plugin management.

### plugin.getDevice(deviceId)
Retrieves a device object from the HC3 system by its unique identifier.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the device to retrieve
- **Returns**: Device object from the HC3 API containing device properties and metadata
- **Usage**: 
  ```lua
  local device = plugin.getDevice(123)
  ```

### plugin.deleteDevice(deviceId)
Permanently removes a device from the HC3 system by its identifier.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the device to delete
- **Returns**: Result of the delete operation (success/failure status)
- **Usage**: 
  ```lua
  plugin.deleteDevice(123)
  ```

### plugin.getProperty(deviceId, propertyName)
Retrieves a specific property value from a device in the HC3 system.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the device
  - `propertyName` (string): The name of the property to retrieve (e.g., "value", "state", "name")
- **Returns**: The current value of the specified property
- **Usage**: 
  ```lua
  local value = plugin.getProperty(123, "value")
  ```

### plugin.getChildDevices(deviceId)
Retrieves all child devices associated with a parent device.

- **Parameters**: 
  - `deviceId` (number): The unique identifier of the parent device
- **Returns**: Array of child device objects, each containing device properties and metadata
- **Usage**: 
  ```lua
  local children = plugin.getChildDevices(123)
  ```

### plugin.createChildDevice(opts)
Creates a new child device with the specified configuration options.

- **Parameters**: 
  - `opts` (table): Configuration table containing device creation options
    - `name` (string): Display name for the child device
    - `type` (string): Device type identifier (e.g., "com.fibaro.binarySwitch")
    - `interfaces` (table, optional): Array of interface names
    - `properties` (table, optional): Initial property values
- **Returns**: The newly created child device object
- **Usage**: 
  ```lua
  local child = plugin.createChildDevice({
    name = "Child Device",
    type = "com.fibaro.binarySwitch"
  })
  ```

### plugin.restart(id)
Restarts a QuickApp plugin, reloading its code and reinitializing the device.

- **Parameters**: 
  - `id` (number, optional): The device ID to restart (defaults to mainDeviceId if not specified)
- **Returns**: Result of the restart operation (success/failure status)
- **Usage**: 
  ```lua
  plugin.restart()
  plugin.restart(123)
  ```

## QuickAppBase Class

The base class for all QuickApp devices, providing core functionality for device management, logging, and UI interaction.

### Constructor

#### QuickAppBase:__init(dev)
Initializes a new QuickAppBase instance with the provided device configuration.

- **Parameters**: 
  - `dev` (table): Device object containing device properties, metadata, and configuration
- **Usage**: Called automatically when creating QuickApp instances

### Logging Methods

#### QuickAppBase:debug(...)
Outputs a debug-level log message with the device tag for troubleshooting and development.

- **Parameters**: `...`: Variable number of arguments to be logged (strings, numbers, tables, etc.)
- **Usage**: 
  ```lua
  self:debug("Debug message", value)
  ```

#### QuickAppBase:trace(...)
Outputs a trace-level log message with the device tag for detailed execution tracking.

- **Parameters**: `...`: Variable number of arguments to be logged (strings, numbers, tables, etc.)
- **Usage**: 
  ```lua
  self:trace("Trace message")
  ```

#### QuickAppBase:warning(...)
Outputs a warning-level log message with the device tag for non-critical issues.

- **Parameters**: `...`: Variable number of arguments to be logged (strings, numbers, tables, etc.)
- **Usage**: 
  ```lua
  self:warning("Warning message")
  ```

#### QuickAppBase:error(...)
Outputs an error-level log message with the device tag for critical issues and failures.

- **Parameters**: `...`: Variable number of arguments to be logged (strings, numbers, tables, etc.)
- **Usage**: 
  ```lua
  self:error("Error message")
  ```

### UI Management Methods

#### QuickAppBase:registerUICallback(elm, typ, fun)
Registers a callback function to handle UI events for a specific element and event type.

- **Parameters**: 
  - `elm` (string): The name of the UI element to monitor
  - `typ` (string): The type of UI event to handle (e.g., "onReleased", "onChanged", "onPressed")
  - `fun` (function): The callback function to execute when the event occurs
- **Usage**: 
  ```lua
  self:registerUICallback("button1", "onReleased", function(event)
    self:debug("Button pressed")
  end)
  ```

#### QuickAppBase:setupUICallbacks()
Automatically configures UI callbacks based on the device's uiCallbacks property configuration.

- **Usage**: 
  ```lua
  self:setupUICallbacks()
  ```

#### QuickAppBase:updateView(elm, prop, value)
Updates a specific property of a UI element in the device's user interface.

- **Parameters**: 
  - `elm` (string): The name of the UI element to update
  - `prop` (string): The property name to modify (e.g., "text", "visible", "enabled")
  - `value`: The new value to assign to the property
- **Usage**: 
  ```lua
  self:updateView("label1", "text", "New Text")
  ```

#### QuickAppBase:UIAction(eventType, elementName, arg)
Programmatically simulates a UI action event for testing and automation purposes.

- **Parameters**: 
  - `eventType` (string): The type of UI event to simulate (e.g., "onReleased", "onChanged")
  - `elementName` (string): The name of the UI element to trigger the event on
  - `arg` (optional): Optional argument value to pass with the event
- **Usage**: 
  ```lua
  self:UIAction("onReleased", "button1")
  ```

### Device Management Methods

#### QuickAppBase:callAction(name, ...)
Dynamically calls an action method on the QuickApp if it exists and is accessible.

- **Parameters**: 
  - `name` (string): The name of the action/method to call
  - `...`: Variable number of arguments to pass to the action method
- **Returns**: Result of the action method execution or nil if method doesn't exist
- **Usage**: 
  ```lua
  self:callAction("turnOn")
  ```

#### QuickAppBase:updateProperty(name, value)
Updates a device property and immediately synchronizes the change with the HC3 system.

- **Parameters**: 
  - `name` (string): The name of the property to update
  - `value`: The new value to assign to the property
- **Usage**: 
  ```lua
  self:updateProperty("value", 75)
  ```

#### QuickAppBase:hasInterface(name)
Checks whether the device currently supports a specific interface capability.

- **Parameters**: 
  - `name` (string): The interface name to check for (e.g., "dimmable", "energy", "turnOn")
- **Returns**: Boolean indicating whether the device has the specified interface
- **Usage**: 
  ```lua
  local hasDimmer = self:hasInterface("dimmable")
  ```

#### QuickAppBase:addInterfaces(values)
Adds new interface capabilities to the device, expanding its functionality.

- **Parameters**: 
  - `values` (table): Array of interface names to add to the device
- **Usage**: 
  ```lua
  self:addInterfaces({"dimmable", "energy"})
  ```

#### QuickAppBase:deleteInterfaces(values)
Removes interface capabilities from the device, reducing its functionality.

- **Parameters**: 
  - `values` (table): Array of interface names to remove from the device
- **Usage**: 
  ```lua
  self:deleteInterfaces({"energy"})
  ```

#### QuickAppBase:setName(name)
Changes the display name of the device in the HC3 interface.

- **Parameters**: 
  - `name` (string): The new display name for the device
- **Usage**: 
  ```lua
  self:setName("New Device Name")
  ```

#### QuickAppBase:setEnabled(enabled)
Controls whether the device is enabled and can perform its functions.

- **Parameters**: 
  - `enabled` (boolean): True to enable the device, false to disable it
- **Usage**: 
  ```lua
  self:setEnabled(true)
  ```

#### QuickAppBase:setVisible(visible)
Controls whether the device is visible in the HC3 user interface.

- **Parameters**: 
  - `visible` (boolean): True to make the device visible, false to hide it
- **Usage**: 
  ```lua
  self:setVisible(false)
  ```

### Variable Management Methods

#### QuickAppBase:setVariable(name, value)
Creates or updates a QuickApp variable with the specified name and value.

- **Parameters**: 
  - `name` (string): The name of the variable to set
  - `value`: The value to assign to the variable (can be string, number, boolean, or table)
- **Usage**: 
  ```lua
  self:setVariable("counter", "5")
  ```

#### QuickAppBase:getVariable(name)
Retrieves the current value of a QuickApp variable by its name.

- **Parameters**: 
  - `name` (string): The name of the variable to retrieve
- **Returns**: The current value of the variable or an empty string if not found
- **Usage**: 
  ```lua
  local counter = self:getVariable("counter")
  ```

### Internal Storage Methods

#### QuickAppBase:internalStorageSet(key, val, hidden)
Stores a value in the device's persistent internal storage for later retrieval.

- **Parameters**: 
  - `key` (string): The unique key to identify the stored value
  - `val`: The value to store (can be any Lua data type)
  - `hidden` (boolean, optional): True to hide the variable from the UI, false to show it
- **Returns**: HTTP status code indicating the success of the storage operation
- **Usage**: 
  ```lua
  self:internalStorageSet("config", {param1 = "value"})
  ```

#### QuickAppBase:internalStorageGet(key)
Retrieves a value from the device's persistent internal storage.

- **Parameters**: 
  - `key` (string, optional): The key of the value to retrieve (if nil, returns all stored variables)
- **Returns**: The stored value or nil if not found
- **Usage**: 
  ```lua
  local config = self:internalStorageGet("config")
  local allVars = self:internalStorageGet() -- Get all variables
  ```

#### QuickAppBase:internalStorageRemove(key)
Removes a specific variable from the device's persistent internal storage.

- **Parameters**: 
  - `key` (string): The key of the variable to remove from storage
- **Returns**: Result of the delete operation (success/failure status)
- **Usage**: 
  ```lua
  self:internalStorageRemove("config")
  ```

#### QuickAppBase:internalStorageClear()
Removes all variables from the device's persistent internal storage.

- **Returns**: Result of the clear operation (success/failure status)
- **Usage**: 
  ```lua
  self:internalStorageClear()
  ```

## QuickApp Class

The main QuickApp class, extending QuickAppBase with additional functionality for managing child devices.

### Constructor

#### QuickApp:__init(dev)
Initializes a new main QuickApp instance with the provided device configuration.

- **Parameters**: 
  - `dev` (table): Device object containing device properties, metadata, and configuration
- **Usage**: Called automatically when creating the main QuickApp instance

### Child Device Management

#### QuickApp:initChildDevices(map)
Initializes and sets up child devices for this QuickApp with optional custom class mappings.

- **Parameters**: 
  - `map` (table, optional): Optional mapping table of device types to custom constructor functions
- **Usage**: 
  ```lua
  self:initChildDevices({
    ["com.fibaro.binarySwitch"] = MyChildClass
  })
  ```

#### QuickApp:createChildDevice(options, classRepresentation)
Creates a new child device instance with the specified configuration and optional custom class.

- **Parameters**: 
  - `options` (table): Configuration table containing device setup options
    - `name` (string): Display name for the child device
    - `type` (string): Device type identifier
    - `initialInterfaces` (table, optional): Array of initial interface names
    - `properties` (table, optional): Initial property values
  - `classRepresentation` (function, optional): Optional custom class constructor for the child device
- **Returns**: The newly created child device instance
- **Usage**: 
  ```lua
  local child = self:createChildDevice({
    name = "My Child Device",
    type = "com.fibaro.binarySwitch",
    initialInterfaces = {"turnOn", "turnOff"}
  }, MyChildClass)
  ```

## QuickAppChild Class

The class for child devices, extending QuickAppBase with child-specific functionality and parent relationship management.

### Constructor

#### QuickAppChild:__init(dev)
Initializes a new child device instance with the provided device configuration and parent relationship.

- **Parameters**: 
  - `dev` (table): Device object containing device properties, metadata, and configuration
- **Usage**: Called automatically when creating child device instances

## RefreshStateSubscriber Class

A class for subscribing to and handling refresh state events from the HC3 system, enabling real-time monitoring of device changes.

### Constructor

#### RefreshStateSubscriber:__init()
Initializes a new refresh state subscriber for monitoring HC3 system events.

- **Usage**: 
  ```lua
  local subscriber = RefreshStateSubscriber()
  ```

### Properties

- **time** (number): Timestamp threshold for filtering events (skip events before this time)
- **subscribers** (table): Collection of registered subscribers with their filters and handlers
- **last** (number): Timestamp of the last processed event
- **subject** (table): Event subject for managing refresh state event handling

### Subscription Methods

#### RefreshStateSubscriber:subscribe(filter, handler)
Registers a new subscription to refresh state events with custom filtering and handling logic.

- **Parameters**: 
  - `filter` (function): Function that determines which events to handle (return true to process)
  - `handler` (function): Function to execute when matching events are received
- **Returns**: Subscription object that can be used to unsubscribe later
- **Usage**: 
  ```lua
  local subscription = subscriber:subscribe(
    function(event) return event.type == "DevicePropertyUpdatedEvent" end,
    function(event) print("Device updated:", event.id) end
  )
  ```

#### RefreshStateSubscriber:unsubscribe(subscription)
Removes a previously registered subscription from the refresh state subscriber.

- **Parameters**: 
  - `subscription`: The subscription object to remove (returned from subscribe method)
- **Usage**: 
  ```lua
  subscriber:unsubscribe(subscription)
  ```

#### RefreshStateSubscriber:run()
Starts the refresh state subscriber and begins processing events from the HC3 system.

- **Usage**: 
  ```lua
  subscriber:run()
  ```

#### RefreshStateSubscriber:stop()
Stops the refresh state subscriber and ceases event processing.

- **Usage**: 
  ```lua
  subscriber:stop()
  ```

## Global Event Handlers

### onAction(id, event)
Global event handler that routes device actions to the appropriate QuickApp or child device instance.

- **Parameters**: 
  - `id` (number): The device ID where the action was triggered
  - `event` (table): Event object containing action details and parameters
- **Usage**: Called automatically by the system when device actions are triggered

### onUIEvent(id, event)
Global event handler that routes UI events to the appropriate QuickApp callback functions.

- **Parameters**: 
  - `id` (number): The device ID where the UI event occurred
  - `event` (table): Event object containing UI event details and element information
- **Usage**: Called automatically by the system when UI events occur

## Usage Examples

### Basic QuickApp Structure

```lua
class 'MyQuickApp'(QuickApp)

function MyQuickApp:__init(dev)
  QuickApp.__init(self, dev)
  self:debug("MyQuickApp initialized")
end

function MyQuickApp:onInit()
  self:debug("onInit called")
  self:setupUICallbacks()
  
  -- Set up a variable
  self:setVariable("counter", "0")
  
  -- Create a child device
  local child = self:createChildDevice({
    name = "Child Switch",
    type = "com.fibaro.binarySwitch"
  })
end

function MyQuickApp:turnOn()
  self:debug("Turning on")
  self:updateProperty("state", true)
  self:updateView("statusLabel", "text", "ON")
end

function MyQuickApp:turnOff()
  self:debug("Turning off")
  self:updateProperty("state", false)
  self:updateView("statusLabel", "text", "OFF")
end
```

### Child Device Implementation

```lua
class 'MyChildDevice'(QuickAppChild)

function MyChildDevice:__init(dev)
  QuickAppChild.__init(self, dev)
  self:debug("Child device initialized:", self.name)
end

function MyChildDevice:turnOn()
  self:debug("Child turning on")
  self:updateProperty("state", true)
  -- Notify parent
  self.parent:debug("Child", self.id, "turned on")
end

function MyChildDevice:turnOff()
  self:debug("Child turning off")
  self:updateProperty("state", false)
end
```

### UI Callback Setup

```lua
function MyQuickApp:onInit()
  -- Register UI callbacks
  self:registerUICallback("powerButton", "onReleased", function(event)
    if self:getVariable("state") == "on" then
      self:turnOff()
    else
      self:turnOn()
    end
  end)
  
  self:registerUICallback("slider", "onChanged", function(event)
    local value = event.values[1]
    self:updateProperty("value", value)
    self:debug("Slider changed to:", value)
  end)
end
```

### RefreshState Monitoring

```lua
function MyQuickApp:onInit()
  -- Monitor device property changes
  local subscriber = RefreshStateSubscriber()
  
  subscriber:subscribe(
    function(event) 
      return event.type == "DevicePropertyUpdatedEvent" and 
             event.id == self.id 
    end,
    function(event)
      self:debug("Property updated:", event.property, "=", event.newValue)
    end
  )
  
  subscriber:run()
end
```

### Internal Storage Usage

```lua
function MyQuickApp:onInit()
  -- Load configuration from storage
  local config = self:internalStorageGet("config")
  if not config then
    -- Set default configuration
    config = {
      polling_interval = 60,
      auto_update = true
    }
    self:internalStorageSet("config", config)
  end
  
  self.config = config
  self:debug("Loaded config:", json.encode(config))
end

function MyQuickApp:updateConfig(newConfig)
  self.config = newConfig
  self:internalStorageSet("config", newConfig)
  self:debug("Config updated")
end
```

This documentation covers all the main QuickApp classes and methods available in the plua Fibaro emulation environment for developing sophisticated QuickApp plugins with proper device management, UI interaction, and event handling.
