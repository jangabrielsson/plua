# PLua - Lua Interpreter in Python

A powerful Lua interpreter implemented in Python using the Lupa library. PLua provides a complete Lua 5.4 environment with an extensive modular extension system, async networking capabilities, debugging support, and a rich set of Python-integrated functions.

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

## Quick Start

```bash
# Install in development mode
uv pip install -e .

# Run a Lua script
plua [your_lua_file.lua]

# Or use the module form
python -m plua [your_lua_file.lua]
```

## Usage Examples

### Running Lua Scripts

```bash
# Using uv (recommended)
uv run plua script.lua

# Direct execution
plua script.lua

# Module form
python -m plua script.lua
```

### Executing Lua Code

```bash
# Execute a single line of Lua code
uv run plua -e "print('Hello, World!')"

# Direct execution
plua -e "print('Hello, World!')"

# Execute multiple lines
uv run plua -e "x=10" -e "print(x)"

# Module form
python -m plua -e "print('Hello, World!')"
```

### Interactive Mode

```bash
# Start interactive shell
uv run plua -i

# Or simply
uv run plua

# Direct execution
plua -i

# Module form
python -m plua -i
```

### Debugging

```bash
# Run with MobDebug server (default port 8818)
uv run plua --debugger script.lua

# Custom debugger port
uv run plua --debugger --debugger-port 8820 script.lua

# With Fibaro library
uv run plua --debugger -e "require('lua.fibaro')" script.lua
```

### Loading Libraries

```bash
# Load socket and debugger libraries
uv run plua -l socket -l debugger script.lua

# Interactive mode with libraries
uv run plua -l socket -i
```

### Command Line Options

- `file` - Lua file to execute
- `-e, --execute` - Execute Lua code string (can be used multiple times)
- `-i, --interactive` - Start interactive shell
- `-l, --library` - Load library before executing script (can be used multiple times)
- `-d, --debug` - Enable debug output
- `--debugger` - Start MobDebug server for remote debugging
- `--debugger-port PORT` - Port for MobDebug server (default: 8818)
- `-v, --version` - Show version information

## Building Executable

Create a standalone executable using PyInstaller:

```bash
# Using uv
uv run python build.py

# Using pip
python build.py
```

The executable will be created in `dist/` directory and includes all dependencies.
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

#### Timer Functions
- `setTimeout(function, ms)` - Schedule a function to run after ms milliseconds
- `clearTimeout(reference)` - Cancel a timer using its reference ID
- `has_active_timers()` - Check if there are active timers

#### I/O Functions
- `input_lua(prompt)` - Get user input with optional prompt
- `read_file(filename)` - Read and return file contents
- `write_file(filename, content)` - Write content to a file

#### JSON Functions
- `parse_json(json_string)` - Parse JSON string to table
- `to_json(data)` - Convert data to JSON string
- `pretty_print(data, indent)` - Pretty print table as JSON string
- `print_table(data, indent)` - Print table in pretty JSON format

#### HTTP Functions
- `http_request_sync(url_or_table)` - Synchronous HTTP request (LuaSocket style)
- `http_request_async(lua_runtime, url_or_table, callback)` - Asynchronous HTTP request

#### TCP Functions (Asynchronous with Callbacks)
- `tcp_connect(host, port, callback)` - Connect to TCP server asynchronously
- `tcp_write(conn_id, data, callback)` - Write data to TCP connection asynchronously
- `tcp_read(conn_id, max_bytes, callback)` - Read data from TCP connection asynchronously
- `tcp_close(conn_id, callback)` - Close TCP connection
- `tcp_set_timeout(conn_id, timeout_seconds, callback)` - Set TCP timeout asynchronously
- `tcp_get_timeout(conn_id, callback)` - Get TCP timeout asynchronously

