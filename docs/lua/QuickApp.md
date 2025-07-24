# QuickApp Documentation

This document covers the QuickApp framework classes and methods available in the plua Fibaro emulation environment for developing QuickApp plugins.

## Plugin Namespace Functions

The `plugin` namespace provides utility functions for device and plugin management.

### plugin.getDevice(deviceId)
Retrieves a device by its ID.
- **Parameters**: 
  - `deviceId` (number): The ID of the device to retrieve
- **Returns**: Device object from the HC3 API
- **Usage**: `local device = plugin.getDevice(123)`

### plugin.deleteDevice(deviceId)
Deletes a device by its ID.
- **Parameters**: 
  - `deviceId` (number): The ID of the device to delete
- **Returns**: Result of the delete operation
- **Usage**: `plugin.deleteDevice(123)`

### plugin.getProperty(deviceId, propertyName)
Gets a specific property of a device.
- **Parameters**: 
  - `deviceId` (number): The ID of the device
  - `propertyName` (string): The name of the property to retrieve
- **Returns**: The property value
- **Usage**: `local value = plugin.getProperty(123, "value")`

### plugin.getChildDevices(deviceId)
Gets all child devices of a parent device.
- **Parameters**: 
  - `deviceId` (number): The ID of the parent device
- **Returns**: Array of child device objects
- **Usage**: `local children = plugin.getChildDevices(123)`

### plugin.createChildDevice(opts)
Creates a new child device.
- **Parameters**: 
  - `opts` (table): Options for creating the child device
- **Returns**: The created child device object
- **Usage**: 
  ```lua
  local child = plugin.createChildDevice({
    name = "Child Device",
    type = "com.fibaro.binarySwitch"
  })
  ```

### plugin.restart(id)
Restarts a QuickApp plugin.
- **Parameters**: 
  - `id` (number, optional): The device ID to restart (defaults to mainDeviceId)
- **Returns**: Result of the restart operation
- **Usage**: `plugin.restart()` or `plugin.restart(123)`

## QuickAppBase Class

The base class for all QuickApp devices, providing core functionality for device management, logging, and UI interaction.

### Constructor

#### QuickAppBase:__init(dev)
Constructor for QuickAppBase class.
- **Parameters**: 
  - `dev` (table): Device object containing device properties and metadata
- **Usage**: Called automatically when creating QuickApp instances

### Logging Methods

#### QuickAppBase:debug(...)
Logs a debug message with the device tag.
- **Parameters**: `...`: Arguments to be logged
- **Usage**: `self:debug("Debug message", value)`

#### QuickAppBase:trace(...)
Logs a trace message with the device tag.
- **Parameters**: `...`: Arguments to be logged
- **Usage**: `self:trace("Trace message")`

#### QuickAppBase:warning(...)
Logs a warning message with the device tag.
- **Parameters**: `...`: Arguments to be logged
- **Usage**: `self:warning("Warning message")`

#### QuickAppBase:error(...)
Logs an error message with the device tag.
- **Parameters**: `...`: Arguments to be logged
- **Usage**: `self:error("Error message")`

### UI Management Methods

#### QuickAppBase:registerUICallback(elm, typ, fun)
Registers a UI callback function for a specific element and event type.
- **Parameters**: 
  - `elm` (string): The UI element name
  - `typ` (string): The event type (e.g., "onReleased", "onChanged")
  - `fun` (function): The callback function to register
- **Usage**: 
  ```lua
  self:registerUICallback("button1", "onReleased", function(event)
    self:debug("Button pressed")
  end)
  ```

#### QuickAppBase:setupUICallbacks()
Sets up UI callbacks based on device properties.
Reads uiCallbacks from device properties and registers them.
- **Usage**: `self:setupUICallbacks()`

#### QuickAppBase:updateView(elm, prop, value)
Updates a UI view element property.
- **Parameters**: 
  - `elm` (string): The UI element name
  - `prop` (string): The property name to update
  - `value`: The new value for the property
