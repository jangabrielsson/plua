---
name: quickapp-api
description: Full HC3 QuickApp Lua API reference: fibaro.* functions, QuickApp methods (self:updateProperty, self:updateView, self:getVariable, etc.), plugin.* API, api.* REST calls, net.HTTPClient/TCPSocket, timers (setTimeout/setInterval), JSON, and standard Lua libraries available in QA context. USE FOR: writing QuickApp code, looking up specific method signatures, understanding what functions are available, fixing "attempt to call nil" errors on QA methods.
---

# QuickApp Lua API Reference

Complete reference for the Fibaro HC3 QuickApp Lua programming environment. Use this skill when writing QuickApp code with plua.

---

## QuickApp Lifecycle

Every QuickApp starts with `onInit()`. The global `quickApp` variable is set only *after* `onInit()` returns.

```lua
function QuickApp:onInit()
    self:debug("Started, id =", self.id, "name =", self.name)
    -- initialize timers, load variables, etc.
end
```

---

## QuickApp Methods (self:...)

### Logging
```lua
self:debug(...)    -- DEBUG level — shown in HC3 debug console
self:trace(...)    -- TRACE level
self:warning(...)  -- WARNING level
self:error(...)    -- ERROR level
```
All logging methods accept multiple arguments separated by commas; they are concatenated with spaces.

### Device Properties
```lua
self:updateProperty("value", true)       -- persist and trigger events
self:updateProperty("log", "status msg") -- update log field
-- self.properties.value = true  ← DO NOT do this, no event generated
```
Common property names: `value`, `dead`, `log`, `userDescription`.

### QuickApp Variables
```lua
local v = self:getVariable("myKey")   -- returns "" if not found (not nil!)
self:setVariable("myKey", "myValue")  -- triggers DevicePropertyUpdatedEvent
-- Always check: if v ~= "" then ...
```

### UI Updates
```lua
self:updateView("labelId", "text", "Hello world")
self:updateView("sliderId", "value", "75")      -- value must be a STRING
self:updateView("btnId", "text", "Click me")
self:updateView("switchId", "value", "true")    -- "true" or "false" as string
```

### Children
```lua
-- Create a child device
local child = self:createChildDevice({
    name = "My Child",
    type = "com.fibaro.binarySwitch",
    initialProperties = { value = false }
}, ChildClass)  -- ChildClass is your class extending QuickAppChild

-- Load existing children at startup (call in onInit)
self:initChildDevices({ ["com.fibaro.binarySwitch"] = ChildClass })

-- Remove a child
self:removeChildDevice(childId)
```

### Actions and Interfaces
```lua
self:callAction("myMethod", arg1, arg2)   -- dispatch to self method
self:addInterfaces({"energy", "battery"}) -- add device interfaces
self:hasInterface("energy")               -- returns boolean
```

### Properties on `self`
| Property | Type | Description |
|---|---|---|
| `self.id` | number | Device ID |
| `self.name` | string | Device name |
| `self.type` | string | Device type string |
| `self.properties` | table | Full properties (read-only reference) |

---

## fibaro.* Global API

### Device Control
```lua
fibaro.call(deviceId, "turnOn")               -- invoke action on device
fibaro.call(deviceId, "setValue", 75)         -- with argument
fibaro.getValue(deviceId, "value")            -- returns value only
fibaro.get(deviceId, "value")                 -- returns (value, modifiedTimestamp)
fibaro.getDevicesID(filter)                   -- returns array of IDs matching filter
```

> Since fw ≥ 5.031.33, `fibaro.call` is async by default. For self-calls use `self:method()`.
> Control with `fibaro.useAsyncHandler(true/false)`.

### Device Metadata
```lua
fibaro.getName(deviceId)
fibaro.getType(deviceId)
fibaro.getRoomID(deviceId)
fibaro.getRoomName(roomId)
fibaro.getRoomNameByDeviceID(deviceId)
fibaro.getSectionID(deviceId)
```

### Global Variables
```lua
fibaro.getGlobalVariable("myVar")         -- returns string value
fibaro.setGlobalVariable("myVar", "val")  -- set value
```

### Scenes & Profiles
```lua
fibaro.scene("execute", sceneId)
fibaro.scene("kill", sceneId)
fibaro.profile(profileId, "activateProfile")
```

### Alarms & Notifications
```lua
fibaro.alarm(partitionId, "arm")          -- arm/disarm partition
fibaro.alert("email", {userId}, "msg")    -- send notification
fibaro.alert("push", {userId}, "msg")
fibaro.emitCustomEvent("myEventName")     -- fire custom event
```

### Logging (global)
```lua
fibaro.debug(tag, message)
fibaro.trace(tag, message)
fibaro.warning(tag, message)
fibaro.error(tag, message)
```

