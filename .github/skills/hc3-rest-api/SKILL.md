---
name: hc3-rest-api
description: HC3 REST API reference: quick-reference for the most-used ~60 endpoints inline, plus full 269-endpoint coverage via assets/ subdirectory (5 files grouped by category: devices, scenes-automation, energy-climate, system, misc). Includes Lua api.* examples for each endpoint. USE FOR: calling HC3 REST endpoints from QA code or externally, understanding request/response shapes, filtering devices, triggering scenes or events. Ask the agent to read a specific asset file for deep coverage of any category.
---

# HC3 REST API Reference

Condensed reference for the most-used Fibaro HC3 REST API endpoints. In QuickApp code, use `api.get/post/put/delete(path, body)` for synchronous calls. For async HTTP, use `net.HTTPClient`.

---

## Querying the live HC3 from the terminal

Use `plua --fibaro -e "..."` to run one-off API queries against the real HC3 without writing a script. Credentials are taken from plua's existing HC3 configuration.

Two patterns for handling `api.get`'s two return values (data, httpStatus):

```bash
# Pattern 1: ((...)) — discard HTTP status, clean JSON output
plua --fibaro --nodebugger -e "json.encodeFormated((api.get('/devices/45')))"

# Pattern 2: {...} — include HTTP status as second element (useful for debugging)
plua --fibaro --nodebugger -e "json.encodeFormated({api.get('/devices/45')})"
# Output: [ <data>, 200 ]
```

Use Pattern 2 when you want to confirm the endpoint succeeded (status 200) vs returned an error.

```bash
# List all QuickApps
plua --fibaro --nodebugger -e "json.encodeFormated((api.get('/devices?interface=quickApp')))"

# List all devices of a specific type
plua --fibaro --nodebugger -e "json.encodeFormated((api.get('/devices?type=com.fibaro.binarySwitch')))"

# Get a specific device property
plua --fibaro --nodebugger -e "json.encodeFormated((api.get('/devices/45/properties/value')))"

# Get all QA variables for device 45
plua --fibaro --nodebugger -e "json.encodeFormated((api.get('/plugins/45/variables')))"

# Get a global variable
plua --fibaro --nodebugger -e "json.encodeFormated((api.get('/globalVariables/myVar')))"

# Energy consumption summary (period is a date: YYYY-MM-DD)
plua --fibaro --nodebugger -e "json.encodeFormated({api.get('/energy/consumption/summary?period=2026-03-27')})"

# List all rooms
plua --fibaro --nodebugger -e "json.encodeFormated((api.get('/rooms')))"

# List all scenes
plua --fibaro --nodebugger -e "json.encodeFormated((api.get('/scenes')))"
```

Use this to inspect real device structures before writing code that reads or updates them.

---

## Devices

### Read
```
GET  /api/devices                              -- all devices
GET  /api/devices?interface=quickApp           -- filter by interface
GET  /api/devices?type=com.fibaro.binarySwitch -- filter by type
GET  /api/devices?roomID=5                     -- filter by room
GET  /api/devices/{id}                         -- single device
GET  /api/devices/{id}/properties             -- all properties
GET  /api/devices/{id}/properties/{propName}  -- one property
```

Lua examples:
```lua
local dev = api.get("/devices/42")
print(dev.name, dev.type, dev.properties.value)

local switches = api.get("/devices?type=com.fibaro.binarySwitch")
for _, d in ipairs(switches) do print(d.id, d.name) end
```

### Control
```
POST /api/devices/{id}/action/{actionName}
```
Body: `{"args": [...], "delay": 0}`

```lua
api.post("/devices/42/action/turnOn", {args={}})
api.post("/devices/42/action/setValue", {args={75}})
api.post("/devices/344/action/myFun", {args={25, "heating"}})
```

### Modify / Delete
```
PUT    /api/devices/{id}
DELETE /api/devices/{id}
```
```lua
api.put("/devices/42", { name = "Living Room Light", roomID = 3 })
```

---

## Plugins (QuickApp runtime)

```
POST /api/plugins/updateProperty     -- update property without QA restart
POST /api/plugins/updateView         -- update UI element
POST /api/plugins/callUIEvent        -- trigger a UI callback
POST /api/plugins/createChildDevice  -- create child device
POST /api/plugins/restart            -- restart a plugin/QA
POST /api/plugins/publishEvent       -- publish event to plugin
POST /api/plugins/interfaces         -- add or remove interfaces
```

```lua
api.post("/plugins/updateProperty", {
    deviceId = 42, propertyName = "value", value = 75
})

api.post("/plugins/updateView", {
    deviceId = 42, componentName = "statusLabel",
    propertyName = "text", newValue = "Online"
})

api.post("/plugins/callUIEvent", {
    deviceId = 42, elementName = "myButton",
    eventType = "onReleased", value = "clicked"
})

api.post("/plugins/restart", { deviceId = 42 })
```

---

## QuickApp Files

```
GET    /api/quickApp/{id}/files          -- list source files
GET    /api/quickApp/{id}/files/{name}   -- get specific file
PUT    /api/quickApp/{id}/files/{name}   -- update file
PUT    /api/quickApp/{id}/files          -- update multiple files
DELETE /api/quickApp/{id}/files/{name}
GET    /api/quickApp/export/{id}         -- export to .fqa
POST   /api/quickApp/import             -- import from .fqa
POST   /api/quickApp                    -- create new QuickApp
```

