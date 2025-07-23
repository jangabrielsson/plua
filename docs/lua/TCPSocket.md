# TCP Socket API

The TCP socket API provides low-level networking capabilities for creating TCP clients and servers with full control over connection lifecycle and data flow.

## 📡 TCP Client

### Basic Client Connection

```lua
local client = net.TCPSocket()

client:connect("www.google.com", 80, {
    connected = function()
        print("✓ Connected to server")
        
        -- Send HTTP request
        local request = "GET / HTTP/1.1\r\nHost: www.google.com\r\nConnection: close\r\n\r\n"
        client:send(request)
    end,
    
    data = function(data)
        print("Received:", #data, "bytes")
        print(data:sub(1, 200) .. "...")  -- Show first 200 chars
    end,
    
    disconnected = function()
        print("✓ Disconnected from server")
    end,
    
    error = function(error)
        print("✗ Connection error:", error)
    end
})
```

### HTTP Client Example

```lua
local function http_get(host, port, path)
    local client = net.TCPSocket()
    local response_data = ""
    
    client:connect(host, port, {
        connected = function()
            local request = string.format(
                "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n",
                path, host
            )
            client:send(request)
        end,
        
        data = function(data)
            response_data = response_data .. data
        end,
        
        disconnected = function()
            -- Parse HTTP response
            local status_line = response_data:match("HTTP/1%.1 (%d+)")
            local body = response_data:match("\r\n\r\n(.*)$")
            
            print("HTTP Status:", status_line)
            print("Response Body:", body and body:sub(1, 500) or "No body")
        end,
        
        error = function(error)
            print("HTTP request failed:", error)
        end
    })
end

-- Usage
http_get("httpbin.org", 80, "/json")
```

### Echo Client Example

```lua
local client = net.TCPSocket()

client:connect("localhost", 8888, {
    connected = function()
        print("✓ Connected to echo server")
        
        -- Send test messages
        client:send("Hello, server!")
        
        setTimeout(function()
            client:send("This is message 2")
        end, 1000)
        
        setTimeout(function()
            client:send("Goodbye!")
        end, 2000)
    end,
    
    data = function(data)
        print("Echo received:", data)
    end,
    
    disconnected = function()
        print("✓ Disconnected from echo server")
    end,
    
    error = function(error)
        print("✗ Client error:", error)
    end
})
```

## 🖥️ TCP Server

### Basic Echo Server

```lua
local server = net.TCPServer()

server:listen("localhost", 8888, {
    connected = function(client_id)
        print("✓ Client connected:", client_id)
        server:send(client_id, "Welcome to echo server!\n")
    end,
    
    data = function(client_id, data)
        print(string.format("Client %s sent: %s", client_id, data:gsub("\n", "\\n")))
        
        -- Echo the data back
        server:send(client_id, "Echo: " .. data)
    end,
    
    disconnected = function(client_id)
        print("✓ Client disconnected:", client_id)
    end,
    
    started = function()
        print("✓ TCP server listening on localhost:8888")
    end,
    
    error = function(error)
        print("✗ Server error:", error)
    end
})
```

### Chat Server Example

```lua
local server = net.TCPServer()
local clients = {}
local client_names = {}

local function broadcast(message, sender_id)
    for client_id, _ in pairs(clients) do
        if client_id ~= sender_id then
            server:send(client_id, message)
        end
    end
end

server:listen("localhost", 8889, {
    connected = function(client_id)
        clients[client_id] = true
        print("✓ Client connected:", client_id)
        
        server:send(client_id, "Welcome to plua2 chat! Enter your name: ")
    end,
    
    data = function(client_id, data)
        local message = data:gsub("[\r\n]+", "")
        
        if not client_names[client_id] then
            -- First message is the name
            client_names[client_id] = message
            server:send(client_id, "Hello " .. message .. "! You can now chat.\n")
            broadcast(message .. " joined the chat\n", client_id)
        else
            -- Regular chat message
            local chat_message = client_names[client_id] .. ": " .. message .. "\n"
            print("Chat:", chat_message:gsub("\n", ""))
            broadcast(chat_message, client_id)
        end
    end,
    
    disconnected = function(client_id)
        if client_names[client_id] then
            broadcast(client_names[client_id] .. " left the chat\n", client_id)
            client_names[client_id] = nil
        end
        clients[client_id] = nil
        print("✓ Client disconnected:", client_id)
    end,
    
    started = function()
        print("✓ Chat server listening on localhost:8889")
        print("Connect with: telnet localhost 8889")
    end,
    
    error = function(error)
        print("✗ Chat server error:", error)
    end
})
```