---

## plugin.* API

Lower-level API — prefer `self:` QuickApp methods where available.

```lua
plugin.mainDeviceId               -- current device ID
plugin.createChildDevice(props)   -- create child device
plugin.deleteDevice(deviceId)
plugin.getChildDevices(deviceId)
plugin.getDevice(deviceId)
plugin.getProperty(deviceId, prop)
plugin.restart(deviceId)
```

---

## api.* — Direct REST Calls to HC3

```lua
local device = api.get("/devices/25")
local devices = api.get("/devices?interface=zwave")
local result = api.post("/customEvents/myEvent", {})
api.put("/devices/25", { name = "New Name" })
api.delete("/globalVariables/oldVar")
```

`api.*` returns the parsed JSON response (Lua table), or `nil` on error.

---

## Timers and Scheduling

```lua
-- One-shot timer
local ref = setTimeout(function()
    self:debug("fired!")
end, 5000)  -- ms

clearTimeout(ref)

-- Repeating timer
local ref2 = setInterval(function()
    self:debug("tick")
end, 10000)

clearInterval(ref2)

-- setTimeout with 0 yields to pending tasks immediately
setTimeout(function() self:doSomething() end, 0)
```

> **Avoid `fibaro.sleep(ms)`** — it blocks all event handling, HTTP callbacks, and timers while sleeping. Always use `setTimeout`/`setInterval` patterns instead.

---

## net.* — Networking in QuickApps

### HTTP Client
```lua
local http = net.HTTPClient()
http:request("https://api.example.com/data", {
    options = {
        method = "GET",
        headers = { ["Authorization"] = "Bearer " .. token }
    },
    success = function(response)
        local data = json.decode(response.data)
        self:debug("status:", response.status)
    end,
    error = function(err)
        self:error("HTTP error:", err)
    end
})
```

### TCP Socket
```lua
local tcp = net.TCPSocket()
tcp:connect("192.168.1.100", 8080, {
    success = function()
        tcp:write("HELLO\n", {
            success = function() self:debug("sent") end
        })
    end,
    error = function(err) self:error("connect error:", err) end
})
tcp:read({ success = function(data) self:debug("received:", data) end })
tcp:close()
```

### UDP Socket
```lua
local udp = net.UDPSocket()
udp:sendTo("data", "192.168.1.100", 9999)
```

---

## JSON

```lua
local t = json.decode('{"key": "value", "num": 42}')
local s = json.encode({ key = "value", num = 42 })
```

### Availability: plua vs HC3
| Function | plua | HC3 |
|---|---|---|
| `json.encode(t)` | ✓ | ✓ |
| `json.decode(s)` | ✓ | ✓ |
| `json.encodeFormated(t)` | ✓ | ✗ — **plua only** |
| `json.util.InitArray(t)` | ✓ | ✓ |

> **`json.encodeFormated`** produces pretty-printed JSON but is only available in plua. Do **not** use it in code intended to run on a real HC3 — it will throw a nil-call error. If you need formatted output on the HC3, provide your own implementation.

### Marking tables as arrays: `json.util.InitArray`
By default, an empty or mixed Lua table may encode as `{}` (object) rather than `[]` (array). Use `json.util.InitArray` to force array encoding — this is available on **both plua and real HC3** and is essential when posting to REST APIs that require a JSON array:

```lua
local arr = json.util.InitArray({})          -- encodes as [] not {}
local items = json.util.InitArray({"a","b"}) -- encodes as ["a","b"]
api.post("/foo", { ids = json.util.InitArray({}) })
```

---

## Standard Lua Available in QAs

`os.time()`, `os.date()`, `os.clock()`, `os.difftime()`

`string.format()`, `string.find()`, `string.gmatch()`, `string.gsub()`, `string.sub()`, `string.split()` *(Fibaro extension)*, `string.starts()` *(Fibaro extension)*

`table.insert()`, `table.remove()`, `table.sort()`, `table.concat()`

`math.floor()`, `math.ceil()`, `math.abs()`, `math.max()`, `math.min()`, `math.random()`, `math.huge`

`pcall(f, ...)` — protected call; returns `(true, result)` or `(false, errmsg)`
`tostring()`, `tonumber()`, `type()`, `pairs()`, `ipairs()`

---

## Key Caveats

- `self:getVariable(name)` returns `""` when missing, **not** `nil`
- `self:updateView(...)` values must be **strings** — use `tostring(n)`
- `self.properties.*` writes are transient — use `self:updateProperty()` to persist
- All QuickApp methods are publicly callable via `fibaro.call(id, "method")` — keep private helpers as `local function`s outside the class
- `self.parent` is **not** available during `Child:__init()` — use child's `onInit()` instead
- `quickApp` global is only set after `onInit()` returns
