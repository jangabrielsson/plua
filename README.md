# PLua - Lua Interpreter in Python

A powerful Lua interpreter implemented in Python using the Lupa library. PLua provides a complete Lua 5.4 environment with an extensive modular extension system, async networking capabilities, debugging support, and comprehensive Fibaro HomeCenter 3 QuickApp development support.

## Features

- **Lua 5.4 Environment**: Full Lua 5.4 compatibility through the Lupa library
- **Command Line Interface**: Run Lua files, execute code fragments, or start interactive mode
- **Interactive Shell**: Full REPL mode with colored output and version information
- **Modular Extension System**: Decorator-based system for adding Python functions to Lua
- **Rich Function Library**: 60+ built-in Python functions across multiple categories
- **Async Networking**: True asynchronous TCP/UDP networking with callback support
- **Synchronous Networking**: Non-blocking TCP functions with smart error handling
- **HTTP Support**: Full HTTP client with request/response handling
- **Debugging Support**: MobDebug integration for remote debugging
- **Smart Shutdown**: Intelligent termination detection for network operations
- **Pretty Printing**: JSON-based table pretty printing with nested structure support
- **Executable Build**: PyInstaller support for creating standalone executables
- **Version Management**: Single source of truth versioning from pyproject.toml
- **Colorized Output**: ANSI color support for enhanced terminal experience
- **Fibaro HomeCenter 3 Support**: Complete Lua API compatibility for Fibaro HomeCenter 3 development and testing
- **Web Server**: Independent HTTP server for receiving callbacks and serving status pages

## Documentation

- **[Coroutine Limitations](docs/COROUTINE_LIMITATIONS.md)** - Important information about Lupa coroutine resumption limitations and PLua's workarounds

## Requirements

- Python 3.12+
- uv package manager (recommended) or pip

## Installation

### Using uv (Recommended)

1. Clone or download this repository
2. Install uv if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Set up the environment and install dependencies:
   ```bash
   uv sync
   ```

### Alternative: Using pip

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Pre-built Executables

For users who don't want to install Python and dependencies, pre-built executables are available for download:

### Latest Release