- **Usage**: `self:updateView("label1", "text", "New Text")`

#### QuickAppBase:UIAction(eventType, elementName, arg)
Programmatically triggers a UI action for testing purposes.
- **Parameters**: 
  - `eventType` (string): The type of UI event to trigger
  - `elementName` (string): The name of the UI element
  - `arg` (optional): Optional argument value for the event
- **Usage**: `self:UIAction("onReleased", "button1")`

### Device Management Methods

#### QuickAppBase:callAction(name, ...)
Calls an action method on the QuickApp if it exists.
- **Parameters**: 
  - `name` (string): The name of the action/method to call
  - `...`: Arguments to pass to the action method
- **Returns**: Result of the action method or nil if method doesn't exist
- **Usage**: `self:callAction("turnOn")`

#### QuickAppBase:updateProperty(name, value)
Updates a device property and sends the update to the HC3 system.
- **Parameters**: 
  - `name` (string): The name of the property to update
  - `value`: The new value for the property
- **Usage**: `self:updateProperty("value", 75)`

#### QuickAppBase:hasInterface(name)
Checks if the device has a specific interface.
- **Parameters**: 
  - `name` (string): The interface name to check for
- **Returns**: Boolean indicating if the device has the interface
- **Usage**: `local hasDimmer = self:hasInterface("dimmable")`

#### QuickAppBase:addInterfaces(values)
Adds new interfaces to the device.
- **Parameters**: 
  - `values` (table): Table of interface names to add
- **Usage**: `self:addInterfaces({"dimmable", "energy"})`

#### QuickAppBase:deleteInterfaces(values)
Removes interfaces from the device.
- **Parameters**: 
  - `values` (table): Table of interface names to remove
- **Usage**: `self:deleteInterfaces({"energy"})`

#### QuickAppBase:setName(name)
Sets the device name.
- **Parameters**: 
  - `name` (string): The new name for the device
- **Usage**: `self:setName("New Device Name")`

#### QuickAppBase:setEnabled(enabled)
Sets the device enabled state.
- **Parameters**: 
  - `enabled` (boolean): Boolean indicating if device should be enabled
- **Usage**: `self:setEnabled(true)`

#### QuickAppBase:setVisible(visible)
Sets the device visibility.
- **Parameters**: 
  - `visible` (boolean): Boolean indicating if device should be visible
- **Usage**: `self:setVisible(false)`

### Variable Management Methods

#### QuickAppBase:setVariable(name, value)
Sets a QuickApp variable value.
- **Parameters**: 
  - `name` (string): The variable name
  - `value`: The variable value
- **Usage**: `self:setVariable("counter", "5")`

#### QuickAppBase:getVariable(name)
Gets a QuickApp variable value.
- **Parameters**: 
  - `name` (string): The variable name
- **Returns**: The variable value or empty string if not found
- **Usage**: `local counter = self:getVariable("counter")`

### Internal Storage Methods

#### QuickAppBase:internalStorageSet(key, val, hidden)
Sets a value in internal storage.
- **Parameters**: 
  - `key` (string): The storage key
  - `val`: The value to store
  - `hidden` (boolean, optional): Boolean indicating if the variable should be hidden
- **Returns**: HTTP status code
- **Usage**: `self:internalStorageSet("config", {param1 = "value"})`

#### QuickAppBase:internalStorageGet(key)
Gets a value from internal storage.
- **Parameters**: 
  - `key` (string, optional): The storage key (if nil returns all variables)
- **Returns**: The stored value or nil if not found
- **Usage**: 
  ```lua
  local config = self:internalStorageGet("config")
  local allVars = self:internalStorageGet() -- Get all variables
  ```

#### QuickAppBase:internalStorageRemove(key)
Removes a variable from internal storage.
- **Parameters**: 
  - `key` (string): The storage key to remove
