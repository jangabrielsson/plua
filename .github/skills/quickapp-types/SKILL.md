---
name: quickapp-types
description: All Fibaro device types (40+ types: switches, sensors, climate, covers, controllers), plua file headers (--%%name, --%%type, --%%var, --%%u:, --%%debug, etc.), UI element syntax (label, button, slider, switch, select, multi), and minimal starter templates for each device category. USE FOR: creating a new QuickApp, choosing the right device type (e.g. "what type for a temperature sensor?"), defining UI elements, understanding required actions per device type.
---

# QuickApp Device Types and Headers

Reference for all plua QuickApp file headers and the complete set of Fibaro device types.

Starter Lua templates are in the [`templates/`](./templates/) directory — reference them when the user needs a working skeleton for a specific device type.

---

## plua Header Syntax

```lua
--%%key:value
```
Headers are Lua comments processed by plua before execution. All headers must appear before any Lua code.

---

## Device Configuration Headers

```lua
--%%name:My QuickApp            -- display name (required)
--%%type:com.fibaro.binarySwitch -- device type (required)
--%%manufacturer:ACME Corp
--%%model:SmartDevice v1.0
--%%description:What this device does
--%%uid:unique-id-string
```

## Variable Headers

```lua
--%%var:apiKey="abc123"          -- string value: must be a Lua string literal
--%%var:location="Stockholm"     -- strings need quotes
--%%var:updateInterval=30        -- numbers are Lua literals, no quotes needed
```

> **Gotcha:** The value is evaluated as a Lua expression. `--%%var:X=London` evaluates the global `London` (likely `nil`). Use `--%%var:X="London"` for strings.

## Interface Headers

```lua
--%%interfaces:{"battery","energy"}
```

## Multi-file Headers

```lua
--%%file:./lib/utils.lua,utils   -- include external Lua file (path, module name)
```
To include a plua library file, use `--%%file:$fibaro.lib.libraryName,alias` (e.g. `--%%file:$fibaro.lib.qwikchild,qwikchild`)

## Development & Debug Headers

```lua
--%%debug:true        -- verbose debug logging
--%%desktop:true      -- auto-open QuickApp UI desktop window
--%%offline:true      -- run without HC3 connection
--%%breakonload:true  -- pause in debugger immediately on load
--%%save:state.json   -- persist state across restarts
--%%project:1001      -- associate with HC3 device ID for upload/sync
--%%proxy:true        -- enable proxy mode (sync with real HC3 QA)
--%%qacolor:lightblue -- background color of the QA desktop window
```

---

## UI Element Headers

Each `--%%u:` line defines one row. Use `{{...},{...}}` for multiple elements on the same row.

### Label
```lua
--%%u:{label="statusLbl",text="Status: Ready"}
```

### Button
```lua
--%%u:{button="myBtn",text="Click Me",onReleased="handleClick"}
-- callback: function QuickApp:handleClick(event) end
```

### Switch (toggle)
```lua
--%%u:{switch="autoSwitch",text="Auto Mode",value="false",onToggled="handleSwitch"}
-- event.values[1] == true/false (boolean)
```

### Slider
```lua
--%%u:{slider="brightSlider",text="Brightness",min="0",max="100",value="50",onChanged="handleSlider"}
-- use tonumber(event.values[1]) to get numeric value
```

### Select (single-choice)
```lua
--%%u:{select="modeSelect",text="Mode",value="1",onToggled="handleSelect",
--      options={{type='option',text='Economy',value='1'},{type='option',text='Comfort',value='2'}}}
```

### Multi (multi-select)
```lua
--%%u:{multi="tagMulti",text="Tags",values={"1","3"},onToggled="handleMulti",
--      options={{type='option',text='Tag A',value='1'},{type='option',text='Tag B',value='2'}}}
```

### Multiple elements on one row
```lua
--%%u:{{button="onBtn",text="On",onReleased="turnOn"},{button="offBtn",text="Off",onReleased="turnOff"}}
```


