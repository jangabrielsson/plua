# plua Examples

This directory contains clean, end-user examples that demonstrate the capabilities of plua. These examples are designed to be educational and show best practices for using the plua runtime.

## Available Examples

### Network Examples

#### `http_client_example.lua`
Demonstrates how to make HTTP requests using the `net.HTTPClient()` class:
- Basic GET requests
- POST requests with JSON data
- Custom headers and authentication
- Error handling

```bash
plua examples/http_client_example.lua
```

#### `tcp_socket_example.lua`
Shows TCP socket programming with `net.TCPSocket()`:
- Connecting to echo servers
- Raw HTTP over TCP (educational)
- Timeout handling
- Reading and writing data

```bash
plua examples/tcp_socket_example.lua
```

#### `udp_socket_example.lua`
UDP socket communication using `net.UDPSocket()`:
- Sending UDP packets
- Broadcasting messages
- Local loopback testing

```bash
plua examples/udp_socket_example.lua
```

#### `http_server_example.lua`
Creating HTTP servers for debugging with `net.HTTPServer()`:
- Simple REST API endpoints
- JSON request/response handling
- URL routing and parameter extraction
- Self-testing with HTTP client

```bash
plua examples/http_server_example.lua
```

### Data Processing Examples

#### `json_example.lua`
Working with JSON data using `json.encode()` and `json.decode()`:
- Basic encoding and decoding
- Nested objects and arrays
- API communication patterns
- Error handling

```bash
plua examples/json_example.lua
```

### Async and Timing Examples

#### `timer_async_example.lua`
Asynchronous programming with timers:
- `setTimeout()` and `setInterval()`
- Chained async operations
- Simulating API calls
- Timer cancellation
- Performance timing

```bash
plua examples/timer_async_example.lua
```

#### `auto_terminating_example.lua`
Demonstrates automatic script termination:
- Custom `_PY.isRunning` hook for termination logic
- Automatic cleanup when all tasks complete
- No need for manual `os.exit()` calls
- Runtime state monitoring

```bash
plua examples/auto_terminating_example.lua
```

#### `http_server_auto_termination_example.lua`
HTTP server with automatic shutdown:
- Request-based termination conditions
- Server state monitoring in real-time
- Clean shutdown after processing requests
- Demonstrates server lifecycle management

```bash
plua examples/http_server_auto_termination_example.lua
# Then make requests: curl http://localhost:8100/hello
```

#### `repl_demo.lua`
Demonstrates features available in the interactive REPL:
- Basic Lua operations and variables
- JSON encoding and decoding
- Timer scheduling and callbacks
- HTTP client usage patterns
- REPL command examples

```bash
# Run the demo as a script first
plua examples/repl_demo.lua

# Then try the same commands in the REPL
plua
```

#### `builtin_modules_test.lua`
Tests the built-in `json` and `net` modules:
- Verifies JSON encoding and decoding
- Tests network module availability
- Demonstrates that no `require()` calls are needed

```bash
plua examples/builtin_modules_test.lua
```

## Key Features Demonstrated

### Network Module (`net`)
- **HTTPClient**: Make HTTP requests with callbacks
- **TCPSocket**: Raw TCP connections for custom protocols
- **UDPSocket**: UDP communication for broadcasting/discovery
- **HTTPServer**: Simple HTTP servers for debugging and testing

### JSON Support
- **json.encode()**: Convert Lua tables to JSON strings
- **json.decode()**: Parse JSON strings to Lua tables
- Handles nested objects, arrays, and primitive types

### Async Runtime
- **setTimeout()**: Execute code after a delay
- **setInterval()**: Repeat code execution at intervals
- **clearTimeout()/clearInterval()**: Cancel scheduled execution
- **_PY.isRunning()**: Custom termination logic for automatic script cleanup
- Event-driven programming with callbacks

## Usage Patterns

### Error Handling
All network operations use callback-based error handling:

```lua
client:request(url, {
    success = function(response)
        -- Handle successful response
    end,
    error = function(status)
        -- Handle error
    end
})
```

### JSON Communication
Standard pattern for API communication:

```lua
local request_data = {key = "value"}
local json_string = json.encode(request_data)

-- Later, parse response:
local response_data = json.decode(response.data)
```

### Async Patterns
Chain operations with timers and callbacks:

```lua
-- Sequence of async operations
setTimeout(function()
    print("Step 1")
    setTimeout(function()
        print("Step 2")
    end, 1000)
end, 1000)
```

### Auto-Termination Pattern
Use the `_PY.isRunning` hook for automatic script termination:

```lua
local work_completed = false

function _PY.isRunning(state)
    -- Check if all work is done
    if work_completed and state.total_tasks == 0 then
        print("Script completed - terminating")
        return false  -- Stop the script
    end
    return true  -- Continue running
end

-- Do async work...
setTimeout(function()
    work_completed = true
end, 5000)
```

## Notes

- All examples are self-contained and don't require external dependencies
- Examples use realistic patterns you'd find in production code
- Network examples may require internet connectivity or running services
- Examples include comprehensive error handling and logging
- All code follows Lua best practices and plua conventions

## Development and Testing

For internal development examples and tests that use `_PY` functions or other internals, see the `dev/` directory instead.