```lua
local f = api.get("/quickApp/42/files/main")
print(f.content)

api.put("/quickApp/42/files/main", {
    name = "main", type = "lua", isMain = true,
    content = "function QuickApp:onInit() end"
})
```

---

## Global Variables

```
GET    /api/globalVariables        -- all
GET    /api/globalVariables/{name} -- one: {name, value, modified}
POST   /api/globalVariables        -- create
PUT    /api/globalVariables/{name} -- update
DELETE /api/globalVariables/{name}
```

```lua
local gv = api.get("/globalVariables/HomeMode")
print(gv.value)
api.put("/globalVariables/HomeMode", { value = "Away" })

-- Prefer fibaro API from within a QA:
local mode = fibaro.getGlobalVariable("HomeMode")
fibaro.setGlobalVariable("HomeMode", "Away")
```

---

## Custom Events

```
GET    /api/customEvents           -- list all
POST   /api/customEvents           -- create: {name, userDescription}
POST   /api/customEvents/{name}    -- trigger event
DELETE /api/customEvents/{name}
```

```lua
api.post("/customEvents/MotionAlert", {})
-- or from Lua:
fibaro.emitCustomEvent("MotionAlert")
```

---

## Scenes

```
GET  /api/scenes                      -- all scenes
POST /api/scenes/{id}/execute         -- run async
POST /api/scenes/{id}/executeSync     -- run and wait
POST /api/scenes/{id}/kill            -- stop: {"force": true}
POST /api/scenes                      -- create
PUT  /api/scenes/{id}                 -- update
DELETE /api/scenes/{id}
```

```lua
api.post("/scenes/10/execute", {})
api.post("/scenes/10/kill", { force = true })
-- or:
fibaro.scene("execute", 10)
fibaro.scene("kill", 10)
```

---

## Alarm Partitions

```
GET  /api/alarms/v1/partitions
POST /api/alarms/v1/partitions/{id}/actions   -- arm/disarm/breach
```

```lua
api.post("/alarms/v1/partitions/1/actions", { type = "arm" })
fibaro.alarm(1, "arm")
fibaro.alarm(1, "disarm")
```

---

## Rooms and Sections

```
GET  /api/rooms
GET  /api/rooms/{id}
POST /api/rooms          -- create: {name, sectionID, icon}
PUT  /api/rooms/{id}
DELETE /api/rooms/{id}
GET  /api/sections
```

---

## Profiles

```
GET  /api/profiles
POST /api/profiles/activeProfile/{id}   -- activate
```

```lua
fibaro.profile(3, "activateProfile")
api.post("/profiles/activeProfile/3", {})
```

---

## Refresh States (Event Polling)

```
GET /api/refreshStates?last={lastKnown}
```

Response:
```json
{
  "last": 12345,
  "changes": [
    { "id": 42, "name": "value", "newValue": true, "oldValue": false }
  ],
  "events": [
    { "type": "CustomEvent", "data": { "name": "myEvent" } }
  ]
}
```

```lua
local data = api.get("/refreshStates?last=" .. self.lastRefresh)
self.lastRefresh = data.last
for _, change in ipairs(data.changes or {}) do
    self:debug(change.id, change.name, "->", tostring(change.newValue))
end
```

---

## Device Filtering — Common Patterns

```lua
local devs    = api.get("/devices?roomID=5&enabled=true")
local pirs    = api.get("/devices?type=com.fibaro.motionSensor")
local battery = api.get("/devices?interface=battery")

-- Check low battery
for _, d in ipairs(battery) do
    local level = tonumber((d.properties or {}).batteryLevel or 100)
    if level < 20 then
        self:warning("Low battery:", d.name, "(", level, "%)")
    end
end

-- Advanced POST filter (multiple criteria)
local result = api.post("/devices/filter", {
    filters = {
        { filter = "roomId",    value = {1, 2} },
        { filter = "interface", value = {"energy"} }
    },
    attributes = { id = true, name = true, type = true }
})
```

---

## Weather

```
GET /api/weather
```
Fields: `Temperature`, `Humidity`, `Wind`, `WeatherCondition`, `ConditionCode`.

---

## Debug Messages

```
GET    /api/debugMessages   -- recent log entries
POST   /api/debugMessages   -- add entry
DELETE /api/debugMessages   -- clear
```

---

## Full Endpoint Reference

Detailed coverage of all 269 HC3 REST endpoints is in the `assets/` subdirectory alongside this skill. These files are distributed with the `/install-qa-skills` installer and available in any workspace that has installed the skills.

Ask the agent to read the relevant file when you need deeper coverage:

| File | Contents | Endpoints |
|------|----------|-----------|
| `.github/skills/hc3-rest-api/assets/devices.md` | Devices, Plugins, QuickApp files, Interfaces | 59 |
| `.github/skills/hc3-rest-api/assets/scenes-automation.md` | Scenes, Profiles, Custom Events, Global Variables | 35 |
| `.github/skills/hc3-rest-api/assets/energy-climate.md` | Energy, Billing, Climate, Humidity, Sprinklers | 52 |
| `.github/skills/hc3-rest-api/assets/system.md` | Network, Users, Alarms, Rooms, Sections | 55 |
| `.github/skills/hc3-rest-api/assets/misc.md` | Notifications, Location, Debug, Weather, Icons, RGB, Push, System | 46 |
