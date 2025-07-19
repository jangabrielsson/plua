# HTTP Debug Tools

This directory contains various debug tools and test scripts for the plua2 HTTP server implementation.

## Debug Files

### `debug_http_server.lua`
- Simple HTTP server for basic testing
- Minimal setup with basic request logging
- Good for quick tests and troubleshooting

### `debug_http_response_format.lua`
- Tests HTTP response formatting
- Multiple endpoints with different content types
- Includes commands for raw response inspection with curl and netcat
- Use this to verify proper HTTP headers and CRLF formatting

### `debug_http_request_parser.lua`
- Tests HTTP request parsing capabilities
- Detailed logging of incoming requests
- Shows how different HTTP methods and payloads are processed
- Good for debugging request handling issues

### `debug_http_stress_test.lua`
- Tests concurrent connections and persistent callbacks
- Includes slow and fast endpoints for concurrency testing
- Request counting and statistics
- Use this to verify that callbacks remain persistent

### `debug_network_utils.lua`
- Utility module with helper functions for debugging
- Colored terminal output
- Hex dump functionality
- JSON parsing tests
- Benchmark utilities

### `debug_http_test_suite.lua`
- Comprehensive test suite using the debug utilities
- Colorized output for easy reading
- Multiple test endpoints for different scenarios
- Self-test functionality with benchmarking

### `test_simple_isrunning.lua`
- Test script for the new `_PY.isRunning` hook feature
- Shows how scripts can auto-terminate when work is complete
- Timer-based example with automatic cleanup

### `test_isrunning_hook.lua`
- HTTP server test for the `_PY.isRunning` hook
- Demonstrates termination based on request count and runtime state
- More complex example with multiple termination conditions

### `ISRUNNING_HOOK_DOCS.md`
- Complete documentation for the `_PY.isRunning` hook feature
- Examples and best practices for automatic script termination

## Usage Examples

### Start a debug server:
```bash
cd /Users/jangabrielsson/Documents/dev/plua2
lua dev/debug_http_response_format.lua
```

### Test HTTP response formatting:
```bash
# In another terminal:
curl -v http://localhost:8095/raw
curl -v http://localhost:8095/json

# Raw byte inspection:
echo -e 'GET /raw HTTP/1.1\r\nHost: localhost:8095\r\n\r\n' | nc localhost 8095 | hexdump -C
```

### Test request parsing:
```bash
lua dev/debug_http_request_parser.lua

# Test different request types:
curl -X POST http://localhost:8096/test -d '{"test": "data"}'
curl -X PUT http://localhost:8096/update -d 'some data'
```

### Stress test concurrent connections:
```bash
lua dev/debug_http_stress_test.lua

# Test concurrency:
curl http://localhost:8097/slow &
curl http://localhost:8097/fast &
curl http://localhost:8097/fast &
curl http://localhost:8097/stats
```

### Full debug test suite:
```bash
lua dev/debug_http_test_suite.lua

# Test all endpoints:
curl http://localhost:8098/debug/hex
curl http://localhost:8098/debug/json
curl http://localhost:8098/debug/large
```

## Debugging Tips

1. **Response Format Issues**: Use `debug_http_response_format.lua` with netcat and hexdump
2. **Request Parsing Issues**: Use `debug_http_request_parser.lua` to see exactly what the server receives
3. **Callback Persistence**: Use `debug_http_stress_test.lua` to verify callbacks work after multiple requests
4. **Performance Issues**: Use the benchmark functions in `debug_network_utils.lua`
5. **General Issues**: Use `debug_http_test_suite.lua` for comprehensive testing with colorized output

## Common Debug Commands

```bash
# Kill any lingering servers:
kill -9 $(lsof -ti:8095-8098) 2>/dev/null || true

# Check what's listening on ports:
lsof -i :8095-8098

# Monitor server logs while testing:
lua dev/debug_http_test_suite.lua | tee debug.log
```
