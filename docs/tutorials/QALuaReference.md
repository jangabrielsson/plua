# HC3 QuickApp Lua Reference

A concise reference of globals, functions, classes, and patterns available in the Fibaro HC3 QuickApp Lua environment. This consolidates common APIs and behavior visible in the global environment (`_G`).

> Notes
> - This reflects observed behavior and available symbols; some entries are internal/undocumented and may change across firmware versions.
> - Unless noted, examples assume QuickApp context (i.e., inside your QA code).
> - Standard Lua 5.3 libraries are available; a few helpers are added by Fibaro (e.g., `string.split`, `string.starts`).

## Contents
- [HC3 QuickApp Lua Reference](#hc3-quickapp-lua-reference)
  - [Contents](#contents)
  - [Globals and constants](#globals-and-constants)
  - [Fibaro APIs](#fibaro-apis)
    - [fibaro.\*](#fibaro)
    - [plugin.\*](#plugin)
    - [api.\* (HTTP to HC3 REST)](#api-http-to-hc3-rest)
  - [Timers and scheduling](#timers-and-scheduling)
  - [Logging and JSON](#logging-and-json)
  - [Classes and userdata](#classes-and-userdata)
  - [QuickApp methods and properties](#quickapp-methods-and-properties)
    - [Lifecycle and logging](#lifecycle-and-logging)
    - [Variables and properties](#variables-and-properties)
    - [Children](#children)
    - [Dispatch and interfaces](#dispatch-and-interfaces)
    - [Common properties on `self`](#common-properties-on-self)
  - [Standard Lua libraries (available in QA)](#standard-lua-libraries-available-in-qa)
  - [Caveats and best practices](#caveats-and-best-practices)
  - [See also](#see-also)

---

## Globals and constants
- `_G` (table): The global environment.
  - Example: `_G['foo'] = function(x) return x + x end`
- `_VERSION` (string): Lua interpreter version (e.g., "Lua 5.3").
- `__TAG` (string): Log tag used by `self:debug/trace/warning/error`.
  - Default: "QuickApp" .. self.id.
- `plugin.mainDeviceId` (number): Current device ID (equivalent to `self.id`).
- `quickApp` (QuickApp instance): Global set to your QA object, but only after `onInit()` returns.
- `math.huge`, `math.pi`, `math.maxinteger`, `math.mininteger`: Standard Lua numeric constants.
- `utf8.charpattern`: Pattern for a single UTF‑8 sequence.
- `logger.*` constants: `logger.TRACE (0)`, `DEBUG (1)`, `INFO (2)`, `WARNING (3)`, `ERROR (4)`, `FATAL (5)` (used with `logger.*` functions).
- `json._VERSION`, `json._COPYRIGHT`, `json.decode.*` and `json.encode.*` flags: JSON library meta and options.

---

## Fibaro APIs

### fibaro.*
- `fibaro.alarm(partitionId, action)`: Control alarm partitions.
- `fibaro.alert(alertType, userIds, message)`: Push alerts/notifications.
- `fibaro.call(deviceId, action, ...)`: Invoke a device action/method.
  - Since fw ≥ 5.031.33 default is async (see `fibaro.useAsyncHandler`). Use local calls like `self:method(...)` when targeting self.
- `fibaro.callGroupAction(action, filter)`: Group actions by filter.
- `fibaro.emitCustomEvent(name)`: Publish custom event.
  - REST: `api.post("/customEvents/<name>")`.
- `fibaro.get(deviceId, property)`: Returns `(value, modifiedTimestamp)`.
  - REST equivalent: `api.get("/devices/<id>/properties/<property>")`.
- `fibaro.getValue(deviceId, property)`: Returns property value only.
- `fibaro.getDevicesID(filter)`: Returns devices matching filter.
- `fibaro.getGlobalVariable(name)`: Returns the string value.
  - REST: `(api.get("/globalVariables/<name>") or {}).value`.
  - HC2‑style value + modified: return `(v.value, v.modified)`.
- `fibaro.setGlobalVariable(name, value)`: Set a global variable.
  - REST: `api.put("/globalVariables/<name>", {value = value})`.
- `fibaro.getIds(devices)`: Filter device structs to IDs (id > 3).
- `fibaro.getName(deviceId)`, `fibaro.getRoomID(deviceId)`, `fibaro.getRoomName(roomId)`, `fibaro.getRoomNameByDeviceID(deviceId)`, `fibaro.getSectionID(deviceId)`, `fibaro.getType(deviceId)`: Metadata helpers.
- `fibaro.profile(profileId)`: Profile operations.
- `fibaro.scene(action, sceneId)`: Control scenes.
- `fibaro.setTimeout(ms, fun)`, `fibaro.clearTimeout(ref)`: Schedule/cancel a callback (see also global `setTimeout/clearTimeout`).
- `fibaro.sleep(ms)`: Blocking sleep (see caveats).
- `fibaro.useAsyncHandler(boolean)`: Switch `fibaro.call` sync/async behavior.
- `fibaro.wakeUpDeadDevice(deviceId)`: Attempt to wake device.
- `fibaro.debug(tag, msg)`, `fibaro.trace(tag, msg)`, `fibaro.warning(tag, msg)`, `fibaro.error(tag, msg)`: Tagged logging.
- `getHierarchy()`: Returns hierarchy descriptor (rooms/sections/types).

Internal (undocumented, may change):
- `__assert_type(typeString, obj)`: Type guard used by internals.
- `__fibaroSleep(ms)`: Underlying implementation of `fibaro.sleep`.
- `__fibaroUseAsyncHandler(bool)`: Underlying async handler toggle.
- `__fibaro_add_debug_message(...)`: Used by logging.
- `__fibaro_get_device(id)`, `__fibaro_get_devices()`, `__fibaro_get_device_property(id, prop)`: Internal getters (use `api.*`).
- `__fibaro_get_global_variable(name)`, `__fibaro_get_room(id)`, `__fibaro_get_scene(id)`: Internal getters (use `api.*`).
- `__ternary(test, e1, e2)`: Ternary helper (equivalent to `test and e1 or e2`).

### plugin.*
- `plugin.createChildDevice(properties)`
- `plugin.deleteDevice(deviceId)`
- `plugin.getChildDevices(deviceId)`
- `plugin.getDevice(deviceId)`
- `plugin.getProperty(deviceId, property)`
- `plugin.restart(deviceId)`

These correspond to device lifecycle and property operations for QA/child devices; prefer the higher‑level QuickApp methods where available.

### api.* (HTTP to HC3 REST)
- `api.get(path)`, `api.post(path, data)`, `api.put(path, data)`, `api.delete(path)`
  - Examples:
    - `api.get("/devices")`, `api.get("/devices/<id>")`.
    - `api.put("/devices/<id>", {enabled = false})` (may restart QA).

---

## Timers and scheduling
- `setTimeout(function, ms)`: Schedule a function to run later (ms). `setTimeout(fn, 0)` yields to pending tasks and runs ASAP.
- `clearTimeout(ref)`: Cancel a scheduled timeout.
- `setInterval(function, ms)`: Repeating schedule (built on timeouts).
- `clearInterval(ref)`: Cancel an interval.
- `fibaro.setTimeout/clearTimeout`: Aliases provided by Fibaro.
- `fibaro.sleep(ms)`: Blocking “busy sleep”; prevents handling of UI events, HTTP callbacks, timeouts, or `fibaro.call` dispatch while sleeping. Avoid in loops—prefer `setTimeout`/`setInterval`.

---

## Logging and JSON
- QuickApp logging (preferred): `self:debug(...)`, `self:trace(...)`, `self:warning(...)`, `self:error(...)` (tagged with `__TAG`).
- Global logging: `fibaro.debug/trace/warning/error(tag, msg)`.
- `logger.*` (if present): `logger.debug/trace/info/warning/error/fatal`, level management via `logger.setLevel(level)` and `logger.getLevel()`.
- JSON: `json.encode(any) -> string`, `json.decode(string) -> any`.
  - Utility/flags: `json.util.*`, `json.decode.*`, `json.encode.*`.

---

## Classes and userdata
- Class helpers (Luabind): `class "Name" (Base)`, `property(setter, getter)`, `super()`.
- Core classes:
  - `Device`: Base device class (internal).
  - `QuickAppBase`: Base for `QuickApp` and `QuickAppChild` (shared methods like logging, `updateView`, `updateProperty`).
  - `QuickApp`: Your QA class; instances are your device object (`self`).
  - `QuickAppChild`: Class for child devices.
  - `Hierarchy`: Class for the hierarchy object returned by `getHierarchy()`.
- Networking/userdata:
  - `net.HTTPClient(options)`: HTTP client (likely LuaSocket wrapper).
  - `net.TCPSocket(options)`, `net.UDPSocket(options)`: TCP/UDP sockets.
  - `mqtt.Client`, `mqtt.ConnectReturnCode`, `mqtt.QoS`: MQTT wrappers.
  - `json.decode.*`: lpeg pattern objects used internally by JSON.

---

## QuickApp methods and properties

### Lifecycle and logging
- `QuickApp:onInit()`: Called after Fibaro creates the QA object and after your code has loaded. `quickApp` global is assigned only after `onInit()` returns.
- `QuickApp:debug/trace/warning/error(...)`: Tagged logging via `__TAG`.

### Variables and properties
- `QuickApp:getVariable(name) -> any|string`: Returns QA variable or "" if not present (note: not `nil`).
- `QuickApp:setVariable(name, value)`: Set QA variable; triggers a `DevicePropertyUpdatedEvent` for the entire variable list.
- `QuickApp:updateProperty(property, value)`: Persist device property and trigger relevant events (preferred over `self.properties.* = ...`).
- `QuickApp:updateView(element, type, value)`: Update UI element. Value must be a string for most types.

### Children
- `QuickApp:createChildDevice(properties, constructor) -> child`: Create child device and corresponding object.
- `QuickApp:removeChildDevice(id)`: Remove child device.
- `QuickApp:initChildDevices(map)`: Load existing children at startup (type → constructor). See limitations in tutorials.

### Dispatch and interfaces
- `QuickApp:callAction(method, ...)`: Manual dispatch helper (similar to how incoming `fibaro.call` is dispatched).
- `QuickApp:addInterfaces({names})`: Add interfaces to device.

### Common properties on `self`
- `self.id` (number) — device ID
- `self.name` (string) — device name
- `self.type` (string) — device type (e.g., `com.fibaro.binarySwitch`)
- `self.properties` (table) — full properties table, including:
  - `value`, `dead`, `deviceIcon`, `categories`, `quickAppVariables`, `viewLayout`, `uiCallbacks`, etc.

---

## Standard Lua libraries (available in QA)

Base functions: `assert`, `collectgarbage`, `error`, `ipairs`, `pairs`, `next`, `pcall`, `print`, `rawlen`, `select`, `tonumber`, `tostring`, `type`, `xpcall`, `unpack` (compat), etc.

`os`: `clock`, `date`, `difftime`, `exit`, `time`.

`string`: `byte`, `char`, `dump`, `find`, `format`, `gmatch`, `gsub`, `len`, `lower`, `match`, `pack`, `packsize`, `rep`, `reverse`, `split` (added), `starts` (added), `sub`, `unpack`, `upper`.

`table`: `concat`, `insert`, `move`, `pack`, `remove`, `sort`, `unpack`.

`math`: `abs`, `acos`, `asin`, `atan`, `atan2`, `ceil`, `cos`, `cosh`, `deg`, `exp`, `floor`, `fmod`, `frexp`, `ldexp`, `log`, `log10`, `max`, `min`, `modf`, `pow`, `rad`, `random`, `randomseed`, `sin`, `sinh`, `sqrt`, `tan`, `tanh`, `tointeger`, `type`, `ult`.

`bit32` (Lua 5.2‑style 32‑bit ops): `arshift`, `band`, `bnot`, `bor`, `btest`, `bxor`, `extract`, `lrotate`, `lshift`, `replace`, `rrotate`, `rshift`.

`utf8`: `char`, `codepoint`, `codes`, `len`, `offset`.

---

## Caveats and best practices
- `fibaro.sleep(ms)` is blocking: it halts the QA’s single thread—no UI, no HTTP callbacks, no timers. Avoid in loops. Prefer `setTimeout`/`setInterval` driven patterns.
- `fibaro.useAsyncHandler(true)` (default) avoids deadlocks and long waits when calling other devices (or self). Keep async enabled unless you specifically need synchronous behavior.
- `self:getVariable(name)` returns an empty string "" when missing, not `nil`. Use explicit checks or defaulting: `local v = self:getVariable("A"); if v ~= "" then ... end`.
- `self:updateView(...)` generally expects string values (e.g., slider "50"). Convert numbers with `tostring`.
- `self.properties.*` updates are transient and don’t generate events; use `self:updateProperty(...)` to persist and notify.
- `quickApp` global reference is only set after `onInit()` returns. If you need it in helpers, initialize those after `onInit()` or schedule with `setTimeout(..., 0)`.
- All methods you add to `QuickApp` become publicly callable via `fibaro.call(id, "method", ...)` and via REST: `POST /api/devices/<id>/action/<method>`. Keep private helpers outside the class (local functions) if you don’t want to expose them.
- For child devices, `self.parent` is not available during `Child:__init(...)`; it’s set after construction. Use `onInit()` in the child if you need parent access immediately.

---

## See also
- Fibaro docs for HC3 QuickApps: https://docs.fibaro.com
- Tutorials in this repo:
  - QuickApps – Part 1: Lua and OO fundamentals
  - QuickApps – Part 2: QuickApp architecture and methods
  - QuickApps – Part 3: Execution model (Operator)
  - QuickApps – Part 4: QuickAppChildren