#### TCP Functions (Synchronous - No Callbacks)
- `tcp_connect_sync(host, port)` - Connect to TCP server, returns `(success, conn_id, message)`
- `tcp_write_sync(conn_id, data)` - Write data to TCP connection, returns `(success, bytes_written, message)`
- `tcp_read_sync(conn_id, pattern)` - Read data from TCP connection using pattern, returns `(success, data, message)`
  - Patterns: `'*a'` (all data), `'*l'` (line), or number (bytes)
  - **Non-blocking behavior**: When socket has no data available (Errno 35), returns `(true, "", "No data available")` instead of error
- `tcp_close_sync(conn_id)` - Close TCP connection, returns `(success, message)`
- `tcp_set_timeout_sync(conn_id, timeout_seconds)` - Set TCP timeout, returns `(success, message)`
  - Use `0` for non-blocking mode
  - Use `nil` for blocking mode
  - Use positive number for timeout in seconds
- `tcp_get_timeout_sync(conn_id)` - Get TCP timeout, returns `(success, timeout_seconds, message)`

#### UDP Functions (Asynchronous with Callbacks)
- `udp_connect(host, port, callback)` - Connect to UDP server asynchronously
- `udp_write(conn_id, data, host, port, callback)` - Write data to UDP connection asynchronously
- `udp_read(conn_id, max_bytes, callback)` - Read data from UDP connection asynchronously
- `udp_close(conn_id, callback)` - Close UDP connection

#### Network Utility Functions
- `get_hostname()` - Get current hostname
- `get_local_ip()` - Get local IP address
- `is_port_available(port, host)` - Check if port is available for binding
- `has_active_network_operations()` - Check if there are active network operations

#### File System Functions
- `file_exists(filename)` - Check if file exists
- `get_file_size(filename)` - Get file size in bytes
- `list_files(directory)` - List files in directory
- `create_directory(path)` - Create directory

#### System Functions
- `get_time()` - Get current timestamp in seconds
- `sleep(seconds)` - Sleep for specified seconds (non-blocking)
- `get_python_version()` - Get Python version information

#### Configuration Functions
- `get_env_var(name, default)` - Get environment variable value
- `set_env_var(name, value)` - Set environment variable
- `get_all_env_vars()` - Get all environment variables as a table (with .env file precedence)

#### Utility Functions
- `list_extensions()` - List all available Python extensions

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

-- POST request with JSON data
local post_data = {
    url = "https://httpbin.org/post",
    method = "POST",
    headers = {["Content-Type"] = "application/json"},
    body = '{"name": "John", "age": 30}'
}

local post_response = _PY.http_request_sync(post_data)
if post_response and not post_response.error then
    print("POST Status:", post_response.code)
    local parsed = _PY.parse_json(post_response.body)
    if parsed then
        print("Posted data:", _PY.pretty_print(parsed.json))
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

