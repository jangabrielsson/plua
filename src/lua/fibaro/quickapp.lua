-- @module fibaro.quickapp
---@description QuickApp core functionality for Plua
---@author Jan Gabrielsson
---@license MIT
---
---This module provides the QuickApp base class and related utilities:
---- QuickApp lifecycle management
---- Device and UI interaction
---- Logging and event handling

local fmt = string.format

function class(name)
  local cls = setmetatable({__USERDATA=true}, {
    __call = function(t,...)
      assert(rawget(t,'__init'),"No constructor")
      local obj = {__USERDATA=true}
      setmetatable(obj,{__index=t, __tostring = t.__tostring or function() return "object "..name end})
      obj:__init(...)
      return obj
    end,
    __tostring = function() return "class "..name end,
  })
  cls.__org = cls
  _ENV[name] = cls
  return function(p) getmetatable(cls).__index = p end
end

local function printErr(...) fibaro.error(__TAG,...) end

local qaTimers = {}

local function timerErr(ref) return function(...) qaTimers[ref]= nil printErr(...) end end

local mobdebug = require("mobdebug")
fibaro.plua = fibaro.plua or {}

local oldSetTimeout = setTimeout
function setTimeout(func,ms)
  local ref
  ref = oldSetTimeout(function() 
    _PY.mobdebug.on()
    qaTimers[ref]= nil 
    fibaro.plua.lib.prettyCall(func,timerErr(ref)) 
  end,ms)
  qaTimers[ref]= 'timer'
  return ref
end

local oldSetInterval = setInterval
function setInterval(func,ms)
  local ref
  ref =oldSetInterval(function()
    _PY.mobdebug.on()
    local ok = fibaro.plua.lib.prettyCall(func,timerErr(ref))
    if not ok then clearInterval(ref) end
  end,ms)
  qaTimers[ref]= 'interv'
  return ref
end

plugin = plugin or {}
plugin._timers = qaTimers -- So api/plugins/restart can clear timers

-- Retrieves a device by its ID
-- @param deviceId - The ID of the device to retrieve
-- @return Device object from the HC3 API
function plugin.getDevice(deviceId) return api.get("/devices/"..deviceId) end

-- Deletes a device by its ID
-- @param deviceId - The ID of the device to delete
-- @return Result of the delete operation
function plugin.deleteDevice(deviceId) return api.delete("/devices/"..deviceId) end

-- Gets a specific property of a device
-- @param deviceId - The ID of the device
-- @param propertyName - The name of the property to retrieve
-- @return The property value
function plugin.getProperty(deviceId, propertyName) return api.get("/devices/"..deviceId).properties[propertyName] end

-- Gets all child devices of a parent device
-- @param deviceId - The ID of the parent device
-- @return Array of child device objects
function plugin.getChildDevices(deviceId) return api.get("/devices?parentId="..deviceId) end

-- Creates a new child device
-- @param opts - Options for creating the child device
-- @return The created child device object
function plugin.createChildDevice(opts) return api.post("/plugins/createChildDevice", opts) end

-- Restarts a QuickApp plugin
-- @param id - The device ID to restart (optional, defaults to mainDeviceId)
-- @return Result of the restart operation
function plugin.restart(id) return api.post("/plugins/restart",{deviceId=id or plugin.mainDeviceId}) end

class 'QuickAppBase'
-- Constructor for QuickAppBase class
-- @param dev - Device object containing device properties and metadata
function QuickAppBase:__init(dev)
  self.id = dev.id
  self.type = dev.type
  self.name = dev.name
  self.enabled = dev.enabled
  self.parentId = dev.parentId
  self.roomID = dev.roomID
  self.properties = dev.properties
  self.interfaces = dev.interfaces
  self.properties = table.copy(dev.properties)
  self.uiCallbacks = {}
  fibaro.plua:registerQAGlobally(self) -- Register this QuickApp globally
end

-- Logs a debug message with the device tag
-- @param ... - Arguments to be logged
function QuickAppBase:debug(...) fibaro.debug(__TAG,...) end

-- Logs a trace message with the device tag
-- @param ... - Arguments to be logged
function QuickAppBase:trace(...) fibaro.trace(__TAG,...) end

-- Logs a warning message with the device tag
-- @param ... - Arguments to be logged
function QuickAppBase:warning(...) fibaro.warning(__TAG,...) end

-- Logs an error message with the device tag
-- @param ... - Arguments to be logged
function QuickAppBase:error(...) fibaro.error(__TAG,...) end

