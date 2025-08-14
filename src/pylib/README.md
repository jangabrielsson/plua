# PyLib - PLua FFI Libraries

This directory contains Python libraries that can be dynamically loaded from Lua using the FFI-like interface.

## Structure

- Each `.py` file in this directory is a loadable module
- Modules use `@export_to_lua()` decorators to expose functions
- Lua scripts load them with `_PY.loadPythonModule("module_name")`

## Bundled Libraries

These libraries come with the PLua package:

- **filesystem.py** - File system operations (luafilesystem compatible)
- **http_client.py** - HTTP requests and responses
- **tcp_client.py** - TCP networking
- **udp_client.py** - UDP networking  
- **websocket_client.py** - WebSocket client/server
- **mqtt_client.py** - MQTT messaging

## Usage from Lua

```lua
-- Load a bundled library
local fs = _PY.loadPythonModule("filesystem")
local current_dir = fs.fs_currentdir()

-- Or use high-level Lua wrappers
local lfs = require("lfs")  -- Uses filesystem.py internally
```

## Creating Custom Libraries

Users can create their own libraries and place them in this directory or use Python's module system to install them elsewhere.
