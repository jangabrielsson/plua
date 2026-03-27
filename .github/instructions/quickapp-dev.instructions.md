---
applyTo: "**/*.lua"
---

# QuickApp Development — Quick Reference

You are helping develop Fibaro HC3 QuickApps run under **plua** (a Lua interpreter written in Python).

## File headers (must be at top of file)
```lua
--%%name:My QuickApp          -- device display name
--%%type:com.fibaro.binarySwitch  -- Fibaro device type
--%%var:myKey=myValue         -- QuickApp variable
--%%u:{label="lbl",text="Status"}  -- UI element (one per row)
--%%u:{button="btn",text="Go",onReleased="handleBtn"}
--%%u:{slider="s1",text="",min="0",max="100",value="50",onChanged="handleSlider"}
--%%debug:true                -- verbose debug
--%%desktop:true              -- open UI window
--%%offline:true              -- no HC3 connection needed
```

## QuickApp skeleton
```lua
function QuickApp:onInit()
    self:debug(self.name, self.id)
    -- init timers, load variables, set initial state
end

-- UI callbacks receive an event table
function QuickApp:handleBtn(event)     end   -- button
function QuickApp:handleSlider(event)  end   -- slider: tonumber(event.values[1])
function QuickApp:handleSwitch(event)  end   -- switch: event.values[1] == true/false
```

## Core API quick-ref
```lua
-- State
self:updateProperty("value", true)           -- persist property + emit event
self:updateView("elemId", "text", "hello")   -- update UI (values must be STRINGS)
self:getVariable("key")   -- returns "" if missing (not nil)
self:setVariable("key", "val")

-- Fibaro globals
fibaro.call(id, "action", ...)
fibaro.getValue(id, "value")
fibaro.getGlobalVariable("name") / fibaro.setGlobalVariable("name", "val")
fibaro.emitCustomEvent("name")

-- REST
api.get("/devices/42")
api.post("/customEvents/evt", {})
api.put("/globalVariables/mode", {value="Away"})

-- Timers (never use fibaro.sleep — it blocks everything)
local ref = setTimeout(function() ... end, ms)
clearTimeout(ref)
local ref2 = setInterval(function() ... end, ms)
clearInterval(ref2)

-- JSON
json.encode(table)  /  json.decode(string)
```

## Key rules
- `self:getVariable()` returns `""` not `nil` when missing
- `self:updateView()` values must be strings — use `tostring(n)`
- Use `self:method()` to call self (not `fibaro.call(self.id, ...)`)
- Private helpers should be `local function`s **outside** the `QuickApp:` methods
- Use `pcall` to guard JSON parsing and HTTP responses

## Common device types
`com.fibaro.binarySwitch` · `com.fibaro.multilevelSwitch` · `com.fibaro.binarySensor`
`com.fibaro.temperatureSensor` · `com.fibaro.humiditySensor` · `com.fibaro.motionSensor`
`com.fibaro.doorSensor` · `com.fibaro.deviceController` · `com.fibaro.thermostat`

## Querying live HC3 state
Use `plua --fibaro -e "..."` in the terminal to inspect the real HC3 — credentials are already configured. The double parentheses prevent the HTTP status code from being passed as a second argument to `json.encodeFormated`.
```bash
# Get a device's full structure
plua --fibaro -e "json.encodeFormated((api.get('/devices/45')))"
# List all QuickApps
plua --fibaro -e "json.encodeFormated((api.get('/devices?interface=quickApp')))"
# Get a global variable
plua --fibaro -e "json.encodeFormated((api.get('/globalVariables/myVar')))"
# Get QA variables for device 45
plua --fibaro -e "json.encodeFormated((api.get('/plugins/45/variables')))"
```
Run these to understand the actual structure before writing code that reads or updates it.

## Available skills
Type a slash command in chat to load detailed reference:
`/quickapp-api` · `/quickapp-types` · `/quickapp-patterns` · `/hc3-rest-api` · `/lua-basics` · `/plua-troubleshooting` · `/plua-setup` · `/quickapp-troubleshooting`
