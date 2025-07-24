# plua API Documentation

This directory contains comprehensive documentation for the plua REST API and web interfaces.

## 📡 REST API Reference

- [**API_USAGE.md**](API_USAGE.md) - Complete REST API reference with examples and use cases

## 🌐 Web Interface

### Web REPL
The plua web REPL provides a modern browser-based interface for interactive Lua development:

- **URL**: `http://localhost:8888/web` (default) or custom port
- **Features**: HTML rendering, real-time execution, state sharing with terminal REPL
- **Documentation**: See [Web REPL HTML Examples](../WEB_REPL_HTML_EXAMPLES.md)

### Quick Start
```bash
# Start plua with API server
plua --api

# Open browser to web REPL
open http://localhost:8888/web
```

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - API information and available endpoints
- `GET /web` - Web REPL interface
- `POST /plua/execute` - Execute Lua code remotely
- `GET /plua/status` - Get runtime status
- `GET /plua/info` - Get API and runtime information

### Endpoint Details

#### POST /plua/execute
Execute Lua code and return results.

**Request:**
```json
{
  "code": "return 2 + 2",
  "timeout": 30.0
}
```

**Response:**
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

#### GET /plua/status
Get current runtime status and active tasks.

**Response:**
```json
{
  "status": "running",
  "active_timers": 2,
  "pending_callbacks": 0,
  "total_tasks": 5,
  "api_requests_pending": 0
}
```

#### GET /plua/info
Get API version and runtime information.

**Response:**
```json
{
  "api_version": "1.0.0",
  "runtime_active": true,
  "lua_version": "5.4",
  "runtime_state": {
    "active_timers": 0,
    "pending_callbacks": 0,
    "total_tasks": 3
  },
  "features": ["timers", "networking", "json", "callbacks"]
}
```

## 🛡️ Security Considerations

### Production Deployment
- **Host Configuration**: Use `--api-host 127.0.0.1` for local-only access
- **Port Management**: Use non-standard ports for security
- **Access Control**: Implement authentication if exposing to network
- **Input Validation**: API validates and sanitizes Lua code execution

### Development vs Production
- **Development**: Default `0.0.0.0` host for easy testing
- **Production**: Restrict to localhost or specific interfaces
- **Monitoring**: Use status endpoints to monitor system health

## 🔧 Configuration

### Command Line Options
```bash
# Default API server (port 8888, all interfaces)
plua --api

# Custom port
plua --api 9000

# Custom host and port (localhost only)
plua --api 8877 --api-host 127.0.0.1
```

### Environment Integration
- **Shared State**: API and terminal REPL share the same Lua interpreter
- **Persistent Variables**: Variables set in one interface persist in the other
- **Background Tasks**: Timers and async operations continue across both interfaces

## 📊 Monitoring and Debugging

### Health Checks
Use the status endpoints to monitor API health:
```bash
curl http://localhost:8888/plua/info
curl http://localhost:8888/plua/status
```

### Error Handling
The API provides comprehensive error information:
- **Lua Syntax Errors**: Detailed error messages with line numbers
- **Runtime Errors**: Exception details and stack traces
- **Timeout Errors**: Clear timeout indication and partial output
- **Connection Errors**: Network and server status information

## 🔄 Integration Examples

### Curl Examples
```bash
# Simple execution
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"return math.pi"}'

# With timeout
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"print(\"Hello, API!\")", "timeout": 5.0}'
```

### Python Integration
```python
import requests

response = requests.post('http://localhost:8888/plua/execute',
                        json={'code': 'return os.date()'})
result = response.json()
print(f"Result: {result['result']}")
```

### JavaScript/Web Integration
```javascript
const response = await fetch('/plua/execute', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({code: 'return "Hello from JS!"'})
});
const result = await response.json();
console.log(result.result);
```

---

For more detailed examples and use cases, see [API_USAGE.md](API_USAGE.md).