### Updating dropdowns at runtime

**Single-select (`select`)** — use `"selectedItem"` to set the current selection:
```lua
self:updateView("modeSelect", "options", {{type='option',text='Economy',value='1'},{type='option',text='Comfort',value='2'}})
self:updateView("modeSelect", "selectedItem", "1")   -- value string of the selected option
```

**Multi-select (`multi`)** — use `"selectedItems"` to set selected values, `"options"` to update the list:
```lua
self:updateView("tagMulti", "options", {{type='option',text='Tag A',value='1'},{type='option',text='Tag B',value='2'}})
self:updateView("tagMulti", "selectedItems", {"1","3"})  -- table of selected value strings
```

> **Gotcha:** Using `"values"` instead of `"selectedItems"` (or `"selectedItem"` for single-select) will silently fail or have no effect on the HC3.

### UI event callback pattern
```lua
function QuickApp:handleClick(event)
    -- event.deviceId, event.elementName, event.eventType, event.values
    self:debug("clicked:", event.elementName)
end

function QuickApp:handleSlider(event)
    local value = tonumber(event.values[1])
    self:updateView("brightSlider", "value", tostring(value))
end
```

---

## Device Type Quick Reference

### Switches

| Type | Required Actions | Value / Notes |
|---|---|---|
| `com.fibaro.binarySwitch` | `turnOn`, `turnOff` | `value` = boolean |
| `com.fibaro.multilevelSwitch` | `turnOn`, `turnOff`, `setValue` | `value` = 0–99 |
| `com.fibaro.colorController` | `turnOn`, `turnOff`, `setValue`, `setColor` | `value` = 0–99, `color` = `"r,g,b,w"` string e.g. `"200,10,100,255"` |

Templates: [binary-switch.lua](./templates/binary-switch.lua) · [multilevel-switch.lua](./templates/multilevel-switch.lua) · [color-controller.lua](./templates/color-controller.lua)

### Binary Sensors

All update `value` (boolean). No required actions.

| Type | Typical use |
|---|---|
| `com.fibaro.binarySensor` | Generic open/closed |
| `com.fibaro.doorSensor` | Door/window |
| `com.fibaro.windowSensor` | Window |
| `com.fibaro.motionSensor` | PIR motion |
| `com.fibaro.smokeSensor` | Smoke detector |
| `com.fibaro.fireDetector` | Fire detector |
| `com.fibaro.floodSensor` | Water/flood |
| `com.fibaro.waterLeakSensor` | Water leak |
| `com.fibaro.gasDetector` | Gas leak |
| `com.fibaro.coDetector` | Carbon monoxide |
| `com.fibaro.rainDetector` | Rain |
| `com.fibaro.heatDetector` | Heat detector |

Template: [binary-sensor.lua](./templates/binary-sensor.lua)

### Numeric Sensors

All update `value` as number or `{value=n, unit="C"}`. No required actions.

| Type | Value format |
|---|---|
| `com.fibaro.temperatureSensor` | `{value=21.5, unit="C"}` |
| `com.fibaro.humiditySensor` | number 0–100 |
| `com.fibaro.lightSensor` | number (lux) |
| `com.fibaro.multilevelSensor` | number |
| `com.fibaro.energyMeter` | number (kWh) |
| `com.fibaro.powerMeter` | number (W) |
| `com.fibaro.rainSensor` | number (mm/h) |
| `com.fibaro.windSensor` | number (m/s) |

Template: [templates/numeric-sensor.lua](./templates/numeric-sensor.lua)

### Climate / Thermostat

All thermostat setpoint/temperature values use `{value=n, unit="C"}` format.

**Full thermostat types** — handle `setThermostatMode`, update `thermostatMode`, `supportedThermostatModes`, `temperature`:

| Type | Extra Actions | Extra Properties |
|---|---|---|
| `com.fibaro.thermostat` | `setThermostatMode`, `setHeatingThermostatSetpoint`, `setCoolingThermostatSetpoint` | `heatingThermostatSetpoint`, `coolingThermostatSetpoint` |
| `com.fibaro.thermostatHeat` | `setThermostatMode`, `setHeatingThermostatSetpoint` | `heatingThermostatSetpoint` |
| `com.fibaro.thermostatCool` | `setThermostatMode`, `setCoolingThermostatSetpoint` | `coolingThermostatSetpoint` |
| `com.fibaro.thermostatHeatCool` | `setThermostatMode`, `setHeatingThermostatSetpoint`, `setCoolingThermostatSetpoint` | `heatingThermostatSetpoint`, `coolingThermostatSetpoint` |

**Setpoint-only types** — no mode, just setpoints + `temperature`:

| Type | Required Actions |
|---|---|
| `com.fibaro.thermostatSetpoint` | `setHeatingThermostatSetpoint`, `setCoolingThermostatSetpoint` |
| `com.fibaro.thermostatSetpointHeat` | `setHeatingThermostatSetpoint` |
| `com.fibaro.thermostatSetpointCool` | `setCoolingThermostatSetpoint` |
| `com.fibaro.thermostatSetpointHeatCool` | `setHeatingThermostatSetpoint`, `setCoolingThermostatSetpoint` |

**HVAC System types** — same interface as full thermostat counterparts:

| Type | Actions |
|---|---|
| `com.fibaro.hvacSystemHeat` | `setThermostatMode`, `setHeatingThermostatSetpoint` |
| `com.fibaro.hvacSystemCool` | `setThermostatMode`, `setCoolingThermostatSetpoint` |
| `com.fibaro.hvacSystemHeatCool` | `setThermostatMode`, `setHeatingThermostatSetpoint`, `setCoolingThermostatSetpoint` |
| `com.fibaro.hvacSystemAuto` | `setThermostatMode`, `setHeatingThermostatSetpoint`, `setCoolingThermostatSetpoint` |

Templates: [thermostat.lua](./templates/thermostat.lua) (full) · [thermostat-heat.lua](./templates/thermostat-heat.lua) · [thermostat-cool.lua](./templates/thermostat-cool.lua) · [thermostat-heatcool.lua](./templates/thermostat-heatcool.lua) · [thermostat-setpoint-heat.lua](./templates/thermostat-setpoint-heat.lua) · [thermostat-setpoint-cool.lua](./templates/thermostat-setpoint-cool.lua) · [thermostat-setpoint-heatcool.lua](./templates/thermostat-setpoint-heatcool.lua)

### Covers and Controllers

| Type | Required Actions | Notes |
|---|---|---|
| `com.fibaro.windowCovering` | `open`, `close`, `stop`, `setValue` | `value` = 0–99 (% open) |
| `com.fibaro.deviceController` | (none — generic) | define your own methods |
| `com.fibaro.remoteController` | (none) | call `self:emitCentralSceneEvent(keyId, keyAttribute)` to emit button events; `keyAttribute` defaults to `"Pressed"` |
| `com.fibaro.alarmPartition` | `arm`, `disarm` | `armed` = boolean, `alarm` = boolean |

Templates: [controller.lua](./templates/controller.lua) · [window-covering.lua](./templates/window-covering.lua) · [alarm-partition.lua](./templates/alarm-partition.lua) · [remote-controller.lua](./templates/remote-controller.lua)

### Special

| Type | Required Actions | Properties |
|---|---|---|
| `com.fibaro.player` | `play`, `pause`, `stop`, `next`, `prev`, `setVolume`, `setMute` | `volume` (0–100), `mute` (boolean), `power` (boolean) |
| `com.fibaro.weather` | (none) | `Temperature` `{value=n,unit="C"}`, `Humidity` (number), `Wind` (number) — note capital property names |
| `com.fibaro.genericDevice` | (none) | No specific interface contract |

Templates: [player.lua](./templates/player.lua) · [weather.lua](./templates/weather.lua) · [generic-device.lua](./templates/generic-device.lua)
