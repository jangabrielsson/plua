# HC3 REST API — Device Management

Full reference for Devices (28), Plugins (18), QuickApp (11), and Additional Interfaces (2) endpoints.

---

## Devices (28 endpoints)

### Core Device Operations
- `GET /api/devices` — List all devices; supports filtering:
  - `?name=MyQuickApp`
  - `?interface=quickApp`
  - `?type=com.fibaro.binarySwitch`
  - `?roomID=5`
  - `?enabled=true`
- `POST /api/devices` — Create new plugin device (use `POST /api/quickApp` for QuickApps)
  ```json
  { "name": "Device Name", "type": "plugin_device_type", "roomID": 1,
    "properties": { "configured": true, "dead": false } }
  ```
- `GET /api/devices/{deviceID}` — Get device details and all properties
- `PUT /api/devices/{deviceID}` — Modify device configuration
  ```json
  { "name": "Updated Name", "roomID": 2, "enabled": true, "visible": true }
  ```
- `DELETE /api/devices/{deviceID}` — Remove device from system
- `POST /api/devices/filter` — Advanced filtered device list
  ```json
  {
    "filters": [
      { "filter": "roomId", "value": [1, 2, 3] },
      { "filter": "interface", "value": ["zwave", "energy"] }
    ],
    "attributes": { "id": true, "name": true, "roomID": true, "type": true }
  }
  ```

### Device Properties
- `GET /api/devices/{deviceID}/properties` — All device properties
- `GET /api/devices/{deviceID}/properties/{propName}` — Single property value

### Device Actions
- `POST /api/devices/{deviceID}/action/{actionName}` — Execute device action
  ```json
  { "args": [25, "heating"], "delay": 0 }
  ```
  ```lua
  api.post("/devices/42/action/turnOn", {args={}})
  api.post("/devices/42/action/setValue", {args={75}})
  api.post("/devices/344/action/myFun", {args={25, "heating"}})
  ```
- `DELETE /api/devices/action/{timestamp}/{id}` — Cancel delayed action
- `POST /api/devices/groupAction/{actionName}` — Execute action on multiple devices
  ```json
  { "devices": [1, 2, 3], "args": ["turnOn"], "delay": 5 }
  ```

### Interface Management
- `POST /api/devices/addInterface` — Add interfaces to devices
  ```json
  { "devicesId": [1, 2, 3], "interfaces": ["energy", "battery"] }
  ```
- `POST /api/devices/deleteInterface` — Remove interfaces from devices
  ```json
  { "devicesId": [1, 2, 3], "interfaces": ["energy"] }
  ```

### Device Information
- `GET /api/uiDeviceInfo` — Get UI device information with filtering
- `GET /api/devices/hierarchy` — Get device type hierarchy
- `GET /api/devices?property=[lastLoggedUser,{userId}]` — Get mobile devices for user

### Lua Examples
```lua
local dev = api.get("/devices/42")
print(dev.name, dev.type, dev.properties.value)

local switches = api.get("/devices?type=com.fibaro.binarySwitch")
for _, d in ipairs(switches) do print(d.id, d.name) end

local devs = api.get("/devices?roomID=5&enabled=true")
local battery = api.get("/devices?interface=battery")
for _, d in ipairs(battery) do
    local level = tonumber((d.properties or {}).batteryLevel or 100)
    if level < 20 then self:warning("Low battery:", d.name, "(", level, "%)") end
end
```

---

## Plugins (18 endpoints)

