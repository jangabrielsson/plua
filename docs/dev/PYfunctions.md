# EPLua _PY Functions Reference

This document provides a comprehensive reference for all `_PY.*` functions available in EPLua. The `_PY` table serves as a bridge between Lua and Python, providing access to Python functionality from within Lua scripts.

## Table of Contents

- [Timer Functions](#timer-functions)
- [System & Platform Functions](#system--platform-functions)
- [File System Functions](#file-system-functions)
- [Network Functions](#network-functions)
- [Threading Functions](#threading-functions)
- [Web Server Functions](#web-server-functions)
- [GUI Functions](#gui-functions)
- [Utility Functions](#utility-functions)
- [JSON Functions](#json-functions)
- [Environment Functions](#environment-functions)
- [Internal Functions](#internal-functions)

---

## Timer Functions

### `_PY.setTimeout(callback, ms)`
**Defined in:** Lua (`init.lua`)  
**Description:** Creates a timer that executes a callback function once after a specified delay.

**Parameters:**
- `callback` (function): The function to execute when the timer expires
- `ms` (number): Delay in milliseconds

**Returns:** Timer ID (number) that can be used with `clearTimeout`

**Example:**
```lua
local timerId = _PY.setTimeout(function()
    print("Timer executed after 1 second!")
end, 1000)
```

### `_PY.clearTimeout(id)`
**Defined in:** Lua (`init.lua`)  
**Description:** Cancels a timeout timer created with `setTimeout`.

**Parameters:**
- `id` (number): Timer ID returned by `setTimeout`

**Returns:** None

**Example:**
```lua
local timerId = _PY.setTimeout(function() print("This won't run") end, 5000)
_PY.clearTimeout(timerId)  -- Cancel the timer
```

### `_PY.setInterval(callback, ms)`
**Defined in:** Lua (`init.lua`)  
**Description:** Creates a timer that repeatedly executes a callback function at specified intervals.

**Parameters:**
- `callback` (function): The function to execute on each interval
- `ms` (number): Interval in milliseconds

**Returns:** Interval ID (number) that can be used with `clearInterval`

**Example:**
```lua
local count = 0
local intervalId = _PY.setInterval(function()
    count = count + 1
    print("Interval tick:", count)
    if count >= 5 then
        _PY.clearInterval(intervalId)
    end
end, 1000)
```

### `_PY.clearInterval(id)`
**Defined in:** Lua (`init.lua`)  
**Description:** Cancels an interval timer created with `setInterval`.

**Parameters:**
- `id` (number): Interval ID returned by `setInterval`

**Returns:** None

---

## System & Platform Functions

### `_PY.get_time()`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Returns the current time as a Unix timestamp.

**Returns:** Current time in seconds (number)

**Example:**
```lua
local timestamp = _PY.get_time()
print("Current time:", timestamp)
```

### `_PY.sleep(seconds)`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Blocks execution for the specified number of seconds. Note: This is blocking - prefer using timers for async operations.

**Parameters:**
- `seconds` (number): Number of seconds to sleep

**Returns:** None

### `_PY.get_platform()`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Returns basic platform information as a Lua table.

**Returns:** Table with platform information

**Example:**
```lua
local platform = _PY.get_platform()
print("System:", platform.system)
print("Machine:", platform.machine)
```

### `_PY.get_system_info()`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Returns comprehensive system information including platform, environment, and runtime details.

**Returns:** Table with detailed system information

**Example:**
```lua
local info = _PY.get_system_info()
print("OS:", info.platform.system)
print("Python version:", info.platform.python_version)
print("Current directory:", info.environment.cwd)
print("Process ID:", info.runtime.pid)
```

---

## File System Functions

### `_PY.read_file(filename)`
**Defined in:** Python (`extensions.py`)  
**Description:** Reads the contents of a file.

**Parameters:**
- `filename` (string): Path to the file to read

**Returns:** File contents (string) or error message

**Example:**
```lua
local content = _PY.read_file("config.txt")
print("File content:", content)
```

### `_PY.write_file(filename, content)`
**Defined in:** Python (`extensions.py`)  
**Description:** Writes content to a file.

**Parameters:**
- `filename` (string): Path to the file to write
- `content` (string): Content to write to the file

**Returns:** Success status (boolean)

**Example:**
```lua
local success = _PY.write_file("output.txt", "Hello, World!")
if success then
    print("File written successfully")
end
```

### `_PY.list_directory(path)`
**Defined in:** Python (`extensions.py`)  
**Description:** Lists the contents of a directory.

**Parameters:**
- `path` (string): Directory path to list (defaults to current directory)

**Returns:** Table with directory entries and metadata

**Example:**
```lua
local dir_info = _PY.list_directory("/path/to/directory")
print("Number of entries:", dir_info.count)
for i, entry in ipairs(dir_info.entries) do
    print(entry.name, entry.is_file and "FILE" or "DIR")
end
```

---

## Network Functions

### `_PY.call_http(url, options, callback_id)`
**Defined in:** Python (`network.py`)  
**Description:** Makes an HTTP request with the specified options and calls back with the result.

**Parameters:**
- `url` (string): The URL to request
- `options` (table): Request options (method, headers, data, etc.)
- `callback_id` (number): Callback ID from `registerCallback`

**Returns:** None (result delivered via callback)

**Example:**
```lua
local callback_id = _PY.registerCallback(function(response)
    if response.error then
        print("Error:", response.error)
    else
        print("Status:", response.status)
        print("Response:", response.text)
    end
end)

_PY.call_http("https://httpbin.org/get", {
    method = "GET",
    headers = {["User-Agent"] = "EPLua/1.0"}
}, callback_id)
```

---



---

## Web Server Functions

### `_PY.start_web_server(host, port)`
**Defined in:** Python (`web_server.py`)  
**Description:** Starts the FastAPI web server.

**Parameters:**
- `host` (string): Host to bind to (default: "127.0.0.1")
- `port` (number): Port to bind to (default: 8000)

**Returns:** Table with operation result and server info

**Example:**
```lua
local result = _PY.start_web_server("127.0.0.1", 8000)
if result.success then
    print("Server started at:", result.server_info.url)
else
    print("Failed to start server:", result.message)
end
```

### `_PY.stop_web_server()`
**Defined in:** Python (`web_server.py`)  
**Description:** Stops the web server.

**Returns:** Table with operation result

### `_PY.get_web_server_status()`
**Defined in:** Python (`web_server.py`)  
**Description:** Gets the current status of the web server.

**Returns:** Table with server status information

---

## GUI Functions

### `_PY.gui_available()`
**Defined in:** Python (`extensions.py`)  
**Description:** Checks if GUI (tkinter) is available.

**Returns:** Boolean indicating GUI availability

### `_PY.html_rendering_available()`
**Defined in:** Python (`extensions.py`)  
**Description:** Checks if HTML rendering is available in GUI windows.

**Returns:** Boolean indicating HTML rendering capability

### `_PY.get_html_engine()`
**Defined in:** Python (`extensions.py`)  
**Description:** Returns the name of the HTML rendering engine.

**Returns:** String with engine name (e.g., "tkhtmlview")

### `_PY.create_window(window_id, title, width, height)`
**Defined in:** Python (`extensions.py`)  
**Description:** Creates a new GUI window.

**Parameters:**
- `window_id` (string): Unique identifier for the window
- `title` (string): Window title
- `width` (number): Window width in pixels
- `height` (number): Window height in pixels

**Returns:** Success status (boolean)

### `_PY.set_window_html(window_id, html_content)`
**Defined in:** Python (`extensions.py`)  
**Description:** Sets HTML content in a window.

**Parameters:**
- `window_id` (string): Window identifier
- `html_content` (string): HTML content to display

**Returns:** Success status (boolean)

### `_PY.set_window_url(window_id, url)`
**Defined in:** Python (`extensions.py`)  
**Description:** Loads a URL in a window.

**Parameters:**
- `window_id` (string): Window identifier
- `url` (string): URL to load

**Returns:** Success status (boolean)

### `_PY.show_window(window_id)`
**Defined in:** Python (`extensions.py`)  
**Description:** Shows/displays a window.

**Parameters:**
- `window_id` (string): Window identifier

**Returns:** Success status (boolean)

### `_PY.hide_window(window_id)`
**Defined in:** Python (`extensions.py`)  
**Description:** Hides a window.

**Parameters:**
- `window_id` (string): Window identifier

**Returns:** Success status (boolean)

### `_PY.close_window(window_id)`
**Defined in:** Python (`extensions.py`)  
**Description:** Closes and destroys a window.

**Parameters:**
- `window_id` (string): Window identifier

**Returns:** Success status (boolean)

### `_PY.list_windows()`
**Defined in:** Python (`extensions.py`)  
**Description:** Lists all open windows.

**Returns:** String with window information or "No windows open"

---

## Utility Functions

### `_PY.print(...)`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Enhanced print function with logging integration.

**Parameters:**
- `...` (any): Values to print

**Returns:** None

### `_PY.log(level, message)`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Logging function with different log levels.

**Parameters:**
- `level` (string): Log level ("DEBUG", "INFO", "WARNING", "ERROR")
- `message` (string): Message to log

**Returns:** None

### `_PY.math_add(a, b)`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Adds two numbers (example utility function).

**Parameters:**
- `a` (number): First number
- `b` (number): Second number

**Returns:** Sum of the two numbers

### `_PY.random_number(min_val, max_val)`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Generates a random number within the specified range.

**Parameters:**
- `min_val` (number): Minimum value (default: 0)
- `max_val` (number): Maximum value (default: 1)

**Returns:** Random number (number)

---

## JSON Functions

### `_PY.parse_json(json_string)`
**Defined in:** Python (`lua_bindings.py`, `extensions.py`)  
**Description:** Parses a JSON string and returns the corresponding Lua data structure.

**Parameters:**
- `json_string` (string): JSON string to parse

**Returns:** Tuple of (parsed_data, error) or Lua table with parsed data

**Example:**
```lua
local data, error = _PY.parse_json('{"name": "John", "age": 30}')
if not error then
    print("Name:", data.name)
    print("Age:", data.age)
else
    print("Parse error:", error)
end
```

### `_PY.to_json(data)`
**Defined in:** Python (`extensions.py`)  
**Description:** Converts Lua data to JSON string.

**Parameters:**
- `data` (any): Data to convert to JSON

**Returns:** JSON string representation

**Example:**
```lua
local json_str = _PY.to_json({name = "John", age = 30})
print("JSON:", json_str)
```

---

## Environment Functions

### `_PY.get_env(var_name, default)`
**Defined in:** Python (`extensions.py`)  
**Description:** Gets an environment variable value.

**Parameters:**
- `var_name` (string): Environment variable name
- `default` (string): Default value if variable not found (default: "")

**Returns:** Environment variable value (string)

**Example:**
```lua
local home = _PY.get_env("HOME", "/unknown")
print("Home directory:", home)
```

### `_PY.set_env(var_name, value)`
**Defined in:** Python (`extensions.py`)  
**Description:** Sets an environment variable.

**Parameters:**
- `var_name` (string): Environment variable name
- `value` (string): Value to set

**Returns:** Success status (boolean)

---

## Internal Functions

These functions are primarily used internally by the EPLua engine and may not be needed in typical user scripts.

### `_PY.registerCallback(callback)`
**Defined in:** Lua (`init.lua`)  
**Description:** Registers a Lua callback function and returns an ID for use with async operations.

**Parameters:**
- `callback` (function): Callback function to register

**Returns:** Callback ID (number)

### `_PY.set_timeout(callback_id, delay_ms)`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Low-level timer function used internally by `setTimeout`.

**Parameters:**
- `callback_id` (number): Internal callback ID
- `delay_ms` (number): Delay in milliseconds

**Returns:** Python timer ID (string)

### `_PY.clear_timeout(timer_id)`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Low-level function used internally by `clearTimeout`.

**Parameters:**
- `timer_id` (string): Python timer ID

**Returns:** Boolean indicating success

### `_PY.get_timer_count()`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Returns the number of active timers in the Python timer manager.

**Returns:** Number of active timers (number)

### `_PY.timerExpired(id, ...)`
**Defined in:** Lua (`init.lua`)  
**Description:** Called internally when a timer expires to execute the associated callback.

**Parameters:**
- `id` (number): Timer callback ID
- `...` (any): Additional arguments passed to the callback

**Returns:** None

### `_PY.getPendingCallbackCount()`
**Defined in:** Lua (`init.lua`)  
**Description:** Returns the number of pending callbacks (used for CLI keep-alive logic).

**Returns:** Number of pending callbacks

### `_PY.getRunningIntervalsCount()`
**Defined in:** Lua (`init.lua`)  
**Description:** Returns the number of running intervals (used for CLI keep-alive logic).

**Returns:** Number of running intervals

### `_PY.mainLuaFile(filename)`
**Defined in:** Lua (`init.lua`)  
**Description:** Loads and executes a Lua file within the EPLua environment.

**Parameters:**
- `filename` (string): Path to the Lua file

**Returns:** None

### `_PY.luaFragment(str)`
**Defined in:** Lua (`init.lua`)  
**Description:** Executes a Lua code fragment.

**Parameters:**
- `str` (string): Lua code to execute

**Returns:** None

### `_PY.threadRequest(id, script, isJson)`
**Defined in:** Lua (`init.lua`)  
**Description:** Handles thread-safe script execution requests from the web API.

**Parameters:**
- `id` (string): Request ID
- `script` (string): Script or JSON function call
- `isJson` (boolean): Whether the script is a JSON function call

**Returns:** None

### `_PY.threadRequestResult(request_id, result)`
**Defined in:** Python (`lua_bindings.py`)  
**Description:** Handles the result of thread-safe script execution.

**Parameters:**
- `request_id` (string): Request ID
- `result` (any): Execution result

**Returns:** None

---

## Test Functions (Global Scope)

These functions are defined globally in `init.lua` for testing the JSON API functionality via the web server.

### `greet(name)`
**Defined in:** Lua (`init.lua`)  
**Description:** Test function that returns a greeting message.

**Parameters:**
- `name` (string): Name to greet

**Returns:** Greeting string

**Example:**
```lua
local message = greet("Alice")
print(message)  -- "Hello, Alice!"
```

### `add_numbers(a, b)`
**Defined in:** Lua (`init.lua`)  
**Description:** Test function that adds two numbers.

**Parameters:**
- `a` (number): First number
- `b` (number): Second number

**Returns:** Sum of the numbers

### `create_user_info(name, age, city)`
**Defined in:** Lua (`init.lua`)  
**Description:** Test function that creates a user information table.

**Parameters:**
- `name` (string): User's name
- `age` (number): User's age  
- `city` (string): User's city

**Returns:** Table with user information including timestamp

### `math_utils` Module
**Defined in:** Lua (`init.lua`)  
**Description:** Test module containing mathematical utility functions.

**Functions:**
- `math_utils.multiply(a, b)` - Multiplies two numbers
- `math_utils.factorial(n)` - Calculates factorial of n
- `math_utils.fibonacci(n)` - Calculates nth Fibonacci number

**Example:**
```lua
local result = math_utils.multiply(5, 3)  -- 15
local fact = math_utils.factorial(5)      -- 120
local fib = math_utils.fibonacci(10)      -- 55
```

---

## Convenience Functions (Examples)

These are example convenience functions found in the test scripts that demonstrate how to build higher-level APIs on top of the core `_PY` functions.

### HTTP Convenience Functions
**Defined in:** Example files (`network_example.lua`, `network_demo.lua`)

```lua
-- Simplified GET request
local function http_get(url, callback_id)
    _PY.call_http(url, {}, callback_id)
end

-- Simplified POST request with JSON
local function http_post(url, data, callback_id)
    _PY.call_http(url, {
        method = "POST",
        headers = {["Content-Type"] = "application/json"},
        data = data
    }, callback_id)
end
```

### Async/Await Style Functions
**Defined in:** Example files (`example.lua`, `basic_example.lua`)

```lua
-- Coroutine-based wait function
local function wait(ms)
    local co = coroutine.running()
    _PY.setTimeout(function()
        coroutine.resume(co)
    end, ms)
    coroutine.yield()
end

-- Usage in a coroutine
local function testWait()
    print("Starting...")
    wait(1000)  -- Wait 1 second
    print("After 1 second")
    wait(2000)  -- Wait 2 more seconds
    print("After 3 seconds total")
end

coroutine.resume(coroutine.create(testWait))
```

These examples show how you can build more convenient APIs on top of the core `_PY` functions to match your application's needs.

---

## Architecture Notes

### Function Registration
Python functions are automatically exposed to Lua using the `@export_to_lua` decorator. The decorator adds functions to the global `_exported_functions` dictionary, which is then copied to the `_PY` table in Lua during engine initialization.

### Async Operations
Many operations (timers, HTTP requests, threading) use a callback-based async pattern:
1. Register a callback with `_PY.registerCallback()`
2. Call the async function with the callback ID
3. The function executes asynchronously and calls back with results

### Table Conversion
Data structures are automatically converted between Python and Lua formats using `python_to_lua_table()` and `lua_to_python_table()` functions in `lua_bindings.py`.

### Error Handling
Most functions include comprehensive error handling and will return error information in callbacks or as return values rather than throwing exceptions that could crash the Lua environment.