- **Returns**: Result of the delete operation
- **Usage**: `self:internalStorageRemove("config")`

#### QuickAppBase:internalStorageClear()
Clears all variables from internal storage.
- **Returns**: Result of the delete operation
- **Usage**: `self:internalStorageClear()`

## QuickApp Class

The main QuickApp class, extending QuickAppBase with additional functionality for managing child devices.

### Constructor

#### QuickApp:__init(dev)
Constructor for QuickApp class (main QuickApp instance).
- **Parameters**: 
  - `dev` (table): Device object containing device properties and metadata
- **Usage**: Called automatically when creating the main QuickApp instance

### Child Device Management

#### QuickApp:initChildDevices(map)
Initializes child devices for this QuickApp.
- **Parameters**: 
  - `map` (table, optional): Optional mapping table of device types to constructor functions
- **Usage**: 
  ```lua
  self:initChildDevices({
    ["com.fibaro.binarySwitch"] = MyChildClass
  })
  ```

#### QuickApp:createChildDevice(options, classRepresentation)
Creates a new child device for this QuickApp.
- **Parameters**: 
  - `options` (table): Options table containing device configuration
  - `classRepresentation` (function, optional): Optional class constructor for the child device
- **Returns**: The created child device instance
- **Usage**: 
  ```lua
  local child = self:createChildDevice({
    name = "My Child Device",
    type = "com.fibaro.binarySwitch",
    initialInterfaces = {"turnOn", "turnOff"}
  }, MyChildClass)
  ```

## QuickAppChild Class

The class for child devices, extending QuickAppBase with child-specific functionality.

### Constructor

#### QuickAppChild:__init(dev)
Constructor for QuickAppChild class (child device of a QuickApp).
- **Parameters**: 
  - `dev` (table): Device object containing device properties and metadata
- **Usage**: Called automatically when creating child device instances

## RefreshStateSubscriber Class

A class for subscribing to and handling refresh state events from the HC3 system.

### Constructor

#### RefreshStateSubscriber:__init()
Constructor for RefreshStateSubscriber class.
Initializes the subscriber for refresh state events.
- **Usage**: `local subscriber = RefreshStateSubscriber()`

### Properties

- **time** (number): Time to skip events before this timestamp
- **subscribers** (table): Table of subscribers with their filters and handlers
- **last** (number): Last processed event timestamp
- **subject** (table): Subject for handling refresh state events

### Subscription Methods

#### RefreshStateSubscriber:subscribe(filter, handler)
Subscribes to refresh state events with a filter and handler.
- **Parameters**: 
  - `filter` (function): Function to filter events (return true to handle)
  - `handler` (function): Function to handle matching events
- **Returns**: Subscription object
- **Usage**: 
  ```lua
  local subscription = subscriber:subscribe(
    function(event) return event.type == "DevicePropertyUpdatedEvent" end,
    function(event) print("Device updated:", event.id) end
  )
  ```

#### RefreshStateSubscriber:unsubscribe(subscription)
Unsubscribes from refresh state events.
- **Parameters**: 
  - `subscription`: The subscription object to remove
- **Usage**: `subscriber:unsubscribe(subscription)`

#### RefreshStateSubscriber:run()
Starts the refresh state subscriber.
- **Usage**: `subscriber:run()`

#### RefreshStateSubscriber:stop()
Stops the refresh state subscriber.
- **Usage**: `subscriber:stop()`

## Global Event Handlers

### onAction(id, event)
Global handler for device actions. Routes actions to the appropriate QuickApp or child device.
- **Parameters**: 
  - `id` (number): Device ID where the action was called
  - `event` (table): Event object containing action details
- **Usage**: Called automatically by the system when device actions are triggered

### onUIEvent(id, event)
Global handler for UI events. Routes UI events to the appropriate QuickApp callbacks.
- **Parameters**: 
  - `id` (number): Device ID where the UI event occurred
  - `event` (table): Event object containing UI event details
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
