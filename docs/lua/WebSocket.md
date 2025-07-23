# WebSocket API

The WebSocket API provides full-duplex communication over a single TCP connection, enabling real-time, bidirectional data exchange between clients and servers.

## 📡 WebSocket Client

### Basic WebSocket Client

```lua
local client = net.WebSocketClient()

client:connect("ws://echo.websocket.org", {
    connected = function()
        print("✓ Connected to WebSocket server")
        client:send("Hello, WebSocket!")
    end,
    
    message = function(data)
        print("Received:", data)
        
        -- Send another message
        client:send("This is message 2")
        
        -- Close after a delay
        setTimeout(function()
            client:close()
        end, 2000)
    end,
    
    closed = function()
        print("✓ WebSocket connection closed")
    end,
    
    error = function(error)
        print("✗ WebSocket error:", error)
    end
})
```

### Secure WebSocket Client (TLS)

```lua
local secure_client = net.WebSocketClientTls()

secure_client:connect("wss://echo.websocket.org", {
    connected = function()
        print("✓ Secure WebSocket connected")
        
        -- Send JSON data
        local message = json.encode({
            type = "greeting",
            message = "Hello from plua2!",
            timestamp = os.time()
        })
        
        secure_client:send(message)
    end,
    
    message = function(data)
        print("Secure response:", data)
        
        local success, json_data = pcall(json.decode, data)
        if success then
            print("Parsed JSON:", json_data.type, json_data.message)
        end
    end,
    
    closed = function()
        print("✓ Secure WebSocket closed")
    end,
    
    error = function(error)
        print("✗ Secure WebSocket error:", error)
    end
})
```

### Chat Client Example

```lua
local function create_chat_client(username)
    local client = net.WebSocketClient()
    
    client:connect("ws://localhost:8888/chat", {
        connected = function()
            print("✓ Chat connected as:", username)
            
            -- Send join message
            client:send(json.encode({
                type = "join",
                username = username
            }))
            
            -- Send a few test messages
            setTimeout(function()
                client:send(json.encode({
                    type = "message",
                    text = "Hello everyone!"
                }))
            end, 1000)
            
            setTimeout(function()
                client:send(json.encode({
                    type = "message", 
                    text = "How is everyone doing?"
                }))
            end, 3000)
        end,
        
        message = function(data)
            local success, msg = pcall(json.decode, data)
            if success then
                if msg.type == "message" then
                    print(string.format("<%s> %s", msg.username, msg.text))
                elseif msg.type == "join" then
                    print(string.format("*** %s joined the chat", msg.username))
                elseif msg.type == "leave" then
                    print(string.format("*** %s left the chat", msg.username))
                end
            else
                print("Raw message:", data)
            end
        end,
        
        closed = function()
            print("✓ Chat disconnected")
        end,
        
        error = function(error)
            print("✗ Chat error:", error)
        end
    })
    
    return client
end

-- Create test chat clients
local alice = create_chat_client("Alice")
local bob = create_chat_client("Bob")
```

## 🖥️ WebSocket Server

### Basic Echo Server

```lua
local server = net.WebSocketServer()

server:start("localhost", 8888, {
    connected = function(client_id)
        print("✓ WebSocket client connected:", client_id)
        server:send(client_id, "Welcome to the echo server!")
    end,
    
    message = function(client_id, data)
        print(string.format("Client %s sent: %s", client_id, data))
        
        -- Echo the message back
        server:send(client_id, "Echo: " .. data)
    end,
    
    disconnected = function(client_id)
        print("✓ WebSocket client disconnected:", client_id)
    end,
    
    started = function()
        print("✓ WebSocket server started on ws://localhost:8888")
    end,
    
    error = function(error)
        print("✗ WebSocket server error:", error)
    end
})
```

### Chat Server

