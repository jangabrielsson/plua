# Internal API Examples

These examples demonstrate EPLua's **internal `_PY.*` functions** used for engine development and debugging.

⚠️ **Warning**: These are internal APIs not intended for end users. Use the high-level APIs in `examples/lua/` instead.

## Internal Functions

### Core Functions
- `_PY.setTimeout(callback, ms)` - Low-level timer
- `_PY.setInterval(callback, ms)` - Low-level interval
- `_PY.registerCallback(callback)` - Manual callback registration
- `_PY.get_time()` - System time

### Network Functions
- `_PY.call_http(url, options, callback_id)` - Raw HTTP calls
- `_PY.start_web_server(host, port)` - Web server
- `_PY.websocket_connect(url, callback_id)` - WebSocket
- `_PY.mqtt_client_connect(uri, options, callback_id)` - MQTT

### System Functions
- `_PY.gui_available()` - GUI system check
- `_PY.create_window(title, width, height)` - GUI windows


## Examples Overview

- `basic_example.lua` - Basic `_PY` timer functions
- `getting_started.lua` - Introduction to internal APIs
- `network_demo.lua` - Raw network function calls
- `api_test_server.lua` - Web server with `_PY` functions
- `gui_demo.lua` - GUI creation with internal APIs
- `test_threading.lua` - Thread management
- `test_callback_tracking.lua` - Callback registration patterns

## When to Use These

You should use these internal functions only when:

1. **Developing EPLua core** - Adding new features to the engine
2. **Debugging issues** - Understanding internal behavior
3. **Performance testing** - Measuring low-level function performance
4. **Advanced integration** - Building custom abstractions

## Migration to User APIs

If you're using `_PY.*` functions in application code, migrate to user APIs:

```lua
-- OLD (internal API)
local callback_id = _PY.registerCallback(function(err, response)
  -- handle response
end)
_PY.call_http("https://api.example.com", {}, callback_id)

-- NEW (user API)  
local http = net.HTTPClient()
http:request("https://api.example.com", {
  success = function(response)
    -- handle response
  end,
  error = function(error)
    -- handle error
  end
})
```

## Running Examples

```bash
python -m src.eplua.cli examples/py/basic_example.lua
python -m src.eplua.cli examples/py/network_demo.lua
```

**Recommendation**: Use `examples/lua/` for application development!
