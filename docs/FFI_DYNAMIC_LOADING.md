# FFI-like Dynamic Python Module Loading

EPLua provides a powerful FFI-like interface for dynamically loading Python modules from Lua scripts. This approach gives you the same convenience as LuaJIT's FFI, but powered by Python instead of C libraries.

## Basic Usage

### Loading a Python Module

```lua
-- Load a Python module dynamically
local fs_functions = _PY.loadPythonModule("filesystem")

-- Use the loaded functions immediately
local current_dir = fs_functions.fs_currentdir()
local attrs = fs_functions.fs_attributes("README.md")
```

### Error Handling

```lua
local module_funcs = _PY.loadPythonModule("some_module")
if module_funcs.error then
    error("Failed to load module: " .. module_funcs.error)
end
```

## Creating Lua Wrapper Modules

You can create clean Lua APIs that use dynamic loading internally:

```lua
-- http.lua - A Lua module that wraps Python HTTP functionality
local http = {}

local http_module = nil

local function ensure_http_loaded()
    if not http_module then
        http_module = _PY.loadPythonModule("http_client")
        if http_module.error then
            error("Failed to load HTTP module: " .. http_module.error)
        end
    end
    return http_module
end

function http.get(url, headers)
    local client = ensure_http_loaded()
    return client.http_request_sync({
        url = url,
        method = "GET",
        headers = headers or {}
    })
end

return http
```

## Available Modules

### Core Modules
- **filesystem** - File system operations (like luafilesystem)
- **http_client** - HTTP requests (sync and async)
- **tcp** - TCP client and server
- **udp** - UDP sockets
- **websocket** - WebSocket client and server
- **mqtt** - MQTT client with event support

### Example Usage

```lua
-- Filesystem operations
local fs = _PY.loadPythonModule("filesystem")
local files = {}
local dir_id = fs.fs_dir_open(".")
while true do
    local file = fs.fs_dir_next(dir_id)
    if not file then break end
    table.insert(files, file)
end
fs.fs_dir_close(dir_id)

-- HTTP requests
local http = _PY.loadPythonModule("http_client")
local response = http.http_request_sync({
    url = "https://api.example.com/data",
    method = "GET",
    headers = { ["Accept"] = "application/json" }
})

-- TCP networking
local tcp = _PY.loadPythonModule("tcp")
local server_id = tcp.tcp_server_create("localhost", 8080)
tcp.tcp_server_start(server_id, function(client_id)
    -- Handle client connection
end)
```

## Benefits

### 1. Lazy Loading
Modules are only loaded when needed, reducing memory usage and startup time.

### 2. Hot Reloading
During development, modules can be reloaded to pick up changes:

```lua
-- The loadPythonModule function will reload if the module was already imported
local updated_module = _PY.loadPythonModule("my_module")
```

### 3. Clean Separation
- **Python backend** - Handles complex operations, networking, file I/O
- **Lua frontend** - Provides clean APIs and scripting interface

### 4. Modular Development
Each Python module is independent and can be developed/tested separately.

### 5. FFI-like Convenience
Similar developer experience to LuaJIT's FFI:

```lua
-- LuaJIT FFI style
local ffi = require("ffi")
local lib = ffi.load("mylib")
lib.my_function()

-- EPLua style
local funcs = _PY.loadPythonModule("my_module")
funcs.my_function()
```

## Comparison to LuaJIT FFI

| Aspect | LuaJIT FFI | EPLua Dynamic Loading |
|--------|------------|----------------------|
| **Loading** | `ffi.load('libname')` | `_PY.loadPythonModule('module')` |
| **Functions** | Direct C function calls | Direct Python function calls |
| **Data Types** | C types and structures | Python objects and tables |
| **Performance** | Native C speed | Python speed (still fast) |
| **Ecosystem** | C libraries | Python packages |
| **Development** | C compilation required | Pure Python development |

## Creating Your Own Modules

### 1. Create a Python Module

```python
# my_custom_module.py
from eplua.lua_bindings import export_to_lua

@export_to_lua("my_function")
def my_function(arg1, arg2):
    return f"Hello {arg1} and {arg2}!"

@export_to_lua("process_data")
def process_data(data_table):
    # data_table is automatically converted from Lua table
    result = {"processed": True, "count": len(data_table)}
    return result  # Automatically converted to Lua table
```

### 2. Import in Extensions

```python
# Add to src/eplua/extensions.py
from . import my_custom_module
```

### 3. Use from Lua

```lua
local my_funcs = _PY.loadPythonModule("my_custom_module")
print(my_funcs.my_function("Alice", "Bob"))

local result = my_funcs.process_data({1, 2, 3, 4, 5})
print("Count:", result.count)
```

## Best Practices

### 1. Lazy Loading Pattern

Always use the lazy loading pattern in your Lua modules:

```lua
local module_cache = nil

local function ensure_loaded()
    if not module_cache then
        module_cache = _PY.loadPythonModule("module_name")
        if module_cache.error then
            error("Failed to load: " .. module_cache.error)
        end
    end
    return module_cache
end
```

### 2. Error Handling

Always check for errors when loading modules:

```lua
local success, result = pcall(function()
    return _PY.loadPythonModule("module_name")
end)

if not success or result.error then
    print("Module loading failed:", result and result.error or "Unknown error")
    return
end
```

### 3. Function Naming

Use consistent naming in your Python modules:

```python
# Good: prefixed names
@export_to_lua("http_request")
@export_to_lua("http_parse_url")

# Better: module-specific prefixes help with organization
@export_to_lua("tcp_connect")
@export_to_lua("tcp_send")
```

This FFI-like system provides the flexibility of Python with the convenience of dynamic loading, making EPLua a powerful platform for Lua scripting with Python backends.
