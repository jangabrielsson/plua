# PyLib Structure for PyPI Packaging

This document outlines how the PyLib FFI system is structured for future PyPI packaging and distribution.

## Current Structure

```
src/
├── eplua/                 # Core EPLua package
│   ├── __init__.py
│   ├── engine.py          # Lua runtime engine
│   ├── lua_bindings.py    # Python-Lua bridge
│   ├── extensions.py      # loadPythonModule() function
│   ├── cli.py            # Command-line interface
│   └── ...               # Other core modules
│
└── pylib/                 # FFI Libraries (bundled with EPLua)
    ├── __init__.py
    ├── README.md
    ├── filesystem.py      # luafilesystem compatible
    ├── http_client.py     # HTTP requests
    ├── tcp_client.py      # TCP networking
    ├── udp_client.py      # UDP networking
    ├── websocket_client.py # WebSocket
    └── mqtt_client.py     # MQTT messaging
```

## PyPI Package Structure

When published to PyPI, the package will have this structure:

```
eplua/
├── __init__.py
├── engine.py
├── lua_bindings.py
├── extensions.py
├── cli.py
├── ...
└── pylib/
    ├── __init__.py
    ├── filesystem.py
    ├── http_client.py
    ├── tcp_client.py
    ├── udp_client.py
    ├── websocket_client.py
    └── mqtt_client.py
```

## Installation and Usage

### Installing EPLua

```bash
pip install eplua
```

### Using Built-in Libraries

```lua
-- All these libraries come bundled with EPLua
local fs = _PY.loadPythonModule("filesystem")
local http = _PY.loadPythonModule("http_client")
local tcp = _PY.loadPythonModule("tcp_client")
local udp = _PY.loadPythonModule("udp_client")
local ws = _PY.loadPythonModule("websocket_client")
local mqtt = _PY.loadPythonModule("mqtt_client")
```

### High-level Lua Modules

Users can also use high-level Lua modules that wrap the PyLib libraries:

```lua
-- These use PyLib libraries internally
local lfs = require("lfs")          -- Uses filesystem.py
local http = require("http")        -- Uses http_client.py
local net = require("net")          -- Uses tcp/udp/websocket/mqtt
```

## Module Loading Strategy

The `loadPythonModule()` function searches for modules in this order:

1. **PyLib directory** (`eplua.pylib.module_name`)
   - Bundled FFI libraries that come with EPLua
   - Always available after `pip install eplua`

2. **EPLua package** (`eplua.module_name`)
   - Core EPLua modules and extensions
   - Legacy compatibility with existing code

3. **Standard Python modules** (`module_name`)
   - Any Python module in sys.path
   - Allows loading user-installed packages

## Adding Custom Libraries

Users can extend EPLua with custom libraries in several ways:

### 1. Project-local PyLib

Create a `pylib/` directory in your project:

```
my_project/
├── my_script.lua
└── pylib/
    └── my_custom.py
```

```python
# pylib/my_custom.py
from eplua.lua_bindings import export_to_lua

@export_to_lua("my_function")
def my_function(data):
    return f"Processed: {data}"
```

```lua
-- my_script.lua
local custom = _PY.loadPythonModule("my_custom")
print(custom.my_function("hello"))
```

### 2. User-specific Libraries

Install libraries in user directory:

```
~/.eplua/pylib/
└── user_library.py
```

### 3. System-wide Extensions

Create separate Python packages:

```bash
pip install eplua-extensions-database
pip install eplua-extensions-graphics
```

## PyPI Package Configuration

The `pyproject.toml` is configured to include the PyLib directory:

```toml
[project]
name = "eplua"
version = "0.1.0"
description = "Lua scripting with Python FFI libraries"

[project.scripts]
eplua = "eplua.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
```

This ensures that both `eplua/` and `pylib/` are included in the wheel.

## Development and Testing

### Running from Source

```bash
git clone https://github.com/yourname/eplua
cd eplua
pip install -e .
eplua examples/lua/demo.lua
```

### Adding New PyLib Modules

1. Create module in `src/pylib/new_module.py`
2. Use `@export_to_lua()` decorators
3. Import from `eplua.lua_bindings`
4. Add to `src/pylib/__init__.py`
5. Test with `_PY.loadPythonModule("new_module")`

### Example New Module

```python
# src/pylib/database.py
import sqlite3
from eplua.lua_bindings import export_to_lua, python_to_lua_table

@export_to_lua("db_open")
def db_open(filename):
    # Implementation here
    pass

@export_to_lua("db_query")
def db_query(connection, sql):
    # Implementation here
    pass
```

## Future Extensions

### Extension Packages

Users could create and publish extension packages:

```bash
# eplua-database extension
pip install eplua-database

# eplua-graphics extension  
pip install eplua-graphics

# eplua-ai extension
pip install eplua-ai
```

### Auto-discovery

Future versions could auto-discover extension packages:

```lua
-- Auto-load from installed extension packages
local db = _PY.loadPythonModule("database")    -- from eplua-database
local gfx = _PY.loadPythonModule("graphics")   -- from eplua-graphics
local ai = _PY.loadPythonModule("ai")          -- from eplua-ai
```

## Benefits for PyPI Distribution

1. **Self-contained**: All FFI libraries bundled with EPLua
2. **Dependency management**: pip handles Python dependencies
3. **Version control**: PyPI versioning for EPLua + libraries
4. **Easy installation**: Single `pip install eplua` command
5. **Extensible**: Users can add custom libraries
6. **Professional**: Standard Python packaging practices

## Migration Path

Existing users can migrate easily:

```lua
-- Old way (still works)
local attrs = _PY.fs_attributes("file.txt")

-- New way (preferred)
local fs = _PY.loadPythonModule("filesystem")
local attrs = fs.fs_attributes("file.txt")

-- Or use high-level Lua modules
local lfs = require("lfs")
local attrs = lfs.attributes("file.txt")
```

This structure provides a clean, professional foundation for EPLua's future as a PyPI package while maintaining backward compatibility and enabling powerful extensibility.