-- Registers a UI callback function for a specific element and event type
-- @param elm - The UI element name
-- @param typ - The event type (e.g., "onReleased", "onChanged")
-- @param fun - The callback function to register
function QuickAppBase:registerUICallback(elm, typ, fun)
  local uic = self.uiCallbacks
  uic[elm] = uic[elm] or {}
  uic[elm][typ] = fun
end

-- Sets up UI callbacks based on device properties
-- Reads uiCallbacks from device properties and registers them
function QuickAppBase:setupUICallbacks()
  local callbacks = (self.properties or {}).uiCallbacks or {}
  for _, elm in pairs(callbacks) do
    self:registerUICallback(elm.name, elm.eventType, elm.callback)
  end
end

QuickAppBase.registerUICallbacks = QuickAppBase.setupUICallbacks

-- Calls an action method on the QuickApp if it exists
-- @param name - The name of the action/method to call
-- @param ... - Arguments to pass to the action method
-- @return Result of the action method or nil if method doesn't exist
function QuickAppBase:callAction(name, ...)
  --if name == "" then return end
  local args = {...}
  local stat,res = fibaro.plua.lib.prettyCall(function()
    if (type(self[name]) == 'function') then return self[name](self, table.unpack(args))
    else print(fmt("[WARNING] Class does not have '%s' function defined - action ignored",tostring(name))) end
  end,printErr)
  if not stat then
    self:error(fmt("Error calling action %s: %s",name,res))
  end
end

-- Updates a device property and sends the update to the HC3 system
-- @param name - The name of the property to update
-- @param value - The new value for the property
function QuickAppBase:updateProperty(name,value)
  self.properties[name] = value
  api.post("/plugins/updateProperty",{
    deviceId=self.id,
    propertyName=name,
    value=table.copy(value)
  })
end

-- Updates a UI view element property
-- @param elm - The UI element name
-- @param prop - The property name to update
-- @param value - The new value for the property
function QuickAppBase:updateView(elm,prop,value)
  api.post("/plugins/updateView", {
    deviceId = self.id,
    componentName = elm,
    propertyName = prop,
    newValue = value
  })
end

-- Checks if the device has a specific interface
-- @param name - The interface name to check for
-- @return True if the device has the interface, false otherwise
function QuickAppBase:hasInterface(name) return table.member(name, self.interfaces) end

-- Adds new interfaces to the device
-- @param values - Table of interface names to add
function QuickAppBase:addInterfaces(values)
  assert(type(values) == "table")
  self:updateInterfaces("add",values)
  for _, v in pairs(values) do
    table.insert(self.interfaces, v)
  end
end

-- Removes interfaces from the device
-- @param values - Table of interface names to remove
function QuickAppBase:deleteInterfaces(values)
  assert(type(values) == "table")
  self:updateInterfaces("delete", values)
  for _, value in pairs(values) do
    for key, interface in pairs(self.interfaces) do
      if interface == value then
        table.remove(self.interfaces, key)
        break
      end
    end
  end
end

-- Updates device interfaces via API call
-- @param action - The action to perform ("add" or "delete")
-- @param interfaces - Table of interfaces to add or remove
function QuickAppBase:updateInterfaces(action, interfaces)
  api.post("/plugins/interfaces", {action = action, deviceId = self.id, interfaces = interfaces})
end

-- Sets the device name
-- @param name - The new name for the device
function QuickAppBase:setName(name) api.put("/devices/"..self.id,{name=name}) end

-- Sets the device enabled state
-- @param enabled - Boolean indicating if device should be enabled
function QuickAppBase:setEnabled(enabled) api.put("/devices/"..self.id,{enabled=enabled}) end

-- Sets the device visibility
-- @param visible - Boolean indicating if device should be visible
function QuickAppBase:setVisible(visible) api.put("/devices/"..self.id,{visible=visible}) end

-- Sets a QuickApp variable value
-- @param name - The variable name
-- @param value - The variable value
function QuickAppBase:setVariable(name, value)
  local qvars,found = self.properties.quickAppVariables,false
  for _,v in ipairs(qvars) do
    if v.name == name then
      v.value = value
      found = true
      break
    end
  end
  if not found then
    table.insert(qvars, {name=name, value=value})
  end
  self:updateProperty("quickAppVariables", qvars)
end

-- Gets a QuickApp variable value
-- @param name - The variable name
-- @return The variable value or empty string if not found
function QuickAppBase:getVariable(name)
  local qvars = self.properties.quickAppVariables
  for _,v in ipairs(qvars) do
    if v.name == name then
      return v.value
    end
  end
  return ""
end

