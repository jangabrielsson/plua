# plua

Python-Lua async runtime with timer support

## Overview

plua is a Python package that provides an async runtime environment for executing Lua scripts with JavaScript-like timer functionality. It bridges Python's asyncio with Lua's coroutines, allowing for sophisticated async programming patterns.

## Features

- **Interactive REPL**: Lua-like interactive prompt with plua features
- **JavaScript-like timers**: `setTimeout()` and `clearTimeout()` in Lua
- **Async/await bridge**: Python asyncio integrated with Lua coroutines  
- **Context safety**: All Lua execution happens in the same Python context
- **Timer management**: Named asyncio tasks with cancellation support
- **Network simulation**: Built-in `netWorkIO()` function for async operations
- **Coroutine support**: Full Lua coroutine functionality with yielding

## Installation

```bash
# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Interactive REPL (no file specified)
plua

# Run a Lua file directly
plua script.lua

# Run with time limit
plua --duration 10 script.lua

# Start with REST API server
plua --api                    # Default port 8888
plua --api 8877              # Custom port
plua --api 8877 --api-host 127.0.0.1  # Custom host and port

# Run built-in examples
plua --example 2 --duration 10
plua --example cancel --duration 5

# Run inline Lua code
plua --script 'print("Hello from Lua"); setTimeout(function() print("Timer fired!") end, 1000)' --duration 5

# Run forever (until Ctrl+C)
plua script.lua
```

### Interactive REPL

plua provides an interactive REPL (Read-Eval-Print Loop) when no Lua file is specified:

```bash
$ plua
Plua v0.1.0 Interactive REPL
Running Lua 5.4 with async runtime support

Quick start:
  help()                           - Show available commands
  print('Hello, plua!')           - Basic Lua
  json.encode({name='test'})       - JSON encoding
  setTimeout(function() print('Hi!') end, 2000) - Async timer

Type 'exit()' or press Ctrl+D to quit

plua> print("Hello, world!")
Hello, world!
plua> x = 42
plua> x + 10
52
plua> client = net.HTTPClient()
plua> setTimeout(function() print("Timer fired!") end, 2000)
plua> -- Timer fires after 2 seconds
Timer fired!
plua> exit()
Goodbye!
```

The REPL supports:
- All plua features (timers, JSON, networking)
- Built-in `json` and `net` modules (no require needed)
- Persistent variables and functions
- Background async operations
- Built-in help and state inspection
- Error recovery

### Python API Usage

```python
import asyncio
from plua import LuaAsyncRuntime

async def main():
    runtime = LuaAsyncRuntime()
    
    script = """
    print("Starting...")
    setTimeout(function() 
        print("Timer 1 fired!")
        setTimeout(function() print("Timer 2 fired!") end, 500)
    end, 1000)
    """
    
    await runtime.start(script=script, duration=5)

asyncio.run(main())
```

### REST API Server

plua includes a built-in REST API server that allows remote execution of Lua code:

```bash
# Start plua with REST API on default port 8888
plua --api

# Start on specific port with custom host
plua --api 8877 --api-host 127.0.0.1

# Access the web REPL interface
# Open browser to: http://localhost:8888/web
```

#### API Endpoints

- `GET /` - API information and available endpoints
- `GET /web` - Web-based REPL interface
- `POST /plua/execute` - Execute Lua code remotely
- `GET /plua/status` - Get runtime status
- `GET /plua/info` - Get API and runtime information

#### Web REPL

The web REPL provides a modern browser-based interface for plua:

- **HTML Rendering**: Supports HTML tags in output for colored and formatted text
- **Real-time Execution**: Share interpreter state with local REPL
- **Timer Support**: Background timers work seamlessly
- **Modern UI**: Responsive design with syntax highlighting

Example HTML output in web REPL:
```lua
print("<font color='red'>Red text</font>")
print("<b>Bold text</b> | <i>Italic text</i>")
print("<span style='background-color: yellow;'>Highlighted</span>")
```

#### Remote Code Execution

```bash
# Execute Lua code via API
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"return 2 + 2", "timeout": 10.0}'
```

Response:
```json
{
  "success": true,
  "result": 4,
  "output": "",
  "error": null,
  "execution_time_ms": 0.123,
  "request_id": "uuid-here"
}
```

The API server and local REPL share the same Lua interpreter instance, so:
- Variables persist between API calls and REPL commands
- Timers set via API continue running in the background
- State is shared seamlessly between web and terminal interfaces
```

## Lua API

### Timer Functions

```lua
-- Set a timer
local timer_id = setTimeout(function() 
    print("This runs after 1 second") 
end, 1000)

