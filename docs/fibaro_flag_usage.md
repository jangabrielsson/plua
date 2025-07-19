# Fibaro API Support in plua2

The `--fibaro` flag provides convenient access to Fibaro Home Center API emulation in plua2.

## Usage

```bash
# Load Fibaro support with a script file
plua2 --fibaro script.lua

# Load Fibaro support in REPL mode
plua2 --fibaro

# Combine with other flags
plua2 --fibaro --api 8888 script.lua
plua2 --fibaro -e 'print("Fibaro loaded:", fibaro ~= nil)' script.lua
```

## What the --fibaro Flag Does

The `--fibaro` flag is equivalent to adding `-e "require('fibaro')"` as the first script fragment. This means:

1. The `fibaro.lua` module is loaded before any other scripts
2. Global `fibaro` and `api` tables become available
3. The `_PY.main_file_hook` is overridden for Fibaro-specific file preprocessing
4. The `_PY.fibaro_api_hook` is installed for handling FastAPI requests

## Available Globals After Loading

### `fibaro` Table
Global table containing Fibaro-specific functions and utilities.

### `api` Table
Global table with HTTP-like API functions:
- `api.get(path)` - GET request
- `api.post(path, data)` - POST request  
- `api.put(path, data)` - PUT request
- `api.delete(path)` - DELETE request

### `_PY.fibaro_api_hook` Function
Handler function for FastAPI endpoints that processes incoming HTTP requests and delegates them to Lua code.

## FastAPI Integration

When running with `--api` and `--fibaro` flags together, plua2 provides 194 auto-generated FastAPI endpoints that match the Fibaro Home Center API specification. All requests are forwarded to the Lua `_PY.fibaro_api_hook` function.

Example:
```bash
# Start server with Fibaro API support
plua2 --fibaro --api 8888

# Test an endpoint
curl http://localhost:8888/api/devices
```

## Implementation Details

The `--fibaro` flag:
1. Prepends `"require('fibaro')"` to the script fragments list
2. This loads `/src/lua/fibaro.lua` which sets up the global environment
3. The fibaro.lua module overrides the default `main_file_hook` for custom preprocessing
4. Auto-generated FastAPI endpoints route to the `fibaro_api_hook` function

## File Processing

With Fibaro support loaded, all main Lua files go through the custom `main_file_hook` defined in `fibaro.lua`, which can perform Fibaro-specific preprocessing before execution.

## Examples

### Basic Usage
```bash
plua2 --fibaro -e 'print("API available:", type(api.get))'
# Output: API available: function
```

### With API Server
```bash
plua2 --fibaro --api 8888 script.lua
# Creates HTTP server with Fibaro endpoints + runs script.lua
```

### Testing Fibaro Support
```bash
plua2 --fibaro -e 'if fibaro then print("Fibaro loaded!") end'
# Output: Fibaro loaded!
```

The `--fibaro` flag makes it very convenient to quickly load Fibaro API emulation support without manually requiring the module.