### HTTP Server Example

```lua
local server = net.TCPServer()

local function parse_http_request(data)
    local lines = {}
    for line in data:gmatch("[^\r\n]+") do
        table.insert(lines, line)
    end
    
    if #lines == 0 then return nil end
    
    local method, path, version = lines[1]:match("(%S+) (%S+) (%S+)")
    local headers = {}
    
    for i = 2, #lines do
        if lines[i] == "" then break end
        local key, value = lines[i]:match("([^:]+): (.+)")
        if key and value then
            headers[key:lower()] = value
        end
    end
    
    return {
        method = method,
        path = path,
        version = version,
        headers = headers
    }
end

local function send_http_response(client_id, status, content, content_type)
    content_type = content_type or "text/plain"
    local response = string.format(
        "HTTP/1.1 %d OK\r\nContent-Type: %s\r\nContent-Length: %d\r\nConnection: close\r\n\r\n%s",
        status, content_type, #content, content
    )
    server:send(client_id, response)
end

server:listen("localhost", 8890, {
    connected = function(client_id)
        print("✓ HTTP client connected:", client_id)
    end,
    
    data = function(client_id, data)
        local request = parse_http_request(data)
        
        if request then
            print(string.format("HTTP %s %s", request.method, request.path))
            
            if request.path == "/" then
                local html = [[
<!DOCTYPE html>
<html>
<head><title>plua2 TCP HTTP Server</title></head>
<body>
    <h1>Hello from plua2!</h1>
    <p>This HTTP response was generated by a TCP server written in Lua.</p>
    <p>Try <a href="/time">/time</a> for the current time.</p>
</body>
</html>]]
                send_http_response(client_id, 200, html, "text/html")
                
            elseif request.path == "/time" then
                local time_json = json.encode({
                    time = os.date(),
                    timestamp = os.time(),
                    server = "plua2-tcp"
                })
                send_http_response(client_id, 200, time_json, "application/json")
                
            else
                send_http_response(client_id, 404, "Not Found")
            end
            
            -- Close connection after response
            setTimeout(function()
                server:disconnect(client_id)
            end, 100)
        end
    end,
    
    disconnected = function(client_id)
        print("✓ HTTP client disconnected:", client_id)
    end,
    
    started = function()
        print("✓ HTTP server listening on localhost:8890")
        print("Visit: http://localhost:8890")
    end,
    
    error = function(error)
        print("✗ HTTP server error:", error)
    end
})
```

## 🔧 Client Methods

### `client:connect(host, port, callbacks)`
Connect to a TCP server.

**Parameters:**
- `host` - Server hostname or IP address
- `port` - Server port number
- `callbacks` - Table with callback functions

**Callbacks:**
- `connected()` - Connection established
- `data(data)` - Data received from server
- `disconnected()` - Connection closed
- `error(error_message)` - Connection error

### `client:send(data)`
Send data to the connected server.

**Parameters:**
- `data` - String data to send

### `client:disconnect()`
Close the connection to the server.

## 🖥️ Server Methods

### `server:listen(host, port, callbacks)`
Start listening for TCP connections.

**Parameters:**
- `host` - Interface to bind to ("localhost", "0.0.0.0", etc.)
- `port` - Port number to listen on
- `callbacks` - Table with callback functions

