# QuickApp Emulator Documentation

This document covers the QuickApp emulation system in plua, which allows you to develop and test Fibaro HC3 QuickApps locally using special header directives.

## Overview

The plua QuickApp emulator enables local development and testing of Fibaro Home Center 3 QuickApps without requiring an actual HC3 device. QuickApp files are standard Lua files with special header directives that define the QuickApp's properties, behavior, and configuration.

## Requirements

- **`--fibaro` flag**: The emulator requires plua to be started with the `--fibaro` flag to enable Fibaro emulation support
- **`.fqa` extension**: QuickApp files typically use the `.fqa` (Fibaro QuickApp) extension, though to run in the QUickApp in the emulator we usually run the main lua file (with extension `.lua`) of the QuickApp file with proper headers

## Usage

```bash
# Run a QuickApp with emulation
plua --fibaro myquickapp.lua

# Run a QuickApp with API server
plua --fibaro --api-port 8888 myquickapp.lua
```

## Header Directive Format

Header directives are special comments at the beginning of your QuickApp file that configure the emulated device. They follow the format:

```lua
--%%<directive>:<value>
```

**Important Notes:**
- Headers must start with `--%%` (two hyphens followed by two percent signs)
- The directive and value are separated by a colon `:`
- Headers are typically placed at the top of the file before any executable code
- Headers can be terminated early with `--ENDOFHEADERS` comment

## Available Header Directives

### Basic QuickApp Properties

#### `--%%name:<string>`
Sets the name of the QuickApp device.
- **Type**: String
- **Default**: Filename without extension
- **Example**: `--%%name:My Smart Light Controller`

#### `--%%type:<string>`
Defines the device type/template.
- **Type**: String
- **Default**: `com.fibaro.binarySwitch`
- **Common Types**:
  - `com.fibaro.binarySwitch` - Basic on/off switch
  - `com.fibaro.multilevelSwitch` - Dimmable device
  - `com.fibaro.temperatureSensor` - Temperature sensor
  - `com.fibaro.humiditySensor` - Humidity sensor
  - `com.fibaro.lightSensor` - Light/illuminance sensor
- **Example**: `--%%type:com.fibaro.multilevelSwitch`

### Device Metadata

#### `--%%description:<string>`
Provides a userDescription property for the QuickApp.
- **Type**: String
- **Example**: `--%%description:Advanced lighting controller with scheduling`

#### `--%%manufacturer:<string>`
Sets the device manufacturer property for QuickApp.
- **Type**: String
- **Example**: `--%%manufacturer:My Company`

#### `--%%model:<string>`
Sets the device model property for QuickApp.
- **Type**: String
- **Example**: `--%%model:SmartLight Pro`

#### `--%%role:<string>`
Defines the deviceRole propertyfor QuickApp
- **Type**: String
- **Example**: `--%%role:Light`

#### `--%%uid:<string>`
Sets a unique quickAppUuid property for the QuickApp.
- **Type**: String
- **Example**: `--%%uid:v1.2.3`

### Geographic Location

#### `--%%latitude:<number>`
Sets the device latitude coordinate. Used when running offline.
- **Type**: Number (float)
- **Example**: `--%%latitude:59.3293`

#### `--%%longitude:<number>`
Sets the device longitude coordinate. Used when running offline.
- **Type**: Number (float)
- **Example**: `--%%longitude:18.0686`

### Development and Debugging

#### `--%%debug:<boolean>`
Enables debug mode for the QuickApp.
- **Type**: Boolean (`true` or `false`)
- **Default**: `false`
- **Example**: `--%%debug:true`

#### `--%%breakonload:<boolean>`
Breaks into debugger when the QuickApp loads (requires debugger setup).
- **Type**: Boolean (`true` or `false`)
- **Default**: `false`
- **Example**: `--%%breakonload:true`

### Proxy and Network Settings

#### `--%%proxy:<boolean>`
Enables proxy mode for development/testing.
- **Type**: Boolean (`true` or `false`)
- **Default**: `false`
- **Example**: `--%%proxy:true`

#### `--%%proxy_port:<number>`
Sets the proxy port when proxy mode is enabled.
- **Type**: Number (integer)
- **Example**: `--%%proxy_port:8080`

#### `--%%offline:<boolean>`
Runs the QuickApp in offline mode (no HC3 API calls).
- **Type**: Boolean (`true` or `false`)
- **Default**: `false`
- **Example**: `--%%offline:true`

### Project Management

#### `--%%save:<string>`
Specifies where to save the QuickApp file.
- **Type**: String (file path)
- **Example**: `--%%save:projects/lights/bedroom.fqa`

#### `--%%project:<number>`
Associates the QuickApp with a project ID.
- **Type**: Number (integer)
- **Example**: `--%%project:12345`

### Advanced Configuration

#### `--%%interfaces:<table>`
Defines the device interfaces/capabilities.
- **Type**: Lua table
- **Example**: `--%%interfaces:{"light", "energy", "power"}`

#### `--%%state:<string>`
Sets the initial device state.
- **Type**: String
- **Example**: `--%%state:idle`

#### `--%%time:<string>`
Sets time-related configuration.
- **Type**: String
- **Example**: `--%%time:2024-01-01T00:00:00`

### Variables and UI

#### `--%%var:<name>=<value>`
Defines QuickApp variables with initial values.
- **Format**: `name=value`
- **Types**: String, number, boolean, or Lua expression
- **Examples**:
  ```lua
  --%%var:interval=300
  --%%var:enabled=true
  --%%var:threshold=25.5
  --%%var:schedule={"07:00", "19:00"}
  ```