```lua
local chat_server = net.WebSocketServer()
local clients = {}
local usernames = {}

local function broadcast(message, sender_id)
    for client_id, _ in pairs(clients) do
        if client_id ~= sender_id then
            chat_server:send(client_id, message)
        end
    end
end

chat_server:start("localhost", 8888, {
    connected = function(client_id)
        clients[client_id] = true
        print("✓ Chat client connected:", client_id)
    end,
    
    message = function(client_id, data)
        local success, msg = pcall(json.decode, data)
        if not success then
            print("Invalid JSON from client:", client_id)
            return
        end
        
        if msg.type == "join" then
            usernames[client_id] = msg.username
            print(string.format("%s joined as %s", client_id, msg.username))
            
            -- Notify other clients
            broadcast(json.encode({
                type = "join",
                username = msg.username
            }), client_id)
            
        elseif msg.type == "message" then
            local username = usernames[client_id]
            if username then
                print(string.format("<%s> %s", username, msg.text))
                
                -- Broadcast to all clients
                broadcast(json.encode({
                    type = "message",
                    username = username,
                    text = msg.text,
                    timestamp = os.time()
                }), client_id)
            end
        end
    end,
    
    disconnected = function(client_id)
        local username = usernames[client_id]
        if username then
            print(string.format("%s (%s) disconnected", client_id, username))
            
            -- Notify other clients
            broadcast(json.encode({
                type = "leave",
                username = username
            }), client_id)
            
            usernames[client_id] = nil
        end
        clients[client_id] = nil
    end,
    
    started = function()
        print("✓ Chat server started on ws://localhost:8888")
    end,
    
    error = function(error)
        print("✗ Chat server error:", error)
    end
})
```

### Real-time Data Server

```lua
local data_server = net.WebSocketServer()
local subscribers = {}

-- Data generator (simulated sensor data)
local function generate_sensor_data()
    return {
        timestamp = os.time(),
        temperature = 20 + math.random() * 10,
        humidity = 40 + math.random() * 20,
        pressure = 1000 + math.random() * 50
    }
end

data_server:start("localhost", 8889, {
    connected = function(client_id)
        subscribers[client_id] = true
        print("✓ Data subscriber connected:", client_id)
        
        -- Send initial data
        data_server:send(client_id, json.encode({
            type = "welcome",
            message = "Connected to sensor data stream"
        }))
    end,
    
    message = function(client_id, data)
        local success, msg = pcall(json.decode, data)
        if success and msg.type == "subscribe" then
            print("Client", client_id, "subscribed to:", msg.channel)
            
            data_server:send(client_id, json.encode({
                type = "subscribed",
                channel = msg.channel
            }))
        end
    end,
    
    disconnected = function(client_id)
        subscribers[client_id] = nil
        print("✓ Data subscriber disconnected:", client_id)
    end,
    
    started = function()
        print("✓ Data server started on ws://localhost:8889")
        
        -- Broadcast sensor data every 2 seconds
        local function broadcast_data()
            if next(subscribers) then  -- Only if there are subscribers
                local sensor_data = generate_sensor_data()
                local message = json.encode({
                    type = "sensor_data",
                    data = sensor_data
                })
                
                for client_id, _ in pairs(subscribers) do
                    data_server:send(client_id, message)
                end
                
                print(string.format("Broadcasted data to %d subscribers: T=%.1f°C, H=%.1f%%, P=%.1fhPa",
                      table_count(subscribers), sensor_data.temperature, 
                      sensor_data.humidity, sensor_data.pressure))
            end
            
            setTimeout(broadcast_data, 2000)
        end
        
        broadcast_data()
    end,
    
    error = function(error)
        print("✗ Data server error:", error)
    end
})

-- Helper function to count table entries
function table_count(t)
    local count = 0
    for _ in pairs(t) do count = count + 1 end
    return count
end
```

## 🔄 Echo Server Utility

For quick testing, use the built-in echo server:

```lua
-- Start an echo server for testing
local echo = net.WebSocketEchoServer("localhost", 8890)

-- Test it with a client
setTimeout(function()
    local client = net.WebSocketClient()
    client:connect("ws://localhost:8890", {
        connected = function()
            print("✓ Connected to echo server")
            client:send("Hello, echo!")
        end,
        
        message = function(data)
            print("Echo response:", data)
            client:close()
        end,
        
        closed = function()
            echo:stop()
            print("✓ Echo test completed")
        end
    })
end, 1000)
```

## 🔧 Client Methods

### `client:connect(url, callbacks)`
Connect to a WebSocket server.

