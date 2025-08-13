# EPLua Examples

This directory contains examples organized by usage pattern:

## 📁 `lua/` - End-User Examples
**For end users writing Lua scripts**

Examples using EPLua's high-level, user-friendly APIs:
- `setTimeout()`, `setInterval()`, `clearTimeout()`, `clearInterval()`
- `net.HTTPClient()`, `net.WebSocketClient()`, `net.MQTTClient()`
- `net.TCPSocket()`, `net.UDPSocket()`

These are the APIs you should use in your applications.

**Examples:**
- `basic_example.lua` - Overview of main features
- `getting_started.lua` - Step-by-step introduction
- `network_demo.lua` - Comprehensive networking examples
- `timer_examples.lua` - Timer and scheduling examples

## 📁 `py/` - Internal API Examples  
**For developers working on EPLua internals**

Examples using low-level `_PY.*` functions:
- `_PY.setTimeout()`, `_PY.setInterval()`
- `_PY.registerCallback()`, `_PY.call_http()`
- Direct Python function calls

These are internal APIs not intended for end users.

## 📁 `python/` - Python Integration Examples
**For Python developers using EPLua engine**

Examples showing how to:
- Embed the EPLua engine in Python applications
- Call Lua functions from Python
- Handle Lua callbacks in Python
- Extend EPLua with custom Python modules

## Getting Started

1. **New to EPLua?** Start with `lua/getting_started.lua`
2. **Want networking examples?** Try `lua/network_demo.lua`
3. **Python developer?** Check out `python/basic_usage.py`
4. **Contributing to EPLua?** Look at `py/` examples

## Running Examples

```bash
# Run end-user examples
python -m src.eplua.cli examples/lua/getting_started.lua

# Run Python integration examples
python examples/python/basic_usage.py
```

## API Reference

- **User APIs**: `setTimeout`, `setInterval`, `net.*` modules
- **Internal APIs**: `_PY.*` functions (not for end users)
- **Python APIs**: EPLua engine embedding and extension

## Core Examples

### `network_demo.lua`
Comprehensive demonstration of HTTP networking capabilities:
- Making GET, POST requests with `call_http()`
- Creating Lua convenience functions (`http_get`, `http_post`, etc.)
- Callback registration with `_PY.registerCallback()`
- Custom headers and JSON data
- Async request handling

**Run with:** `eplua examples/network_demo.lua`

### `network_example.lua`
Detailed network testing with request tracking and error handling.

**Run with:** `eplua examples/network_example.lua`

## Lua Examples (`lua/`)

### `getting_started.lua`
Basic introduction to EPLua features including:
- Timers and intervals
- Platform information
- File operations
- Math utilities

**Run with:** `eplua examples/lua/getting_started.lua`

### `basic_example.lua`
Shows timer functionality and coroutine-based waiting patterns.

**Run with:** `eplua examples/lua/basic_example.lua`

### `comprehensive_test_final.lua`
Complete test of all EPLua functionality including:
- Timers and intervals
- Lua table returns
- File operations
- System information
- JSON parsing

**Run with:** `eplua examples/lua/comprehensive_test_final.lua`

## Python Examples (`python/`)

### `basic_usage.py`
Demonstrates how to use EPLua from Python applications:
- Creating and managing LuaEngine instances
- Running Lua scripts from Python
- Setting Lua global variables
- Waiting for timers to complete

**Run with:** `python examples/python/basic_usage.py`

### `custom_extensions.py`
Template showing how to create custom Python functions for Lua:
- Using `@export_to_lua` decorator
- Returning Lua tables with `python_to_lua_table()`
- Date/time utilities
- String processing
- Math operations
- Hash generation

**Import this module** to add the custom functions to your EPLua environment.

## Available _PY Functions

When running Lua scripts with EPLua, the following Python functions are available via the `_PY` table:

### Core Functions
- `_PY.set_timeout(callback_id, ms)` - Set a timeout timer
- `_PY.clear_timeout(timer_id)` - Clear a timeout timer
- `_PY.get_timer_count()` - Get number of active timers
- `_PY.print(...)` - Enhanced print function
- `_PY.log(level, message)` - Logging function
- `_PY.get_time()` - Get current time in seconds
- `_PY.sleep(seconds)` - Blocking sleep (prefer timers)

### Platform & System
- `_PY.get_platform()` - Platform information as Lua table
- `_PY.get_system_info()` - Comprehensive system info as Lua table

### File Operations
- `_PY.read_file(filename)` - Read file contents
- `_PY.write_file(filename, content)` - Write content to file
- `_PY.list_directory(path)` - List directory contents as Lua table

### Utilities
- `_PY.math_add(a, b)` - Add two numbers
- `_PY.random_number(min, max)` - Generate random number
- `_PY.parse_json(json_string)` - Parse JSON to Lua table
- `_PY.to_json(data)` - Convert data to JSON string
- `_PY.get_env(var_name, default)` - Get environment variable
- `_PY.set_env(var_name, value)` - Set environment variable

### Lua-side Functions
These are implemented in Lua and built on top of the Python functions:

- `setTimeout(callback, ms)` - Set a timeout
- `clearTimeout(id)` - Clear a timeout
- `setInterval(callback, ms)` - Set a repeating interval
- `clearInterval(id)` - Clear an interval

## Getting Started

1. **Install EPLua:**
   ```bash
   pip install -e .
   ```

2. **Run a simple example:**
   ```bash
   eplua examples/lua/getting_started.lua
   ```

3. **Create your own extensions:**
   - Copy `examples/python/custom_extensions.py` as a template
   - Add your own `@export_to_lua` decorated functions
   - Import your module in your application

4. **Use from Python:**
   - See `examples/python/basic_usage.py` for integration patterns
   - Use async/await with the LuaEngine
   - Manage timer lifecycles properly

## Tips

- Use `python_to_lua_table()` to return complex data structures from Python to Lua
- Prefer `setTimeout`/`setInterval` over blocking operations
- Check `_PY.get_timer_count()` to know when all async operations are complete
- Use the global engine pattern for easy access across modules
