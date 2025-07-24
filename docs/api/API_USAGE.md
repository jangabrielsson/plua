# plua REST API Example

This example demonstrates the REST API functionality of plua.

## Starting the API Server

```bash
# Start plua with REPL and REST API server (shared interpreter)
python -m plua --api 8888

# Start with a Lua script and API
python -m plua --api 8888 my_script.lua

# Custom host and port
python -m plua --api 9000 --api-host 127.0.0.1 my_script.lua
```

## Shared Interpreter State

**Important**: The API server and REPL/script share the **same Lua interpreter instance**. This means:

- Variables set in the REPL are accessible via API
- Variables set via API are accessible in the REPL
- Functions defined in either context are available in both
- Global state is completely shared

### Example Workflow

```bash
# Start plua with both REPL and API
python -m plua --api 8888

# In the REPL, set a variable:
plua> a = 42

# From another terminal, access it via API:
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"return a"}'
# Returns: {"success":true,"result":42,...}

# Set a variable via API:
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"name = \"plua\"; return name"}'

# Access it in the REPL:
plua> return name
# Outputs: plua
```

## API Endpoints

### GET /
Basic API information and available endpoints.

### GET /plua/info
Runtime and API information including active features.

### GET /plua/status
Current runtime status including active timers, callbacks, and tasks.

### POST /plua/execute
Execute Lua code and get results.

#### Request Format
```json
{
  "code": "return 2 + 2",
  "timeout": 30.0
}
```

#### Response Format
```json
{
  "success": true,
  "result": 4,
  "output": "",
  "error": null,
  "execution_time_ms": 0.5,
  "request_id": "uuid-here"
}
```

## Examples

### Simple Calculation
```bash
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"return 2 + 2"}'
```

### String Operations
```bash
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"return \"Hello, \" .. \"World!\""}'
```

### Using Built-in Network Module
```bash
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"return type(net) .. \" module available\""}'
```

### Using Built-in JSON Module  
```bash
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"local data = {name=\"test\", value=42}; return json.encode(data)"}'
```

### Creating a Timer
```bash
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"setTimeout(function() print(\"Timer fired!\") end, 1000); return \"Timer created\""}'
```

## Features

- ✅ Execute arbitrary Lua code
- ✅ Return values from expressions and statements
- ✅ Built-in `net` module for networking (HTTP, TCP, UDP)
- ✅ Built-in `json` module for JSON operations
- ✅ Timer support via `setTimeout` (setInterval coming soon)
- ✅ Error handling and timeout protection
- ✅ CORS support for browser integration
- ✅ Access and modify variables in running Lua scripts
- ✅ Real-time interaction with background Lua processes
- 🔄 Print output capture (planned for future version)

## Use Cases

1. **Interactive Development**: Use REPL for exploration, API for automation
2. **Remote Script Control**: Start a Lua script and control it via HTTP API
3. **Real-time Monitoring**: Check script state and variables via API calls
4. **Dynamic Configuration**: Modify script behavior without restarting
5. **Web Integration**: Build web interfaces that interact with Lua scripts
6. **Development Tools**: Create debugging and development interfaces
7. **IoT Integration**: Control embedded Lua scripts remotely
8. **Hybrid Workflows**: Mix manual REPL commands with automated API calls

## Quick Demo

```bash
# Start plua with API and background script
python -m plua --api 8888 -e "counter = 0; message = 'Hello World'"

# Test basic calculation
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"return 2 + 2"}'

# Access variables from running script
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"return message"}'

# Modify variables in running script
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"counter = counter + 1; return counter"}'
```

## Reserved Paths

- `/plua/*` - plua specific functions
- `/api/*` - Reserved for future Fibaro API integration

## Architecture

The API server runs in the same event loop as the Lua runtime, ensuring:

- Responsive API even if Lua VM is paused (e.g., by debugger)
- Efficient communication without thread/process overhead
- Access to all runtime state and capabilities
- Real-time interaction with running Lua scripts

## Next Steps

- Complete print output capture implementation
- Add more plua-specific endpoints
- Implement Fibaro API endpoints under `/api/*`
- Add authentication and security features