**Parameters:**
- `url` - WebSocket URL (ws:// or wss://)
- `callbacks` - Table with callback functions

**Callbacks:**
- `connected()` - Connection established
- `message(data)` - Message received from server
- `closed()` - Connection closed
- `error(error_message)` - Connection error

### `client:send(data)`
Send data to the connected server.

**Parameters:**
- `data` - String data to send

### `client:close()`
Close the WebSocket connection.

## 🖥️ Server Methods

### `server:start(host, port, callbacks)`
Start the WebSocket server.

**Parameters:**
- `host` - Host to bind to ("localhost", "0.0.0.0", etc.)
- `port` - Port number to listen on
- `callbacks` - Table with callback functions

**Callbacks:**
- `connected(client_id)` - New client connected
- `message(client_id, data)` - Message received from client
- `disconnected(client_id)` - Client disconnected
- `started()` - Server started successfully
- `error(error_message)` - Server error

### `server:send(client_id, data)`
Send data to a specific client.

**Parameters:**
- `client_id` - Client identifier from callbacks
- `data` - String data to send

### `server:stop()`
Stop the WebSocket server.

## 🧪 Testing Examples

### Connection Test

```lua
-- Test WebSocket connection with public echo server
local function test_public_echo()
    local client = net.WebSocketClient()
    
    client:connect("ws://echo.websocket.org", {
        connected = function()
            print("✓ Connected to public echo server")
            client:send("Test message from plua2")
        end,
        
        message = function(data)
            print("✓ Echo received:", data)
            client:close()
        end,
        
        closed = function()
            print("✓ Public echo test completed")
        end,
        
        error = function(error)
            print("✗ Public echo test failed:", error)
        end
    })
end

test_public_echo()
```

### Stress Test

```lua
local function websocket_stress_test()
    local server = net.WebSocketServer()
    local message_count = 0
    local start_time = os.time()
    
    server:start("localhost", 9999, {
        message = function(client_id, data)
            message_count = message_count + 1
            server:send(client_id, data)  -- Echo back
            
            if message_count % 100 == 0 then
                local elapsed = os.time() - start_time
                print(string.format("Processed %d messages in %d seconds (%.1f msg/sec)",
                      message_count, elapsed, message_count / elapsed))
            end
        end,
        
        started = function()
            print("✓ Stress test server ready")
            
            -- Connect test client and send many messages
            local client = net.WebSocketClient()
            client:connect("ws://localhost:9999", {
                connected = function()
                    print("✓ Stress test client connected")
                    
                    -- Send 1000 messages rapidly
                    for i = 1, 1000 do
                        client:send("stress test message " .. i)
                    end
                end,
                
                message = function(data)
                    -- Echo received
                end
            })
        end
    })
end

websocket_stress_test()
```

## 💡 Best Practices

### Message Validation
```lua
-- Always validate incoming JSON messages
server:start("localhost", port, {
    message = function(client_id, data)
        local success, msg = pcall(json.decode, data)
        
        if not success then
            server:send(client_id, json.encode({
                type = "error",
                message = "Invalid JSON format"
            }))
            return
        end
        
        -- Validate required fields
        if not msg.type then
            server:send(client_id, json.encode({
                type = "error", 
                message = "Missing message type"
            }))
            return
        end
        
        -- Process valid message
        handle_message(client_id, msg)
    end
})
```

### Connection Management
```lua
-- Track client connections and metadata
local clients = {}

server:start("localhost", port, {
    connected = function(client_id)
        clients[client_id] = {
            connected_at = os.time(),
            message_count = 0,
            last_activity = os.time()
        }
        
        print(string.format("Client %s connected (total: %d)", 
              client_id, table_count(clients)))
    end,
    
    message = function(client_id, data)
        local client_info = clients[client_id]
        if client_info then
            client_info.message_count = client_info.message_count + 1
            client_info.last_activity = os.time()
        end
    end,
    
    disconnected = function(client_id)
        local client_info = clients[client_id]
        if client_info then
            local session_duration = os.time() - client_info.connected_at
            print(string.format("Client %s disconnected after %d seconds, %d messages",
                  client_id, session_duration, client_info.message_count))
        end
        clients[client_id] = nil
    end
})
```

### Heartbeat/Ping-Pong
```lua
-- Implement heartbeat to detect dead connections
local function setup_heartbeat(server)
    local heartbeat_interval = 30000  -- 30 seconds
    
    local function send_ping()
        for client_id, _ in pairs(clients) do
            server:send(client_id, json.encode({type = "ping"}))
        end
        setTimeout(send_ping, heartbeat_interval)
    end
    
    setTimeout(send_ping, heartbeat_interval)
end

-- Handle pong responses
server:start("localhost", port, {
    message = function(client_id, data)
        local success, msg = pcall(json.decode, data)
        
        if success and msg.type == "pong" then
            -- Update last activity
            if clients[client_id] then
                clients[client_id].last_activity = os.time()
            end
        else
            -- Handle other messages
        end
    end
})
```

## 🚀 Advanced Examples

See the [examples directory](../../examples/) for more comprehensive WebSocket examples including:
- Real-time collaboration tools
- Live dashboards
- Gaming protocols
- IoT device management
