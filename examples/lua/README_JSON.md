# JSON Module for EPLua

The JSON module provides comprehensive JSON encoding and decoding functionality for EPLua Lua scripts.

## API Reference

### json.encode(value)
Encodes a Lua value to a compact JSON string.

```lua
local json = require('json')

local data = {name = "Alice", age = 30, hobbies = {"reading", "coding"}}
local encoded = json.encode(data)
-- Result: {"name":"Alice","age":30,"hobbies":["reading","coding"]}
```

### json.decode(json_string)
Decodes a JSON string back to a Lua table.

```lua
local json_str = '{"name":"Bob","active":true,"score":95.5}'
local decoded = json.decode(json_str)
-- Result: Lua table with decoded values
print(decoded.name)   -- "Bob"
print(decoded.active) -- true
print(decoded.score)  -- 95.5
```

### json.encodeFormated(value)
Encodes a Lua value to a pretty-printed JSON string with indentation.

```lua
local data = {
    user = {
        name = "Charlie",
        settings = {theme = "dark", notifications = true}
    }
}
local formatted = json.encodeFormated(data)
-- Result: Multi-line JSON with proper indentation
```

## Supported Data Types

| Lua Type | JSON Type | Notes |
|----------|-----------|-------|
| `nil` | `null` | |
| `boolean` | `boolean` | |
| `number` | `number` | Both integers and floats |
| `string` | `string` | Unicode support |
| `table` (array) | `array` | Sequential numeric indices |
| `table` (object) | `object` | String keys |

## Features

- **High Performance**: Fast encoding/decoding optimized for Lua
- **Unicode Support**: Handles emojis and international characters
- **Nested Structures**: Supports deeply nested objects and arrays
- **Error Handling**: Graceful handling of invalid JSON
- **Pretty Printing**: Optional formatted output for readability

## Usage Examples

### Basic Usage
```lua
local json = require('json')

-- Encode
local data = {message = "Hello", count = 42}
local json_str = json.encode(data)

-- Decode
local parsed = json.decode(json_str)
```

### Configuration Files
```lua
local json = require('json')

-- Save configuration
local config = {
    server = {
        host = "localhost",
        port = 8080,
        ssl = true
    },
    features = {"auth", "logging", "metrics"}
}

local config_json = json.encodeFormated(config)
-- Write to file or send over network
```

### API Communication
```lua
local json = require('json')

-- Prepare API request
local request_data = {
    action = "user.create",
    params = {
        username = "newuser",
        email = "user@example.com"
    }
}

local request_json = json.encode(request_data)
-- Send via HTTP, WebSocket, etc.

-- Parse API response
local response_json = '{"success":true,"user_id":12345}'
local response = json.decode(response_json)
if response.success then
    print("User created with ID:", response.user_id)
end
```

## Error Handling

```lua
local json = require('json')

-- Safe decoding
local function safe_decode(json_str)
    local success, result = pcall(json.decode, json_str)
    if success then
        return result
    else
        print("JSON decode error:", result)
        return nil
    end
end

local data = safe_decode('{"invalid": json}')
```

## Performance Notes

- Encoding and decoding are optimized for speed
- Large datasets (100+ objects) process in milliseconds
- Memory usage is efficient for typical web API payloads
- Consider using `json.encode()` for network transmission (compact)
- Use `json.encodeFormated()` for configuration files (readable)

## Integration with Network Modules

The JSON module works seamlessly with EPLua's network modules:

```lua
local json = require('json')
local net = require('net')

-- HTTP POST with JSON
local data = {user = "alice", action = "login"}
net.HTTPClient():request({
    url = "https://api.example.com/auth",
    method = "POST",
    headers = {["Content-Type"] = "application/json"},
    data = json.encode(data)
}, function(response)
    if response.status == 200 then
        local result = json.decode(response.data)
        print("Login result:", result.success)
    end
end)
```

See `examples/lua/test_json.lua` for comprehensive usage examples and test cases.