-- Cancel a timer
clearTimeout(timer_id)

-- Sleep (yields current coroutine)
sleep(500)  -- Sleep for 500ms
```

### Network Simulation

```lua
-- Simulate async network operation
netWorkIO(function(data) 
    print("Received data:", data)  -- "xyz" after 1 second
end)
```

### Coroutines

```lua
local function asyncFunction()
    print("Start")
    local co = coroutine.running()
    
    setTimeout(function() 
        coroutine.resume(co, "result") 
    end, 1000)
    
    local result = coroutine.yield()
    print("Got result:", result)
end

coroutine.wrap(asyncFunction)()
```

## Examples

### Example 1: Repeating Timer

```lua
local function loop()
    print("PING")
    netWorkIO(function(data) 
        print("Network callback", data) 
    end)
    setTimeout(loop, 5000)  -- Repeat every 5 seconds
end
setTimeout(loop, 100)  -- Start after 100ms
```

### Example 2: Coroutine Yielding

```lua
local function foo()
    print("A")
    local co = coroutine.running()
    setTimeout(function() 
        coroutine.resume(co) 
        print("D") 
    end, 1000)
    print("B")
    coroutine.yield()
    print("C")
end
coroutine.wrap(foo)()
-- Output: A, B, (1 second delay), D, C
```

### Example 3: Timer Cancellation

```lua
-- Set a timer
local timer_id = setTimeout(function() 
    print("This should be cancelled!") 
end, 2000)

-- Cancel it after 500ms
setTimeout(function()
    print("Cancelling timer")
    clearTimeout(timer_id)
end, 500)
```

## Architecture

### Components

- **`LuaInterpreter`**: Manages Lua runtime and script execution
- **`LuaAsyncRuntime`**: Handles asyncio integration and timer management
- **Timer System**: Maps Lua timer calls to Python asyncio tasks
- **Callback Loop**: Executes Lua callbacks in the correct context

### Flow

1. Lua calls `setTimeout(callback, delay)`
2. Python creates an asyncio task that waits for `delay`
3. When timer fires, Python queues the callback ID
4. Callback loop executes the Lua callback in the same context
5. Lua coroutines can yield and be resumed by timers

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Documentation Index](docs/README.md)** - Complete documentation overview
- **[Web REPL HTML Examples](docs/WEB_REPL_HTML_EXAMPLES.md)** - HTML rendering guide for web interface
- **[REST API Documentation](docs/api/README.md)** - Complete API reference and examples
- **[Developer Documentation](docs/dev/README.md)** - Implementation details and development guides

### Quick Links
- 🚀 **Getting Started**: This README
- 🌐 **Web Interface**: [Web REPL Examples](docs/WEB_REPL_HTML_EXAMPLES.md)
- 📡 **API Integration**: [REST API Docs](docs/api/README.md)
- 🔧 **Contributing**: [Developer Docs](docs/dev/README.md)

## Fibaro HC3 API Integration

plua includes a comprehensive Fibaro Home Center 3 API emulator with full type safety and documentation:

### Generated API Endpoints

The Fibaro API endpoints are auto-generated from official Swagger/OpenAPI specifications:

```bash
# Regenerate Fibaro API endpoints and models
python src/plua/generate_typed_fibaro_api.py

# Generate with custom paths
python src/plua/generate_typed_fibaro_api.py --docs-dir fibaro_api_docs --output-dir src/plua
```

This generates:
- **`fibaro_api_models.py`**: 305+ Pydantic models with full type validation
- **`fibaro_api_endpoints.py`**: 267+ FastAPI endpoints with proper documentation

### Fibaro API Features

- **Complete Coverage**: All major Fibaro HC3 API endpoints
- **Type Safety**: Full Pydantic validation for request/response data
- **Swagger Documentation**: Auto-generated API docs at `/docs`
- **Lua Integration**: All calls delegate to `_PY.fibaro_api_hook(method, path, data)`
- **Easy Testing**: Use web interface or curl to test endpoints

```bash
# Start server with Fibaro API
plua --api-port 8888 --fibaro

# Test an endpoint
curl -X GET "http://localhost:8888/devices" -H "accept: application/json"
```

## Development

### Setup Development Environment

```bash
# Clone and setup
git clone <repository>
cd plua
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
```

### Type Checking

```bash
mypy src/
```

## License

MIT License

## Requirements

- Python 3.8+
- lupa (Python-Lua bridge)
- asyncio (built-in)
