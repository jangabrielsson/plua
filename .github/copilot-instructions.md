# plua2 AI Agent Instructions

## Project Overview
plua2 is a Python-Lua async runtime that bridges Python's asyncio with Lua's coroutines, providing JavaScript-like timers and async operations. Think of it as "Node.js for Lua" with Python as the runtime.

## Architecture

### Core Components
- **`LuaAsyncRuntime`** (`src/plua2/runtime.py`) - Main async event loop coordinator
- **`LuaInterpreter`** (`src/plua2/interpreter.py`) - Lua runtime wrapper with `_PY` bridge
- **`api_server.py`** - FastAPI REST server with Web REPL interface  
- **`fibaro_api_endpoints.py`** - Auto-generated 194 Fibaro HC3 API endpoints

### Key Patterns

#### The `_PY` Bridge System
All Python-Lua communication flows through the `_PY` global table:
```lua
-- Hook functions for custom behavior
_PY.main_file_hook = function(filename) end  -- File preprocessing
_PY.fibaro_api_hook = function(method, path, data) end  -- API delegation
_PY.isRunning = function() return true end  -- Auto-termination

-- Built-in functions
_PY.setTimeout(callback, delay_ms)  -- Timer creation
_PY.clearTimeout(timer_id)  -- Timer cancellation
```

#### Async Timer Architecture
Timers use a producer-consumer pattern:
1. `setTimeout()` creates asyncio tasks that sleep, then queue callbacks
2. `run_timer_callbacks_loop()` consumes callback queue and executes Lua functions
3. All Lua execution happens in main thread for context safety

#### Module Registration Pattern
Python modules register functions using `@lua_exporter` decorator:
```python
@lua_exporter
def my_function(arg1, arg2):
    """Function exposed to Lua as _PY.my_function"""
    return result
```

## Development Workflows

### Running & Testing
```bash
# Interactive REPL (most common development mode)
plua2

# Run script with API server (for web debugging)
plua2 --api 8888 script.lua

# Run with Fibaro API emulation
plua2 --api 8888 dev/fibaro.lua

# Development tests (use dev/ directory)
plua2 dev/test_timers.lua
```

### Key Commands & Flags
- `--api [port]` - Start FastAPI REST server (default port 8888)
- `--duration N` - Auto-terminate after N seconds
- `--debug` - Enable verbose logging
- `--fibaro` - Load Fibaro HC3 API support

### File Organization
- `src/plua2/` - Core Python runtime
- `dev/` - Development tests and internal examples (use `_PY` functions)
- `examples/` - Clean user examples (avoid `_PY` internals)
- `docs/dev/` - Development documentation
- `fibaro_api_docs/` - Swagger/OpenAPI specs for auto-generation

## Integration Points

### Fibaro HC3 Integration
The project includes a comprehensive Fibaro Home Center 3 emulator:
- 194 auto-generated endpoints from Swagger specs
- Single Lua hook handles all API calls: `_PY.fibaro_api_hook(method, path, data)`
- Use `generate_fibaro_api.py` to regenerate endpoints from new Swagger files

### Web REPL Interface
- FastAPI serves both REST API and web interface at `/web`
- Supports HTML rendering in output (use `html_extensions.py` functions)
- Shared interpreter state between web and CLI REPL

### Network & Socket Support
- Synchronous socket operations via `syncsocket.py` 
- Built-in `net` module with HTTP client/server support
- TCP/UDP socket primitives available in Lua

## Common Pitfalls

### Context Safety
- All Lua execution must happen in main thread - never call Lua from asyncio tasks
- Use callback queue pattern for timer execution, not direct calls

### Module Loading
- Built-in modules (`json`, `net`) are auto-loaded, don't use `require()`
- External Lua files should go through `_PY.main_file_hook` for preprocessing

### Testing Patterns
- Development tests go in `dev/` and can use `_PY` internals
- User examples go in `examples/` and should be production-ready
- Use `--duration` flag to prevent infinite loops in tests

### VS Code Tasks
The project includes HC3-specific VS Code tasks for Fibaro development:
- "QA, upload current file as QA to HC3" - Upload Lua scripts to HC3
- Use these for Fibaro QuickApp development workflow