-- Sets a value in internal storage
-- @param key - The storage key
-- @param val - The value to store
-- @param hidden - Boolean indicating if the variable should be hidden
-- @return HTTP status code
function QuickAppBase:internalStorageSet(key, val, hidden)
  __assert_type(key, 'string')
  local data = { name = key, value = val, isHidden = hidden }
  local _, stat = api.put("/plugins/" .. self.id .. "/variables/" .. key, data)
  --print(key,stat)
  if stat > 206 then
    local _, stat = api.post("/plugins/" .. self.id .. "/variables", data)
    --print(key,stat)
    return stat
  end
end

-- Gets a value from internal storage
-- @param key - The storage key (optional, if nil returns all variables)
-- @return The stored value or nil if not found
function QuickAppBase:internalStorageGet(key)
  __assert_type(key, 'string')
  if key then
    local res, stat = api.get("/plugins/" .. self.id .. "/variables/" .. key)
    if stat ~= 200 then return nil end
    return res.value
  else
    local res, stat = api.get("/plugins/" .. self.id .. "/variables")
    if stat ~= 200 then return nil end
    local values = {}
    for _, v in pairs(res) do values[v.name] = v.value end
    return values
  end
end

-- Removes a variable from internal storage
-- @param key - The storage key to remove
-- @return Result of the delete operation
function QuickAppBase:internalStorageRemove(key) return api.delete("/plugins/" .. self.id .. "/variables/" .. key) end

-- Clears all variables from internal storage
-- @return Result of the delete operation
function QuickAppBase:internalStorageClear() return api.delete("/plugins/" .. self.id .. "/variables") end

class 'QuickApp'(QuickAppBase)
-- Constructor for QuickApp class (main QuickApp instance)
-- @param dev - Device object containing device properties and metadata
function QuickApp:__init(dev)
  __TAG = dev.name..dev.id
  plugin.mainQA = self
  QuickAppBase.__init(self, dev)
  self.childDevices = {}
  self.childsInitialized = false
  self:setupUICallbacks()
  if self.onInit then self:onInit() end
  if not self.childsInitialized then self:initChildDevices() end
end

-- Initializes child devices for this QuickApp
-- @param map - Optional mapping table of device types to constructor functions
---@diagnostic disable-next-line: duplicate-set-field
function QuickApp:initChildDevices(map)
  map = map or {}
  local children = api.get("/devices?parentId="..self.id)
  local childDevices = self.childDevices
  for _, c in pairs(children) do
    if childDevices[c.id] == nil and map[c.type] then
      childDevices[c.id] = map[c.type](c)
    elseif childDevices[c.id] == nil then
      self:error(fmt("Class for the child device: %s, with type: %s not found. Using base class: QuickAppChild", c.id, c.type))
      childDevices[c.id] = QuickAppChild(c)
    end
    ---@diagnostic disable-next-line: inject-field
    childDevices[c.id].parent = self
  end
  self.childsInitialized = true
end

-- Creates a new child device for this QuickApp
-- @param options - Options table containing device configuration
-- @param classRepresentation - Optional class constructor for the child device
-- @return The created child device instance
function QuickApp:createChildDevice(options, classRepresentation)
  __assert_type(options, "table")
  __assert_type(options.name, "string")
  __assert_type(options.type, "string")
  options.parentId = self.id
  if options.initialInterfaces then
    __assert_type(options.initialInterfaces, "table")
    table.insert(options.initialInterfaces, "quickAppChild")
  else
    options.initialInterfaces = {"quickAppChild"}
  end
  if options.initialProperties then
    __assert_type(options.initialProperties, "table")
  end
  local child = api.post("/plugins/createChildDevice", options)
  if classRepresentation == nil then
    classRepresentation = QuickAppChild
  end
  self.childDevices[child.id] = classRepresentation(child)
  ---@diagnostic disable-next-line: inject-field
  self.childDevices[child.id].parent = self
  
  return self.childDevices[child.id]
end

class 'QuickAppChild'(QuickAppBase)
-- Constructor for QuickAppChild class (child device of a QuickApp)
-- @param dev - Device object containing device properties and metadata
function QuickAppChild:__init(dev)
  QuickAppBase.__init(self, dev)
  self.parentId = dev.parentId
  if self.onInit then self:onInit() end
end

-- Global handler for device actions
-- Routes actions to the appropriate QuickApp or child device
-- @param id - Device ID where the action was called
-- @param event - Event object containing action details
function onAction(id,event) -- { deviceID = 1234, actionName = "test", args = {1,2,3} }
  --if Emu:DBGFLAG('onAction') then print("onAction: ", json.encode(event)) end
  setTimeout(function()
  local self = plugin.mainQA
  ---@diagnostic disable-next-line: undefined-field
  if self.actionHandler then return self:actionHandler(event) end
  if event.deviceId == self.id then
    return self:callAction(event.actionName, table.unpack(event.args or {}))
  elseif self.childDevices[event.deviceId] then
    return self.childDevices[event.deviceId]:callAction(event.actionName, table.unpack(event.args or {}))
  end
  self:error(fmt("Child with id:%s not found",id))
end,0)
end