#### `--%%u:<ui_definition>`
Defines UI elements for the QuickApp interface.
- **Type**: Lua table representing UI elements
- **Example**:
  ```lua
  --%%u:{"button", "button1", "Turn On", "onReleased"}
  --%%u:{"label", "status", "Status: Ready"}
  --%%u:{"slider", "brightness", 0, 100, 50}
  ```

### File Inclusion

#### `--%%file:<path>,<name>`
Includes additional files in the QuickApp package.
- **Format**: `path,internal_name`
- **Library Prefix**: Use `$` prefix for library files in package.path
- **Examples**:
  ```lua
  --%%file:utils/helper.lua,helper -- load from file system
  --%%file:$mylibs.funcs,myfuncs   -- load as lua module (require)
  ```

### Utility Directives

#### `--%%nop:<boolean>`
No-operation directive (for compatibility/testing).
- **Type**: Boolean
- **Example**: `--%%nop:true`

#### `--%%proxyupdate:<string>`
Configuration for proxy update behavior.
- **Type**: String
- **Example**: `--%%proxyupdate:auto`

## Complete Example

Here's a comprehensive example of a QuickApp with various header directives:

```lua
--%%name:Smart Temperature Controller
--%%type:com.fibaro.temperatureSensor
--%%description:Advanced temperature monitoring with alerts
--%%manufacturer:MyCompany
--%%model:TempSensor Pro
--%%role:Sensor
--%%uid:v2.1.0
--%%debug:true
--%%proxy:true
--%%proxy_port:8080
--%%latitude:59.3293
--%%longitude:18.0686
--%%var:alertThreshold=25.0
--%%var:checkInterval=60
--%%var:enableAlerts=true
--%%u:{"label", "tempLabel", "Temperature: --°C"}
--%%u:{"button", "alertBtn", "Toggle Alerts", "onReleased"}
--%%u:{"slider", "threshold", 0, 50, 25}
--%%file:utils/math_helper.lua,math_utils
--%%save:sensors/temperature_controller.fqa

class 'TemperatureController'(QuickApp)

function TemperatureController:__init(dev)
    QuickApp.__init(self, dev)
    self.alertThreshold = tonumber(self:getVariable("alertThreshold")) or 25.0
    self.checkInterval = tonumber(self:getVariable("checkInterval")) or 60
    self.enableAlerts = self:getVariable("enableAlerts") == "true"
end

function TemperatureController:onInit()
    self:debug("Temperature Controller initialized")
    self:setupUICallbacks()
    self:scheduleTemperatureCheck()
    self:updateView("tempLabel", "text", "Temperature: --°C")
end

function TemperatureController:scheduleTemperatureCheck()
    setInterval(function()
        self:checkTemperature()
    end, self.checkInterval * 1000)
end

function TemperatureController:checkTemperature()
    -- Simulate temperature reading
    local temp = math.random(15, 35) + math.random()
    self:updateProperty("value", temp)
    self:updateView("tempLabel", "text", string.format("Temperature: %.1f°C", temp))
    
    if self.enableAlerts and temp > self.alertThreshold then
        self:warning("High temperature alert:", temp, "°C")
    end
end

function TemperatureController:onReleased(event)
    if event.elementName == "alertBtn" then
        self.enableAlerts = not self.enableAlerts
        self:setVariable("enableAlerts", tostring(self.enableAlerts))
        self:debug("Alerts", self.enableAlerts and "enabled" or "disabled")
    end
end

function TemperatureController:onChanged(event)
    if event.elementName == "threshold" then
        self.alertThreshold = tonumber(event.values[1])
        self:setVariable("alertThreshold", tostring(self.alertThreshold))
        self:debug("Alert threshold changed to", self.alertThreshold, "°C")
    end
end
```

## File Structure

When using file inclusion directives, the QuickApp emulator will:

1. Validate that specified files exist
2. Include them in the QuickApp package
3. Make them available during execution
4. Handle library references with `$` prefix

## Best Practices

### Header Organization
- Place all headers at the top of the file
- Group related headers together (basic properties, location, variables, etc.)
- Use meaningful names and descriptions
- Include version information with `uid`

### Development Workflow
1. Start with basic headers (`name`, `type`, `description`)
2. Add debugging support (`debug:true`, `proxy:true`)
3. Define variables and UI elements
4. Include additional files as needed
5. Test with `--fibaro` flag

### Variable Management
- Use descriptive variable names
- Set sensible default values
- Document variable purposes in comments
- Consider data types when setting initial values

### UI Design
- Start with simple UI elements
- Use clear, descriptive labels
- Implement proper event handlers
- Test UI interactions thoroughly

## Integration with plua

The QuickApp emulator integrates seamlessly with plua's features:

- **Timer System**: Use `setTimeout` and `setInterval` for scheduling
- **Network Module**: Access HTTP client/server capabilities via `net` module
- **JSON Support**: Built-in JSON encoding/decoding
- **Debugging**: Full debugger support with breakpoints
- **API Server**: Real-time UI updates via WebSocket
- **Hot Reload**: Modify and restart QuickApps during development

## Troubleshooting

### Common Issues

1. **Headers not recognized**: Ensure `--%%` prefix is correct
2. **Invalid values**: Check data types match directive requirements
3. **File not found**: Verify file paths in `--%%file` directives
4. **Library loading**: Use `$` prefix for package.path libraries
5. **Proxy issues**: Check proxy port conflicts

### Debug Tips

- Enable `--%%debug:true` for detailed logging
- Use `--%%breakonload:true` to debug initialization
- Check console output for header parsing errors
- Verify QuickApp appears in web interface (`/web`)

This emulation system provides a powerful development environment for creating and testing Fibaro HC3 QuickApps locally before deployment to actual devices.