-- Non-blocking socket example
local success, conn_id, message = _PY.tcp_connect_sync("httpbin.org", 80)
if success then
    -- Set to non-blocking mode
    _PY.tcp_set_timeout_sync(conn_id, 0)
    
    -- Try to read data
    local read_success, data, read_message = _PY.tcp_read_sync(conn_id, 1024)
    if read_success then
        if #data > 0 then
            print("Data received:", #data, "bytes")
        else
            print("No data available (normal for non-blocking)")
        end
    end
    
    _PY.tcp_close_sync(conn_id)
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

### Debugging

```lua
-- Start with debugging enabled
-- Run: plua --debugger script.lua

-- Load fibaro module for MobDebug integration
require('lua.fibaro')

-- Your Lua code here
local function my_function()
    local x = 10
    local y = 20
    local result = x + y
    print("Result:", result)
end

my_function()
```

### Interactive Mode

```bash
# Start interactive shell
plua -i

# In the shell:
plua> local data = {name="John", age=30}
plua> _PY.print_table(data)
plua> _PY.list_extensions()
plua> exit
```

## Fibaro HC3 Lua API Support

PLua includes comprehensive support for the Fibaro HomeCenter 3 Lua API through the `fibaro.lua` module. This provides access to HomeCenter 3 devices, scenes, variables, and system functions.

### Architecture

The Fibaro API integration uses an **embedded API server** architecture:

- **Embedded API Server**: A FastAPI server runs within the PLua interpreter process
- **Direct Lua Integration**: API calls are handled directly through `_PY.fibaroapi()` function
- **External Redirect Support**: Can redirect requests to real HC3 servers for testing
- **Non-blocking HTTP**: Uses asyncio-based HTTP requests to avoid blocking the main thread

### API Request Flow

1. **Lua Code** calls `api.get("/devices")` or similar
2. **Embedded API Server** receives the request via `_PY.fibaroapi()`
3. **Lua Handler** processes the request and can:
   - Return mock data for testing
   - Return a redirect response to call external HC3 server
   - Return actual data from external server
4. **HTTP Client** (if redirect) makes non-blocking request to external server
5. **Response** is returned to the original Lua code

### Redirect to External HC3 Server

Lua handlers can redirect requests to real HC3 servers:

```lua
-- In your Lua handler
function handle_devices_request()
    -- Return redirect to external HC3 server
    return {
        _redirect = true,
        hostname = "http://192.168.1.57/",
        port = 80
    }
end
```

The embedded API server will automatically:
1. Detect the redirect response
2. Make an HTTP request to the external server
3. Return the actual data from the external server

### HTTP Request Improvements

- **Non-blocking**: `_PY.http_request_sync()` uses asyncio internally with threading
- **Legacy Fallback**: `_PY.http_request_sync_legacy()` available for compatibility
- **Timeout Handling**: Configurable timeouts with fallback mechanisms
- **Error Recovery**: Automatic fallback to legacy implementation on errors

**Available Functions:**

**Device Management:**
- `fibaro.call(deviceId, action, ...)` - Call device actions
- `fibaro.callhc3(deviceId, action, ...)` - Call device actions via HC3 API
- `fibaro.callGroupAction(actionName, actionData)` - Execute group actions
- `fibaro.get(deviceId, prop)` - Get device property with modification time
- `fibaro.getValue(deviceId, propertyName)` - Get device property value
- `fibaro.getType(deviceId)` - Get device type
- `fibaro.getName(deviceId)` - Get device name
- `fibaro.getRoomID(deviceId)` - Get device room ID
- `fibaro.getSectionID(deviceId)` - Get device section ID
- `fibaro.getRoomName(roomId)` - Get room name by ID
- `fibaro.getRoomNameByDeviceID(deviceId)` - Get room name for device
- `fibaro.getDevicesID(filter)` - Get device IDs with optional filtering
- `fibaro.getIds(devices)` - Extract IDs from device objects
- `fibaro.wakeUpDeadDevice(deviceID)` - Wake up dead Z-Wave devices

**Alarm System:**
- `fibaro.alarm(partitionId, action)` - Control partition alarm (arm/disarm)
- `fibaro.__houseAlarm(action)` - Control main house alarm (arm/disarm)
- `fibaro.isHomeBreached()` - Check if home is breached
- `fibaro.isPartitionBreached(partitionId)` - Check if partition is breached
- `fibaro.getPartitionArmState(partitionId)` - Get partition arm state
- `fibaro.getHomeArmState()` - Get overall home arm state

**Variables:**
- `fibaro.getGlobalVariable(name)` - Get global variable with modification time
- `fibaro.setGlobalVariable(name, value)` - Set global variable
- `fibaro.getSceneVariable(name)` - Get scene variable
- `fibaro.setSceneVariable(name, value)` - Set scene variable

**Scenes:**
- `fibaro.scene(action, ids)` - Execute or kill scenes

**Profiles:**
- `fibaro.profile(action, id)` - Activate user profile

**Timers:**
- `fibaro.setTimeout(timeout, action, errorHandler)` - Set timeout with error handling
- `fibaro.clearTimeout(ref)` - Clear timeout

**Notifications:**
- `fibaro.alert(alertType, ids, notification)` - Send alerts (email/push/simplePush)

**Events:**
- `fibaro.emitCustomEvent(name)` - Emit custom events

**System:**
- `fibaro.sleep(ms)` - Pause execution
- `fibaro.useAsyncHandler(value)` - Configure async handler

**Usage Examples:**

```lua
-- Load the fibaro module
require('lua.fibaro')

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

-- Set global variable
fibaro.setGlobalVariable("myVar", "hello")

-- Get global variable
local value, modified = fibaro.getGlobalVariable("myVar")

-- Control alarm
fibaro.alarm(1, "arm")  -- Arm partition 1
fibaro.alarm("disarm")  -- Disarm main alarm

-- Check alarm state
if fibaro.isHomeBreached() then
    print("Home is breached!")
end

-- Set timeout
local timer = fibaro.setTimeout(5000, function()
    print("5 seconds passed")
end)

-- Send notification
fibaro.alert("push", {1, 2, 3}, "Alert message")

-- Execute scene
fibaro.scene("execute", {1, 2, 3})

-- Wake up dead device
fibaro.wakeUpDeadDevice(456)
```

**Note:** The `hub` variable is also available as an alias for `fibaro`.

### Additional Lua Modules

#### class.lua
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

#### json.lua
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

#### net.lua
Network utilities for HTTP and TCP operations:

**HTTP Client:**
```lua
local net = require("plua.net")
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
```

**TCP Socket:**
```lua
local net = require("plua.net")
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

**UDP Socket:**
```lua
local net = require("plua.net")
local udp = net.UDPSocket({
    success = function(data) print("UDP data received") end,
    error = function(err) print("UDP Error:", err) end
})

udp:connect("example.com", 53, {
    success = function() 
        udp:write("UDP message", {
            success = function()
                udp:read({
                    success = function(data) print("UDP Data:", data) end
                })
            end
        })
    end
})
```

#### quickapp.lua
QuickApp base class for developing Fibaro QuickApps:

```lua
local QuickApp = require("plua.quickapp")

-- Define your QuickApp
local MyQuickApp = class('MyQuickApp', QuickApp)

function MyQuickApp:onInit()
    self:debug("QuickApp initialized")
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
local qa = MyQuickApp(deviceObject)
```

**QuickApp Methods:**
- `:debug(...)`, `:trace(...)`, `:warning(...)`, `:error(...)` - Logging
- `:updateProperty(name, value)` - Update device property
- `:updateView(element, property, value)` - Update UI element
- `:registerUICallback(element, event, function)` - Register UI callbacks
- `:hasInterface(name)` - Check if device has interface
- `:addInterfaces(interfaces)` - Add device interfaces
- `:deleteInterfaces(interfaces)` - Remove device interfaces
- `:setName(name)` - Set device name
- `:setEnabled(enabled)` - Set device enabled state

### Environment Variables

Configure HC3 connection via environment variables:
- `HC3_URL` - HomeCenter 3 URL (e.g., "https://192.168.1.100")
- `HC3_USER` - Username for API access
- `HC3_PASSWORD` - Password for API access

### Complete Usage Examples

**Basic QuickApp Development:**
```lua
-- Load Fibaro modules
require("lua.fibaro")

-- Create QuickApp
local MyQA = class('MyQA', QuickApp)
function MyQA:onInit()
    self:debug("Starting QuickApp")
    self:updateProperty("status", "ready")
end

-- Test locally
local device = {id = 1, name = "Test Device", properties = {}}
local qa = MyQA(device)
```

**API Testing:**
```lua
require("lua.fibaro")

-- Test device retrieval
local devices = fibaro.getDevices()
print("Found", #devices, "devices")

-- Test alarm control
fibaro.alarm("arm")
local partitions = fibaro.getPartitions()
```

**Network Operations:**
```lua
local net = require("plua.net")

-- HTTP request to external API
local http = net.HTTPClient()
http:request("https://httpbin.org/json", {
    success = function(response)
        local data = json.decode(response.body)
        print("Title:", data.slideshow.title)
    end
})
```

### Debugging

Enable debugging with MobDebug:
```bash
plua --debugger -e "require('lua.fibaro')" script.lua
```

This allows remote debugging of QuickApps using VS Code or other IDEs with MobDebug support.

### Web Server

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

### Bundled Files

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