-- Global handler for UI events
-- Routes UI events to the appropriate QuickApp callbacks
-- @param id - Device ID where the UI event occurred
-- @param event - Event object containing UI event details
function onUIEvent(id, event)
  local quickApp = plugin.mainQA
  --print("onUIEvent",json.encode(event))
  --if Emu:DBGFLAG('onUIEvent') then print("UIEvent: ", json.encode(event)) end
  ---@diagnostic disable-next-line: undefined-field
  if quickApp.UIHandler then quickApp:UIHandler(event) return end
  if quickApp.uiCallbacks[event.elementName] and quickApp.uiCallbacks[event.elementName][event.eventType] then
    local action = quickApp.uiCallbacks[event.elementName][event.eventType]
    if action == "" then
      fibaro.warning(__TAG,fmt("UI callback for %s %s not found.", event.elementName, event.eventType))
      return
    end
    setTimeout(function() quickApp:callAction(action, event) end,0)
  else
    fibaro.warning(__TAG,fmt("UI callback for element %s not found.", event.elementName))
  end
end

-- Programmatically triggers a UI action for testing purposes
-- @param eventType - The type of UI event to trigger
-- @param elementName - The name of the UI element
-- @param arg - Optional argument value for the event
function QuickAppBase:UIAction(eventType, elementName, arg)
  local event = {
    deviceId = self.id,
    eventType = eventType,
    elementName = elementName
  }
  event.values = arg ~= nil and  { arg } or json.util.InitArray({})
  onUIEvent(self.id, event)
end

---@class RefreshStateSubscriber
---@field time number - Time to skip events before this timestamp
---@field subscribers table - Table of subscribers with their filters and handlers
---@field last number - Last processed event timestamp
---@field subject table - Subject for handling refresh state events
RefreshStateSubscriber = {}
class 'RefreshStateSubscriber'

-- Constructor for RefreshStateSubscriber class
-- Initializes the subscriber for refresh state events
function RefreshStateSubscriber:__init()
  self.time = os.time() -- Skip events before this time
  self.subscribers = {}
  self.last = 0
  function self.handle(event)
    event.created = event.created or os.time()
    if self.time > event.created+2 then return end -- Allow for 2 seconds mismatch between emulator and HC3
    for sub,_ in pairs(self.subscribers) do
      if sub.filter(event) then pcall(sub.handler,event) end
    end
  end
end

-- Subscribes to refresh state events with a filter and handler
-- @param filter - Function to filter events (return true to handle)
-- @param handler - Function to handle matching events
-- @return Subscription object
function RefreshStateSubscriber:subscribe(filter, handler)
  return self.subject:filter(function(event) return filter(event) end):subscribe(function(event) handler(event) end)
end

local MTsub = { __tostring = function(self) return "Subscription" end }

local SUBTYPE = '%SUBSCRIPTION%'
-- Subscribes to refresh state events with a filter and handler (alternative implementation)
-- @param filter - Function to filter events (return true to handle)
-- @param handler - Function to handle matching events
-- @return Subscription object
function RefreshStateSubscriber:subscribe(filter, handler)
  local sub = setmetatable({ type=SUBTYPE, filter = filter, handler = handler },MTsub)
  self.subscribers[sub]=true
  return sub
end

-- Unsubscribes from refresh state events
-- @param subscription - The subscription object to remove
function RefreshStateSubscriber:unsubscribe(subscription)
  if type(subscription)=='table' and subscription.type==SUBTYPE then
    self.subscribers[subscription]=nil
  end
end

local listeners = {}

-- Starts the refresh state subscriber
---@diagnostic disable-next-line: undefined-field
function RefreshStateSubscriber:run()
  function _PY.newRefreshStatesEvent(jsonevent)
  --print("New jsonevent",jsonevent) -- jsonevent)
  local event = json.decode(jsonevent)
  for l,_ in pairs(listeners) do
    pcall(l,event)
  end
end
  fibaro.plua:startRefreshStatesPolling()
  listeners[self.handle] = true
end

-- Stops the refresh state subscriber
---@diagnostic disable-next-line: undefined-field
function RefreshStateSubscriber:stop() 
  listeners[self.handle] = nil
end