Download the latest release from [GitHub Releases](https://github.com/jangabrielsson/plua/releases/latest).

**Available platforms:**
- **Windows**: `plua-windows.exe` - For Windows 10/11
- **macOS Universal**: `plua-macos-universal` - For both Intel and Apple Silicon Macs

### Usage

```bash
# Windows
plua-windows.exe script.lua

# macOS Universal
chmod +x plua-macos-universal
./plua-macos-universal script.lua
```

### All Releases

View all releases at: https://github.com/your-username/plua/releases

## Getting Started

### Installation

```bash
# Install in development mode
uv pip install -e .

# Run a Lua script
plua [your_lua_file.lua]

# Or use the module form
python -m plua [your_lua_file.lua]
```

## Usage Modes

PLua supports two main usage modes:

### 1. Standard Lua Development (without --fibaro flag)

For general Lua development with access to Python extensions and additional libraries.

**Starting PLua:**
```bash
# Run a Lua script
plua script.lua

# Interactive mode
plua -i

# Execute code directly
plua -e "print('Hello, World!')"

# Load additional libraries
plua -l socket -l debugger script.lua

# With debugging
plua --debugger script.lua
```

**Available Libraries:**
- `plua.net` - Network utilities (HTTP, TCP, UDP)
- `plua.json` - JSON encoding/decoding
- `plua.class` - Object-oriented programming support
- `socket` - Socket library for networking
- `debugger` - Debugging utilities

**Python Extensions:**
All `_PY.*` functions are available for direct access to Python functionality.

### 2. Fibaro HomeCenter 3 QuickApp Development (with --fibaro flag)

For developing and testing Fibaro HomeCenter 3 QuickApps with full API emulation.

**Starting PLua:**
```bash
# Run a QuickApp script
plua --fibaro script.lua

# Interactive mode with Fibaro support
plua --fibaro -i

# Execute QuickApp code directly
plua --fibaro -e "fibaro.call(123, 'turnOn')"

# With debugging
plua --fibaro --debugger script.lua
```

**Automatic Loading:**
When using `--fibaro`, the following are automatically loaded:
- `fibaro.lua` - Complete Fibaro HC3 API
- `quickapp.lua` - QuickApp base class
- `net.lua` - Network utilities
- All standard Lua libraries

**Hidden Complexity:**
- `_PY` functions are hidden from the user
- Standard Fibaro environment is provided
- QuickApp development is simplified

## VS Code Configuration

### Launch Configuration

Create or update `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "PLua Standard",
            "type": "lua",
            "request": "launch",
            "program": "${file}",
            "runtimeExecutable": "plua",
            "runtimeArgs": [],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "PLua Fibaro",
            "type": "lua",
            "request": "launch",
            "program": "${file}",
            "runtimeExecutable": "plua",
            "runtimeArgs": ["--fibaro"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "PLua Debugger",
            "type": "lua",
            "request": "launch",
            "program": "${file}",
            "runtimeExecutable": "plua",
            "runtimeArgs": ["--debugger", "--debugger-port", "8818"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "PLua Fibaro Debugger",
            "type": "lua",
            "request": "launch",
            "program": "${file}",
            "runtimeExecutable": "plua",
            "runtimeArgs": ["--fibaro", "--debugger", "--debugger-port", "8818"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### Tasks Configuration

Create or update `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run PLua Script",
            "type": "shell",
            "command": "plua",
            "args": ["${file}"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "Run PLua Fibaro Script",
            "type": "shell",
            "command": "plua",
            "args": ["--fibaro", "${file}"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "PLua Interactive",
            "type": "shell",
            "command": "plua",
            "args": ["-i"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "PLua Fibaro Interactive",
            "type": "shell",
            "command": "plua",
            "args": ["--fibaro", "-i"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        }
    ]
}
```

## Command Line Options

- `file` - Lua file to execute
- `-e, --execute` - Execute Lua code string (can be used multiple times)
- `-i, --interactive` - Start interactive shell
- `-l, --library` - Load library before executing script (can be used multiple times)
- `-d, --debug` - Enable debug output
- `--fibaro` - Load Fibaro HC3 environment and libraries
- `--debugger` - Start MobDebug server for remote debugging
- `--debugger-port PORT` - Port for MobDebug server (default: 8818)
- `-v, --version` - Show version information

## Configuration

### Project Configuration File: .plua.lua

PLua supports project/user configuration via a `.plua.lua` file. This file can be placed in either the current working directory or your home directory (or both). If both exist, values from the current directory take precedence.

**Search order:**
1. `$HOME/.plua.lua` (user config)
2. `./.plua.lua` (project config, overrides user config)

**Format:**
The file must return a Lua table (with or without the `return` keyword):
```lua
return {
  key1 = "value1",
  key2 = 42,
  key3 = { nested = true },
  key4 = function() print("hello") end,
  ...
}
```
Or simply:
```lua
{
  key1 = "value1",
  ...
}
```

**Accessing configuration in Lua:**
The merged configuration table is available as `_PY.pluaconfig`:
```lua
print(_PY.pluaconfig.key1)
if _PY.pluaconfig.debug then print("Debug mode enabled") end
if _PY.pluaconfig.on_startup then _PY.pluaconfig.on_startup() end
```

**Notes:**
- Any Lua type is supported (strings, numbers, tables, booleans, functions, etc).
- If both files exist, keys from the current directory override those from the home directory.
- If no config is found, `_PY.pluaconfig` is an empty table.
- Comments and whitespace are allowed in the config file.

---

# Standard Lua Development

This section covers using PLua for general Lua development without the Fibaro environment.

## Available Libraries

### plua.net
Network utilities for HTTP and TCP operations:

```lua
local net = require("plua.net")

-- HTTP Client
local http = net.HTTPClient()
http:request("https://api.example.com/data", {
    options = {
        method = "POST",
        headers = {["Content-Type"] = "application/json"},
        data = '{"key":"value"}'
    },
    success = function(response)
        print("Response:", response.body)
    end,
    error = function(status)
        print("Error:", status)
    end
})

-- TCP Socket
local socket = net.TCPSocket({
    success = function(data) print("Connected") end,
    error = function(err) print("Error:", err) end
})

socket:connect("example.com", 80, {
    success = function() 
        socket:write("GET / HTTP/1.0\r\n\r\n", {
            success = function()
                socket:read({
                    success = function(data) print("Data:", data) end
                })
            end
        })
    end
})
```

### plua.json
JSON encoding and decoding utilities:

```lua
local json = require("plua.json")

-- Encode table to JSON string
local data = {name = "John", age = 30}
local json_str = json.encode(data)

-- Decode JSON string to table
local decoded = json.decode('{"name":"John","age":30}')

-- Pretty print table as formatted JSON
local pretty = json.encodeFormated(data)
```

### plua.class
Simple class system for object-oriented programming:

```lua
local class = require("plua.class")

-- Define a class
local MyClass = class("MyClass")
function MyClass:__init(name)
    self.name = name
end
function MyClass:greet()
    return "Hello, " .. self.name
end

-- Create instance
local obj = MyClass("World")
print(obj:greet()) -- Output: Hello, World
```

## Python Extensions (_PY functions)

PLua provides extensive Python integration through the `_PY` table. Functions are organized into categories:

### Timer Functions
- `setTimeout(function, ms)` - Schedule a function to run after ms milliseconds
- `clearTimeout(reference)` - Cancel a timer using its reference ID
- `has_active_timers()` - Check if there are active timers

### I/O Functions
- `input_lua(prompt)` - Get user input with optional prompt
- `read_file(filename)` - Read and return file contents
- `write_file(filename, content)` - Write content to a file

### JSON Functions
- `parse_json(json_string)` - Parse JSON string to table
- `to_json(data)` - Convert data to JSON string
- `pretty_print(data, indent)` - Pretty print table as JSON string
- `print_table(data, indent)` - Print table in pretty JSON format

### HTTP Functions
- `http_request_sync(url_or_table)` - Synchronous HTTP request (LuaSocket style)
- `http_request_async(lua_runtime, url_or_table, callback)` - Asynchronous HTTP request

### TCP Functions (Synchronous)
- `tcp_connect_sync(host, port)` - Connect to TCP server, returns `(success, conn_id, message)`
- `tcp_write_sync(conn_id, data)` - Write data to TCP connection, returns `(success, bytes_written, message)`
- `tcp_read_sync(conn_id, pattern)` - Read data from TCP connection using pattern, returns `(success, data, message)`
- `tcp_close_sync(conn_id)` - Close TCP connection, returns `(success, message)`

### File System Functions
- `file_exists(filename)` - Check if file exists
- `get_file_size(filename)` - Get file size in bytes
- `list_files(directory)` - List files in directory
- `create_directory(path)` - Create directory

### System Functions
- `get_time()` - Get current timestamp in seconds
- `sleep(seconds)` - Sleep for specified seconds (non-blocking)
- `get_python_version()` - Get Python version information

### Configuration Functions
- `get_env_var(name, default)` - Get environment variable value
- `set_env_var(name, value)` - Set environment variable
- `get_all_env_vars()` - Get all environment variables as a table

## Examples

### Basic Usage

```lua
-- Variables and control structures
local name = "World"
if name == "World" then
    print("Hello, " .. name .. "!")
end

-- Functions
local function greet(person)
    return "Hello, " .. person .. "!"
end

print(greet("Alice"))
```

### Pretty Printing Tables

```lua
-- Create a complex nested table
local data = {
    name = "John",
    age = 30,
    hobbies = {"reading", "coding", "gaming"},
    address = {
        city = "New York",
        zip = "10001",
        coordinates = {40.7128, -74.0060}
    },
    metadata = {
        created = "2024-01-01",
        tags = {"user", "active"}
    }
}

-- Pretty print the table
_PY.print_table(data)

-- Get pretty JSON string
local json_string = _PY.pretty_print(data, 4)
print("JSON string length:", #json_string)
```

### HTTP Requests

```lua
-- Simple GET request
local response = _PY.http_request_sync("https://httpbin.org/json")
if response and not response.error then
    print("Status:", response.code)
    print("Response length:", #response.body)
    
    -- Parse JSON response
    local data = _PY.parse_json(response.body)
    if data then
        print("Title:", data.slideshow.title)
    end
end
```

### Network Operations

```lua
-- TCP connection with synchronous functions
local success, conn_id, message = _PY.tcp_connect_sync("httpbin.org", 80)
if success then
    print("Connected:", message)
    
    -- Send HTTP request
    local request = "GET /json HTTP/1.1\r\nHost: httpbin.org\r\n\r\n"
    local write_success, bytes_written, write_message = _PY.tcp_write_sync(conn_id, request)
    if write_success then
        print("Sent:", write_message)
        
        -- Read response
        local read_success, data, read_message = _PY.tcp_read_sync(conn_id, "*a")
        if read_success then
            print("Received:", read_message)
            print("Data preview:", string.sub(data, 1, 200))
        end
    end
    
    _PY.tcp_close_sync(conn_id)
else
    print("Connection failed:", message)
end
```

### Timer Operations

```lua
-- Set a timer
print("Starting timer...")
local timer_id = _PY.setTimeout(function()
    print("Timer fired after 3 seconds!")
end, 3000)

-- Check if timers are active
if _PY.has_active_timers() then
    print("Timers are running")
end

-- Cancel timer (optional)
-- _PY.clearTimeout(timer_id)
```

### File Operations

```lua
-- Read and write files
local content = _PY.read_file("input.txt")
if content then
    print("File content length:", #content)
    
    -- Write modified content
    local success = _PY.write_file("output.txt", string.upper(content))
    if success then
        print("File written successfully")
    end
end

-- Check file existence
if _PY.file_exists("important.txt") then
    local size = _PY.get_file_size("important.txt")
    print("File size:", size, "bytes")
end

-- List files in directory
local files = _PY.list_files(".")
if files then
    print("Files in current directory:")
    for i, file in ipairs(files) do
        print("  " .. i .. ": " .. file)
    end
end
```

---

# Fibaro HomeCenter 3 QuickApp Development

This section covers developing and testing Fibaro HomeCenter 3 QuickApps using PLua.

## Quick Start

```bash
# Run a QuickApp script
plua --fibaro my_quickapp.lua

# Interactive mode with Fibaro support
plua --fibaro -i

# With debugging enabled
plua --fibaro --debugger my_quickapp.lua
```

## Environment Setup

When using `--fibaro`, PLua automatically loads:
- Complete Fibaro HC3 API (`fibaro` table)
- QuickApp base class (`QuickApp`)
- Network utilities (`net`)
- JSON utilities (`json`)
- Class system (`class`)

The `_PY` table is hidden from the user to provide a clean Fibaro development environment.

## Configuration

### HC3 Credentials

You can configure HC3 connection credentials in several ways:

#### 1. Environment Variables
```bash
export HC3_URL="https://192.168.1.100"
export HC3_USER="admin"
export HC3_PASSWORD="your_password"
```

#### 2. .env File
Create a `.env` file in your project directory:
```
HC3_URL=https://192.168.1.100
HC3_USER=admin
HC3_PASSWORD=your_password
```

#### 3. .plua.lua Configuration File
Create a `.plua.lua` file in your project directory:
```lua
return {
    hc3_url = "https://192.168.1.100",
    hc3_user = "admin",
    hc3_pass = "your_password"
}
```

## Fibaro API Reference

### Device Management

```lua
-- Get all device IDs
local deviceIds = fibaro.getDevicesID()

-- Get devices by type
local lightIds = fibaro.getDevicesID({type = "com.fibaro.multilevelSwitch"})

-- Get devices by property
local armedDevices = fibaro.getDevicesID({
    properties = {armed = true}
})

-- Call device action
fibaro.call(123, "turnOn")

-- Get device property
local value = fibaro.getValue(123, "value")

-- Get device with modification time
local value, modified = fibaro.get(123, "value")

-- Get device type
local deviceType = fibaro.getType(123)

-- Get device name
local deviceName = fibaro.getName(123)

-- Get device room ID
local roomId = fibaro.getRoomID(123)

-- Get room name
local roomName = fibaro.getRoomName(roomId)

-- Wake up dead Z-Wave device
fibaro.wakeUpDeadDevice(456)
```

### Alarm System

```lua
-- Control partition alarm
fibaro.alarm(1, "arm")    -- Arm partition 1
fibaro.alarm(1, "disarm") -- Disarm partition 1

-- Control main house alarm
fibaro.__houseAlarm("arm")    -- Arm main alarm
fibaro.__houseAlarm("disarm") -- Disarm main alarm

-- Check alarm states
if fibaro.isHomeBreached() then
    print("Home is breached!")
end

if fibaro.isPartitionBreached(1) then
    print("Partition 1 is breached!")
end

-- Get arm states
local partitionState = fibaro.getPartitionArmState(1)
local homeState = fibaro.getHomeArmState()
```

### Variables

```lua
-- Global variables
fibaro.setGlobalVariable("myVar", "hello")
local value, modified = fibaro.getGlobalVariable("myVar")

-- Scene variables
fibaro.setSceneVariable("myVar", "hello")
local value = fibaro.getSceneVariable("myVar")
```

### Scenes

```lua
-- Execute scenes
fibaro.scene("execute", {1, 2, 3})

-- Kill scenes
fibaro.scene("kill", {1, 2, 3})
```

### Profiles

```lua
-- Activate user profile
fibaro.profile("activate", 1)
```

### Timers

```lua
-- Set timeout with error handling
local timer = fibaro.setTimeout(5000, function()
    print("5 seconds passed")
end, function(error)
    print("Timer error:", error)
end)

-- Clear timeout
fibaro.clearTimeout(timer)
```

### Notifications

```lua
-- Send alerts
fibaro.alert("push", {1, 2, 3}, "Alert message")
fibaro.alert("email", {1, 2, 3}, "Email alert")
fibaro.alert("simplePush", {1, 2, 3}, "SimplePush alert")
```

### Events

```lua
-- Emit custom events
fibaro.emitCustomEvent("myCustomEvent")
```

### System

```lua
-- Pause execution
fibaro.sleep(1000) -- 1 second

-- Configure async handler
fibaro.useAsyncHandler(true)
```

## QuickApp Development

### Basic QuickApp Structure

```lua
-- Define your QuickApp
local MyQuickApp = class('MyQuickApp', QuickApp)

function MyQuickApp:onInit()
    self:debug("QuickApp initialized")
    self:updateProperty("status", "ready")
    self:setupUICallbacks()
end

function MyQuickApp:onAction()
    self:debug("Action triggered")
    self:updateProperty("status", "active")
end

-- UI callback example
function MyQuickApp:buttonPressed()
    self:debug("Button was pressed")
    self:updateView("button", "text", "Pressed!")
end

-- Create and initialize QuickApp
local device = {id = 1, name = "Test Device", properties = {}}
local qa = MyQuickApp(device)
```

### QuickApp Methods

#### Logging
```lua
self:debug("Debug message")
self:trace("Trace message")
self:warning("Warning message")
self:error("Error message")
```

#### Properties
```lua
self:updateProperty("status", "active")
local value = self:getProperty("status")
```

#### UI Management
```lua
self:updateView("button", "text", "New Text")
self:updateView("slider", "value", 50)
self:registerUICallback("button", "onReleased", self.buttonPressed)
```

#### Interfaces
```lua
if self:hasInterface("com.fibaro.multilevelSwitch") then
    print("Device has multilevel switch interface")
end

self:addInterfaces({"com.fibaro.binarySwitch"})
self:deleteInterfaces({"com.fibaro.multilevelSwitch"})
```

#### Device Management
```lua
self:setName("New Device Name")
self:setEnabled(true)
```

### UI Elements

```lua
-- Button
{
    button = "myButton",
    text = "Click Me",
    onReleased = "buttonPressed"
}

-- Slider
{
    slider = "mySlider",
    text = "Brightness",
    min = 0,
    max = 100,
    value = 50,
    onChanged = "sliderChanged"
}

-- Label
{
    label = "myLabel",
    text = "Status: Ready"
}

-- Switch
{
    switch = "mySwitch",
    text = "Enable Feature",
    value = false,
    onChanged = "switchChanged"
}
```

## Examples

### Basic Device Control

```lua
-- Load Fibaro modules
require("lua.fibaro")

-- Get all devices
local devices = fibaro.getDevices()
print("Found", #devices, "devices")

-- Find all lights
local lights = fibaro.getDevicesID({type = "com.fibaro.multilevelSwitch"})
print("Found", #lights, "lights")

-- Turn on all lights
for _, lightId in ipairs(lights) do
    fibaro.call(lightId, "turnOn")
end

-- Set brightness to 50%
for _, lightId in ipairs(lights) do
    fibaro.call(lightId, "setValue", 50)
end
```

### Alarm Control

```lua
-- Check current alarm state
if fibaro.isHomeBreached() then
    print("Home is currently breached!")
else
    print("Home is secure")
end

-- Arm the alarm
fibaro.alarm(1, "arm")
print("Alarm armed")

-- Check arm state
local state = fibaro.getPartitionArmState(1)
print("Partition 1 state:", state)
```

### Variable Management

```lua
-- Set global variable
fibaro.setGlobalVariable("lastUpdate", os.date())

-- Get global variable
local lastUpdate, modified = fibaro.getGlobalVariable("lastUpdate")
print("Last update:", lastUpdate)
print("Modified:", modified)

-- Set scene variable
fibaro.setSceneVariable("counter", 42)
local counter = fibaro.getSceneVariable("counter")
print("Counter:", counter)
```

### QuickApp with UI

```lua
local MyQuickApp = class('MyQuickApp', QuickApp)

function MyQuickApp:onInit()
    self:debug("Starting QuickApp with UI")
    self:updateProperty("status", "ready")
    
    -- Setup UI callbacks
    self:registerUICallback("onButton", "onReleased", self.onButtonPressed)
    self:registerUICallback("brightnessSlider", "onChanged", self.onBrightnessChanged)
end

function MyQuickApp:onButtonPressed()
    self:debug("Button pressed!")
    self:updateView("statusLabel", "text", "Button was pressed at " .. os.date())
    
    -- Toggle light
    local currentValue = self:getProperty("value")
    local newValue = currentValue > 0 and 0 or 100
    self:updateProperty("value", newValue)
    self:updateView("brightnessSlider", "value", newValue)
end

function MyQuickApp:onBrightnessChanged(value)
    self:debug("Brightness changed to:", value)
    self:updateProperty("value", value)
    self:updateView("statusLabel", "text", "Brightness: " .. value .. "%")
end

-- Create and initialize
local device = {
    id = 1,
    name = "My Light Controller",
    properties = {value = 0}
}
local qa = MyQuickApp(device)
```

### Network Integration

```lua
local net = require("plua.net")

-- HTTP request to external API
local http = net.HTTPClient()
http:request("https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY", {
    success = function(response)
        local data = json.decode(response.body)
        local temp = data.main.temp
        print("London temperature:", temp, "K")
        
        -- Update device property with temperature
        fibaro.setGlobalVariable("londonTemp", temp)
    end,
    error = function(status)
        print("Weather API error:", status)
    end
})
```

## Debugging

### Enable Debugging

```bash
# Run with MobDebug server
plua --fibaro --debugger my_quickapp.lua

# Custom debugger port
plua --fibaro --debugger --debugger-port 8820 my_quickapp.lua
```

### Debugging in VS Code

1. Install the Lua extension for VS Code
2. Configure launch.json (see VS Code Configuration section above)
3. Set breakpoints in your QuickApp code
4. Use the "PLua Fibaro Debugger" launch configuration

### Debug Output

```lua
-- Debug messages will appear in the console
self:debug("This is a debug message")
self:trace("This is a trace message")
self:warning("This is a warning")
self:error("This is an error")
```

## Testing

### Unit Testing

```lua
-- Test device API
local devices = fibaro.getDevices()
assert(#devices > 0, "Should have at least one device")

-- Test alarm API
local isBreached = fibaro.isHomeBreached()
assert(type(isBreached) == "boolean", "isHomeBreached should return boolean")

-- Test variable API
fibaro.setGlobalVariable("testVar", "testValue")
local value = fibaro.getGlobalVariable("testVar")
assert(value == "testValue", "Variable should be set correctly")
```

### Integration Testing

```lua
-- Test complete workflow
local function testLightControl()
    local lights = fibaro.getDevicesID({type = "com.fibaro.multilevelSwitch"})
    if #lights > 0 then
        local lightId = lights[1]
        
        -- Turn on
        fibaro.call(lightId, "turnOn")
        local value = fibaro.getValue(lightId, "value")
        assert(value > 0, "Light should be on")
        
        -- Turn off
        fibaro.call(lightId, "turnOff")
        value = fibaro.getValue(lightId, "value")
        assert(value == 0, "Light should be off")
        
        print("Light control test passed!")
    end
end

testLightControl()
```

## Building Executables

### Local Builds

Create standalone executables using PyInstaller:

```bash
# macOS (Apple Silicon or Intel)
python scripts/build.py

# macOS Intel specifically
python scripts/build_macos_intel.py

# Test all local builds
./scripts/test_release_builds.sh
```

### Automated Builds

- **Windows**: Built automatically via GitHub Actions on every push/PR
- **macOS Intel & Apple Silicon**: Built automatically when creating releases
- **All platforms**: Built and released together when you create a GitHub release

The executables will be created in `dist/` directory and include all dependencies.

## Extension System

PLua uses a decorator-based extension system that automatically registers Python functions to the Lua environment. Functions are organized into categories and available through the `_PY` table.

### Adding Custom Extensions

Create a new Python file and use the `@registry.register` decorator:

```python
from extensions.registry import registry

@registry.register(description="My custom function", category="custom")
def my_function(arg1, arg2):
    """My custom function that will be available in Lua"""
    return arg1 + arg2
```

### Available Function Categories

See the Standard Lua Development section for a complete list of available `_PY` functions.

## Web Server

PLua includes a web server that runs in a separate process, allowing it to receive HTTP callbacks even when Lua execution is paused by the debugger. The server communicates with Lua via a message queue system.

**Web Server Functions:**
- `start_web_server(port, host)` - Start web server on specified port and host
- `stop_web_server()` - Stop the web server
- `is_web_server_running()` - Check if server is running
- `get_web_server_status()` - Get server status information
- `get_web_server_message()` - Get next HTTP request (non-blocking)
- `register_web_callback(event_type, callback)` - Register Lua callback for HTTP events
- `unregister_web_callback(event_type, callback)` - Unregister callback
- `start_web_message_processing()` - Start automatic message processing
- `stop_web_message_processing()` - Stop message processing

**Usage Examples:**

```lua
-- Start web server
local success, message = _PY.start_web_server(8080, "0.0.0.0")
print("Server started:", success, message)

-- Register callback for HTTP requests
local function handle_request(request)
    print("Received", request.method, "request to", request.path)
    if request.body then
        print("Body:", _PY.to_json(request.body))
    end
end

_PY.register_web_callback("http_request", handle_request)

-- Start message processing
_PY.start_web_message_processing()

-- Check server status
local status = _PY.get_web_server_status()
print("Server running:", status.running)
print("Port:", status.port)
```

**Features:**
- **Independent Process**: Server runs separately from Lua execution
- **JSON Communication**: All messages use JSON format for simplicity
- **Callback System**: Register Lua functions to handle HTTP requests
- **Multiple HTTP Methods**: Supports GET, POST, PUT, DELETE
- **Query Parameters**: Automatically parses URL query parameters
- **JSON Body Parsing**: Automatically parses JSON request bodies
- **Status Endpoints**: Built-in status and health check endpoints

**Demo Scripts:**
- `examples/web_server_demo.lua` - Basic web server usage
- `examples/web_server_status_demo.lua` - Advanced status page example

## Bundled Files

When PLua is built as a standalone executable using PyInstaller, additional files (like demos, examples, and Lua modules) are bundled with the executable. These files are accessible from within Lua scripts using the bundled files API.

**Bundled Files Functions:**
- `bundled_file_read(path)` - Read contents of a bundled file
- `bundled_file_exists(path)` - Check if a bundled file exists
- `bundled_file_list(directory)` - List files in a bundled directory
- `bundled_file_path(path)` - Get the full path to a bundled file

**Usage Examples:**

```lua
-- Check if a bundled file exists
if _PY.bundled_file_exists("demos/basic.lua") then
    print("Demo file exists")
end

-- Read a bundled file
local content = _PY.bundled_file_read("demos/basic.lua")
if content then
    print("Demo file content length:", #content)
end

-- List files in bundled directory
local files = _PY.bundled_file_list("demos")
if files then
    print("Bundled demo files:")
    for i, file in ipairs(files) do
        print("  " .. i .. ": " .. file)
    end
end

-- Get full path to bundled file
local full_path = _PY.bundled_file_path("examples/http_demo.lua")
print("Full path:", full_path)
```

**Available Bundled Directories:**
- `demos/` - Demo scripts and libraries
- `examples/` - Example scripts
- `lua/` - Lua modules and libraries
- `test/` - Test scripts

**Note:** Bundled files are only available when running from a PyInstaller-built executable. When running from source, these functions will work with files in the project directory.