**Callbacks:**
- `connected(client_id)` - New client connected
- `data(client_id, data)` - Data received from client
- `disconnected(client_id)` - Client disconnected
- `started()` - Server started successfully
- `error(error_message)` - Server error

### `server:send(client_id, data)`
Send data to a specific client.

**Parameters:**
- `client_id` - Client identifier from callbacks
- `data` - String data to send

### `server:disconnect(client_id)`
Disconnect a specific client.

**Parameters:**
- `client_id` - Client identifier to disconnect

### `server:stop()`
Stop the TCP server and disconnect all clients.

## 🧪 Testing Examples

### Test TCP Connection

```lua
-- Start a simple echo server for testing
local server = net.TCPServer()
server:listen("localhost", 9999, {
    connected = function(client_id)
        print("Test client connected")
    end,
    
    data = function(client_id, data)
        server:send(client_id, "Echo: " .. data)
    end,
    
    started = function()
        print("✓ Test server ready")
        
        -- Connect a test client
        local client = net.TCPSocket()
        client:connect("localhost", 9999, {
            connected = function()
                print("✓ Test client connected")
                client:send("Hello, test!")
            end,
            
            data = function(data)
                print("✓ Received:", data)
                client:disconnect()
            end,
            
            disconnected = function()
                print("✓ Test completed")
                server:stop()
            end
        })
    end
})
```

### Performance Test

```lua
local server = net.TCPServer()
local message_count = 0
local start_time = os.time()

-- High-throughput echo server
server:listen("localhost", 10000, {
    data = function(client_id, data)
        message_count = message_count + 1
        server:send(client_id, data)  -- Echo back
        
        if message_count % 1000 == 0 then
            local elapsed = os.time() - start_time
            print(string.format("Processed %d messages in %d seconds (%.1f msg/sec)", 
                  message_count, elapsed, message_count / elapsed))
        end
    end,
    
    started = function()
        print("✓ Performance test server ready on localhost:10000")
    end
})
```

## 💡 Best Practices

### Connection Management
```lua
-- Keep track of active connections
local active_clients = {}

server:listen("localhost", port, {
    connected = function(client_id)
        active_clients[client_id] = {
            connected_at = os.time(),
            bytes_sent = 0,
            bytes_received = 0
        }
    end,
    
    disconnected = function(client_id)
        local info = active_clients[client_id]
        if info then
            print(string.format("Client %s: session lasted %d seconds, %d bytes in, %d bytes out",
                  client_id, os.time() - info.connected_at, info.bytes_received, info.bytes_sent))
        end
        active_clients[client_id] = nil
    end
})
```

### Error Handling
```lua
-- Robust error handling
local client = net.TCPSocket()
local reconnect_count = 0
local max_reconnects = 3

local function try_connect()
    client:connect(host, port, {
        connected = function()
            reconnect_count = 0  -- Reset on successful connect
            print("✓ Connected successfully")
        end,
        
        error = function(error)
            reconnect_count = reconnect_count + 1
            print(string.format("✗ Connection failed (attempt %d/%d): %s", 
                  reconnect_count, max_reconnects, error))
            
            if reconnect_count < max_reconnects then
                setTimeout(try_connect, 5000)  -- Retry after 5 seconds
            else
                print("✗ Max reconnection attempts reached")
            end
        end
    })
end

try_connect()
```

### Data Framing
```lua
-- Handle message boundaries in streaming data
local function create_line_handler()
    local buffer = ""
    
    return function(data)
        buffer = buffer .. data
        
        while true do
            local line, rest = buffer:match("([^\n]*)\n(.*)")
            if not line then break end
            
            buffer = rest
            
            -- Process complete line
            handle_message(line)
        end
    end
end

local line_handler = create_line_handler()

client:connect(host, port, {
    data = line_handler
})
```

## 🚀 Advanced Examples

See the [examples directory](../../examples/) for more comprehensive TCP socket examples including:
- File transfer protocols
- Custom binary protocols  
- Load balancing servers
- Proxy implementations
