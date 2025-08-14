# Web Server Extension

The PLua web server extension provides a FastAPI-based HTTP server that can be controlled from Lua scripts. The server runs in a separate thread and communicates with the main Lua engine through the thread-safe callback system.

## Features

- **RESTful API**: Standard HTTP endpoints for interacting with the Lua engine
- **Thread Safety**: Server runs in separate thread with safe communication to main engine
- **Real-time Status**: Get live information about engine state and active operations
- **Script Execution**: Execute Lua scripts remotely via HTTP API
- **Callback Monitoring**: View active callbacks and intervals

## API Endpoints

### GET /
Root endpoint with basic server information.

### GET /status
Get comprehensive server and engine status:
```json
{
  "status": "running",
  "uptime": 123.45,
  "active_callbacks": 2,
  "running_intervals": 1,
  "server_port": 8000
}
```

### POST /execute
Execute a Lua script remotely:

**Request:**
```json
{
  "script": "return {message = 'Hello', time = os.time()}",
  "timeout": 30.0
}
```

**Response:**
```json
{
  "result": {
    "message": "Hello",
    "time": 1706123456
  },
  "execution_time": 0.023
}
```

### GET /engine/callbacks
Get information about active callbacks and intervals:
```json
{
  "callbacks": [
    {"id": "uuid-1", "type": "callback"},
    {"id": "uuid-2", "type": "callback"}
  ],
  "count": 2,
  "running_intervals": 1
}
```

## Lua Functions

### start_web_server(host, port, callback_id)
Start the web server.

**Parameters:**
- `host` (string, optional): Host to bind to (default: "127.0.0.1")
- `port` (number, optional): Port to bind to (default: 8000)
- `callback_id` (string, optional): Callback ID for async notification

**Returns:** Server start result with status information

**Example:**
```lua
local result = _PY.start_web_server("127.0.0.1", 8000)
if result.success then
    print("Server started at: " .. result.server_info.url)
end
```

### stop_web_server(callback_id)
Stop the web server.

**Parameters:**
- `callback_id` (string, optional): Callback ID for async notification

**Returns:** Server stop result

**Example:**
```lua
local result = _PY.stop_web_server()
if result.success then
    print("Server stopped")
end
```

### get_web_server_status()
Get current web server status.

**Returns:** Server status information

**Example:**
```lua
local status = _PY.get_web_server_status()
print("Server running: " .. tostring(status.running))
if status.running then
    print("URL: " .. status.url)
end
```

## Usage Examples

### Basic Server Setup
```lua
-- Start server
local result = _PY.start_web_server("0.0.0.0", 8080)
if result.success then
    print("API server available at: " .. result.server_info.url)
    
    -- Keep server running for 60 seconds
    setTimeout(function()
        _PY.stop_web_server()
        print("Server stopped")
    end, 60000)
end
```

### With Background Operations
```lua
-- Start server
_PY.start_web_server()

-- Set up some operations that will show in /status
setInterval(function()
    print("Background task running...")
end, 5000)

-- HTTP request
_PY.call_http("https://api.github.com", {}, function(response, error)
    print("HTTP request completed")
end)

-- Server will show these active operations in /engine/callbacks
```

## Testing with cURL

```bash
# Get server status
curl http://127.0.0.1:8000/status

# Execute a Lua script
curl -X POST http://127.0.0.1:8000/execute \
  -H 'Content-Type: application/json' \
  -d '{"script": "return math.random(1, 100)"}'

# Get active callbacks
curl http://127.0.0.1:8000/engine/callbacks
```

## Integration with Other Features

The web server integrates seamlessly with all PLua features:

- **Timers**: Active timers show up in status endpoints
- **HTTP Requests**: Network operations are tracked
- **Threading**: Uses the same thread-safe callback system
- **Intervals**: Running intervals are counted and reported

## Architecture Notes

- **Thread Separation**: Server runs in dedicated thread to avoid blocking main engine
- **Callback System**: Uses existing thread-safe queue for communication
- **Error Handling**: Proper HTTP status codes and error messages
- **Resource Management**: Automatic cleanup and timeout handling
- **JSON Serialization**: Lua tables are automatically converted to JSON responses

## Dependencies

- `fastapi>=0.100.0`: Web framework
- `uvicorn>=0.23.0`: ASGI server
- `pydantic`: Request/response models
