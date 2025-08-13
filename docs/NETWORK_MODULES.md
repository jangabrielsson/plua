# Network Module Organization

## Overview

The EPLua network functionality has been reorganized into separate modules for better maintainability and cleaner code organization.

## Module Structure

### Current Modules

#### `http.py`
- **Status**: ✅ Implemented
- **Functions**: `call_http()`
- **Features**: 
  - Async HTTP requests (GET, POST, PUT, DELETE, etc.)
  - JSON and form data support
  - Custom headers and timeout
  - Response parsing (JSON, text, headers, status)

#### `sync_socket.py`
- **Status**: ✅ Implemented  
- **Functions**: `tcp_connect_sync()`, `tcp_write_sync()`, `tcp_read_sync()`, `tcp_close_sync()`, `tcp_set_timeout_sync()`, `http_call_sync()`
- **Features**: Synchronous TCP operations for MobDebug compatibility

### Planned Modules

#### `tcp.py`
- **Status**: 🚧 Placeholder created
- **Planned Functions**: `tcp_connect()`, `tcp_listen()`, `tcp_send()`, `tcp_receive()`
- **Features**: 
  - Async TCP client connections
  - TCP server sockets
  - Connection pooling
  - Binary and text data transfer

#### `udp.py`
- **Status**: 🚧 Placeholder created
- **Planned Functions**: `udp_socket()`, `udp_send()`, `udp_receive()`, `udp_broadcast()`
- **Features**:
  - UDP client/server sockets
  - Broadcast and multicast support
  - Async UDP operations

#### `websocket.py`
- **Status**: 🚧 Placeholder created
- **Planned Functions**: `ws_connect()`, `ws_send()`, `ws_close()`, `ws_server()`
- **Features**:
  - WebSocket client connections
  - WebSocket server endpoints
  - Real-time bidirectional communication
  - Message frame handling

#### `mqtt.py`
- **Status**: ✅ Implemented
- **Functions**: `mqtt_client_connect()`, `mqtt_client_publish()`, `mqtt_client_subscribe()`, `mqtt_client_unsubscribe()`, `mqtt_client_disconnect()`, `mqtt_client_is_connected()`, `mqtt_client_get_info()`, `mqtt_client_add_event_listener()`, `mqtt_client_remove_event_listener()`
- **Features**:
  - Async MQTT client connections (mqtt:// and mqtts://)
  - Publish/Subscribe operations with QoS support
  - Event-driven architecture with persistent callbacks
  - Connection state management
  - Automatic SSL/TLS for secure connections
  - Comprehensive error handling and reconnection support

## Benefits of Modular Architecture

1. **Better Code Organization**: Each protocol has its own dedicated file
2. **Easier Maintenance**: Smaller, focused modules are easier to maintain
3. **Cleaner Separation**: Each module handles only its specific protocol
4. **Reduced File Size**: Avoids creating large monolithic network files
5. **Easier Testing**: Each module can be tested independently
6. **Flexible Loading**: Only import what you need

## Migration from `network.py`

The original `network.py` file has been renamed to `http.py` to better reflect its specific functionality. All HTTP-related code remains in this module, and the imports have been updated throughout the codebase.

### Changed Files:
- `src/eplua/network.py` → `src/eplua/http.py`
- `src/eplua/__init__.py` (updated import)
- `src/eplua/extensions.py` (updated import)

## Usage Examples

### HTTP Requests
```lua
-- Use HTTP functionality
local function on_response(err, response)
    if err then
        _PY.print("Error: " .. err)
    else
        _PY.print("Status: " .. response.status)
        _PY.print("Response: " .. response.text)
    end
end

-- Make HTTP request
local callback_id = registerCallback(on_response)
_PY.call_http("https://api.example.com/data", {
    method = "GET",
    headers = {["Content-Type"] = "application/json"}
}, callback_id)
```

### Future TCP Usage (when implemented)
```lua
-- Future TCP functionality
local function on_connect(err, connection)
    if not err then
        _PY.tcp_send(connection, "Hello TCP!")
    end
end

local callback_id = registerCallback(on_connect)
_PY.tcp_connect("example.com", 80, callback_id)
```