### Plugin Management
- `GET /api/plugins` — Get all plugins information
- `GET /api/plugins/installed` — Get installed plugins list
- `POST /api/plugins/installed` — Install plugin (HC2 compatibility; don't use for QuickApps)
- `DELETE /api/plugins/installed` — Uninstall plugin (don't use for QuickApps)
- `GET /api/plugins/types` — Available plugin types
- `GET /api/plugins/ipCameras` — Available IP camera plugins

### UI and Event Handling
- `GET /api/plugins/callUIEvent` — Trigger UI event (query params)
- `POST /api/plugins/callUIEvent` — Trigger UI event (JSON payload)
  ```json
  { "deviceId": 25, "elementName": "button1", "eventType": "onReleased", "value": "clicked" }
  ```
- `GET /api/plugins/getView` — Get plugin view configuration
- `POST /api/plugins/updateView` — Update UI element
  ```json
  { "deviceId": 25, "componentName": "label1", "propertyName": "text", "newValue": "Online" }
  ```

### Property and Interface Management
- `POST /api/plugins/updateProperty` — Update device property (no QA restart; generates system event)
  ```json
  { "deviceId": 25, "propertyName": "value", "value": 75 }
  ```
- `POST /api/plugins/interfaces` — Add or remove device interfaces
  ```json
  { "action": "add", "deviceId": 25, "interfaces": ["energy", "battery"] }
  ```
- `POST /api/plugins/restart` — Restart specific plugin
  ```json
  { "deviceId": 25 }
  ```

### Child Device Support
- `POST /api/plugins/createChildDevice` — Create child device
  ```json
  {
    "parentId": 25, "type": "com.fibaro.binarySwitch", "name": "Channel 2",
    "initialProperties": { "value": false, "dead": false },
    "initialInterfaces": ["zwave"]
  }
  ```

### Event Publishing
- `POST /api/plugins/publishEvent` — Publish event through plugin system
  ```json
  { "eventType": "centralSceneEvent", "source": 25, "data": { "keyId": 1, "keyAttribute": "Pressed" } }
  ```

### Lua Examples
```lua
api.post("/plugins/updateProperty", { deviceId = 42, propertyName = "value", value = 75 })

api.post("/plugins/updateView", {
    deviceId = 42, componentName = "statusLabel",
    propertyName = "text", newValue = "Online"
})

api.post("/plugins/callUIEvent", {
    deviceId = 42, elementName = "myButton",
    eventType = "onReleased", value = "clicked"
})

api.post("/plugins/restart", { deviceId = 42 })

api.post("/plugins/createChildDevice", {
    parentId = self.id, type = "com.fibaro.binarySwitch",
    name = "Channel 2", initialProperties = { value = false }
})
```

---

## QuickApp (11 endpoints)

### QuickApp Creation
- `POST /api/quickApp` — Create new QuickApp device
  ```json
  {
    "name": "My QuickApp", "type": "com.fibaro.generic.device", "roomId": 1,
    "initialProperties": { "userDescription": "Custom description" },
    "initialInterfaces": ["zwave", "energy"]
  }
  ```
- `GET /api/quickApp/availableTypes` — Available QuickApp device types

### File Management
- `GET /api/quickApp/{deviceId}/files` — List source files
- `POST /api/quickApp/{deviceId}/files` — Create new source file
  ```json
  { "name": "utils.lua", "type": "lua", "isOpen": false, "isMain": false }
  ```
- `PUT /api/quickApp/{deviceId}/files` — Update multiple files at once
  ```json
  [
    { "name": "main.lua", "content": "-- main", "isOpen": true },
    { "name": "utils.lua", "content": "-- utils", "isOpen": false }
  ]
  ```
- `GET /api/quickApp/{deviceId}/files/{fileName}` — Get specific file
- `PUT /api/quickApp/{deviceId}/files/{fileName}` — Update specific file
  ```json
  { "name": "main.lua", "type": "lua", "isOpen": true, "isMain": true, "content": "..." }
  ```
- `DELETE /api/quickApp/{deviceId}/files/{fileName}` — Delete source file

### Import/Export
- `GET /api/quickApp/export/{deviceId}` — Export to .fqa file
- `POST /api/quickApp/export/{deviceId}` — Export encrypted .fqax
  ```json
  { "encrypted": true, "serialNumbers": ["HC3-001234"] }
  ```
- `POST /api/quickApp/import` — Import from .fqa/.fqax
  ```json
  { "file": "<base64_fqa_content>", "roomId": 1 }
  ```

### Lua Examples
```lua
local f = api.get("/quickApp/42/files/main")
print(f.content)

api.put("/quickApp/42/files/main", {
    name = "main", type = "lua", isMain = true,
    content = "function QuickApp:onInit() end"
})
```

---

## Additional Interfaces (2 endpoints)

- `GET /api/additionalInterfaces` — List all additional interfaces for device
- `GET /api/additionalInterfaces/{interface}` — Get specific interface details
