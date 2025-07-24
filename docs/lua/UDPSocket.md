# UDP Socket API

The UDP socket API provides connectionless, datagram-based networking for applications requiring low-latency communication, broadcasting, or simple request-response patterns.

## 📡 UDP Client

### Basic UDP Client

```lua
local client = net.UDPSocket()

-- Bind to a local port (optional for clients)
client:bind("localhost", 0, {  -- 0 = any available port
    bound = function(port)
        print("✓ UDP client bound to port:", port)
        
        -- Send data to server
        client:sendto("Hello, UDP server!", "localhost", 8888)
    end,
    
    data = function(data, from_host, from_port)
        print(string.format("Received from %s:%d: %s", from_host, from_port, data))
    end,
    
    error = function(error)
        print("✗ UDP client error:", error)
    end
})
```

### Simple UDP Echo Client

```lua
local function udp_echo_test()
    local client = net.UDPSocket()
    
    client:bind("localhost", 0, {
        bound = function(port)
            print("✓ Echo client bound to port:", port)
            
            -- Send test messages
            client:sendto("Message 1", "localhost", 8888)
            client:sendto("Message 2", "localhost", 8888)
            client:sendto("quit", "localhost", 8888)
        end,
        
        data = function(data, from_host, from_port)
            print("Echo response:", data)
            
            if data == "quit" then
                client:close()
                print("✓ Echo test completed")
            end
        end,
        
        error = function(error)
            print("✗ Echo client error:", error)
        end
    })
end

udp_echo_test()
```

### UDP Time Client

```lua
local function query_time_server()
    local client = net.UDPSocket()
    
    client:bind("localhost", 0, {
        bound = function(port)
            print("✓ Time client ready on port:", port)
            client:sendto("TIME", "localhost", 8889)
        end,
        
        data = function(data, from_host, from_port)
            print("Current server time:", data)
            client:close()
        end,
        
        error = function(error)
            print("✗ Time client error:", error)
        end
    })
    
    -- Timeout after 5 seconds
    setTimeout(function()
        print("⚠ Time query timeout")
        client:close()
    end, 5000)
end

query_time_server()
```

## 🖥️ UDP Server

### Basic Echo Server

```lua
local server = net.UDPSocket()

server:bind("localhost", 8888, {
    bound = function(port)
        print("✓ UDP echo server listening on port:", port)
    end,
    
    data = function(data, from_host, from_port)
        print(string.format("Received from %s:%d: %s", from_host, from_port, data))
        
        if data == "quit" then
            print("Server shutting down...")
            server:close()
        else
            -- Echo the data back
            server:sendto(data, from_host, from_port)
        end
    end,
    
    error = function(error)
        print("✗ UDP server error:", error)
    end
})
```

### Time Server

```lua
local time_server = net.UDPSocket()

time_server:bind("localhost", 8889, {
    bound = function(port)
        print("✓ Time server listening on port:", port)
    end,
    
    data = function(data, from_host, from_port)
        local request = data:upper():gsub("[\r\n]", "")
        print(string.format("Time request from %s:%d: %s", from_host, from_port, request))
        
        if request == "TIME" then
            local time_response = os.date("%Y-%m-%d %H:%M:%S UTC")
            time_server:sendto(time_response, from_host, from_port)
        elseif request == "TIMESTAMP" then
            local timestamp = tostring(os.time())
            time_server:sendto(timestamp, from_host, from_port)
        else
            time_server:sendto("ERROR: Unknown command. Use TIME or TIMESTAMP", from_host, from_port)
        end
    end,
    
    error = function(error)
        print("✗ Time server error:", error)
    end
})
```

### Discovery Server

```lua
local discovery_server = net.UDPSocket()
local services = {
    {name = "web-server", port = 8080, description = "HTTP Web Server"},
    {name = "api-server", port = 8081, description = "REST API Server"},
    {name = "time-server", port = 8889, description = "Time Service"}
}

discovery_server:bind("0.0.0.0", 8890, {  -- Listen on all interfaces
    bound = function(port)
        print("✓ Discovery server listening on all interfaces, port:", port)
        print("Send 'DISCOVER' to find services")
    end,
    
    data = function(data, from_host, from_port)
        local command = data:upper():gsub("[\r\n]", "")
        
        if command == "DISCOVER" then
            print(string.format("Discovery request from %s:%d", from_host, from_port))
            
            local response = "SERVICES:\n"
            for _, service in ipairs(services) do
                response = response .. string.format("%s:%d - %s\n", 
                          service.name, service.port, service.description)
            end
            
            discovery_server:sendto(response, from_host, from_port)
            
        elseif command:match("^PING") then
            discovery_server:sendto("PONG", from_host, from_port)
            
        else
            discovery_server:sendto("UNKNOWN COMMAND", from_host, from_port)
        end
    end,
    
    error = function(error)
        print("✗ Discovery server error:", error)
    end
})
```

## 📡 UDP Broadcasting

### Broadcast Client

```lua
local function send_broadcast()
    local client = net.UDPSocket()
    
    client:bind("localhost", 0, {
        bound = function(port)
            print("✓ Broadcast client ready on port:", port)
            
            -- Send broadcast message
            local message = json.encode({
                type = "announcement",
                sender = "plua-client",
                timestamp = os.time(),
                data = "Hello, network!"
            })
            
            client:sendto(message, "255.255.255.255", 8891)
            print("✓ Broadcast sent")
            
            setTimeout(function()
                client:close()
            end, 1000)
        end,
        
        error = function(error)
            print("✗ Broadcast error:", error)
        end
    })
end

send_broadcast()
```

### Broadcast Listener

```lua
local listener = net.UDPSocket()

listener:bind("0.0.0.0", 8891, {  -- Listen for broadcasts
    bound = function(port)
        print("✓ Broadcast listener active on port:", port)
    end,
    
    data = function(data, from_host, from_port)
        print(string.format("Broadcast from %s:%d", from_host, from_port))
        
        local success, message = pcall(json.decode, data)
        if success then
            print("Type:", message.type)
            print("Sender:", message.sender)
            print("Data:", message.data)
            print("Timestamp:", os.date("%H:%M:%S", message.timestamp))
        else
            print("Raw data:", data)
        end
        print("---")
    end,
    
    error = function(error)
        print("✗ Broadcast listener error:", error)
    end
})
```

## 🎯 Multicast Example

### Multicast Publisher

```lua
local publisher = net.UDPSocket()

publisher:bind("localhost", 0, {
    bound = function(port)
        print("✓ Multicast publisher ready on port:", port)
        
        local message_count = 0
        
        -- Send multicast messages every 2 seconds
        local function send_multicast()
            message_count = message_count + 1
            
            local message = json.encode({
                sequence = message_count,
                timestamp = os.time(),
                data = "Multicast message #" .. message_count
            })
            
            publisher:sendto(message, "224.0.0.1", 8892)  -- Multicast address
            print("Sent multicast message #" .. message_count)
            
            if message_count < 10 then
                setTimeout(send_multicast, 2000)
            else
                publisher:close()
                print("✓ Multicast publishing completed")
            end
        end
        
        send_multicast()
    end,
    
    error = function(error)
        print("✗ Multicast publisher error:", error)
    end
})
```

## 🔧 UDP Socket Methods

### `socket:bind(host, port, callbacks)`
Bind the socket to a local address and port.

**Parameters:**
- `host` - Local interface to bind to ("localhost", "0.0.0.0", etc.)
- `port` - Local port number (0 for automatic assignment)
- `callbacks` - Table with callback functions

**Callbacks:**
- `bound(port)` - Socket successfully bound
- `data(data, from_host, from_port)` - Data received
- `error(error_message)` - Socket error

### `socket:sendto(data, host, port)`
Send data to a specific address and port.

**Parameters:**
- `data` - String data to send
- `host` - Destination hostname or IP
- `port` - Destination port number

### `socket:close()`
Close the UDP socket.

## 🧪 Testing Examples

### UDP Ping-Pong Test

```lua
-- Start a ping-pong server
local server = net.UDPSocket()
server:bind("localhost", 9999, {
    bound = function()
        print("✓ Ping-pong server ready")
    end,
    
    data = function(data, from_host, from_port)
        if data == "PING" then
            server:sendto("PONG", from_host, from_port)
        elseif data == "QUIT" then
            server:close()
            print("✓ Ping-pong server stopped")
        end
    end
})

-- Test with a client
setTimeout(function()
    local client = net.UDPSocket()
    client:bind("localhost", 0, {
        bound = function()
            print("✓ Ping-pong client ready")
            client:sendto("PING", "localhost", 9999)
        end,
        
        data = function(data, from_host, from_port)
            print("✓ Received:", data)
            
            -- Send quit and cleanup
            setTimeout(function()
                client:sendto("QUIT", "localhost", 9999)
                client:close()
                print("✓ Ping-pong test completed")
            end, 1000)
        end
    })
end, 500)
```

### UDP Performance Test

```lua
local function udp_performance_test()
    local server = net.UDPSocket()
    local message_count = 0
    local start_time = os.time()
    
    -- High-speed echo server
    server:bind("localhost", 10000, {
        bound = function()
            print("✓ Performance test server ready")
        end,
        
        data = function(data, from_host, from_port)
            message_count = message_count + 1
            server:sendto(data, from_host, from_port)  -- Echo back
            
            if message_count % 1000 == 0 then
                local elapsed = os.time() - start_time
                print(string.format("Processed %d messages in %d seconds (%.1f msg/sec)",
                      message_count, elapsed, message_count / elapsed))
            end
        end
    })
    
    -- Test client
    setTimeout(function()
        local client = net.UDPSocket()
        client:bind("localhost", 0, {
            bound = function()
                print("✓ Performance test client ready")
                
                -- Send 5000 messages rapidly
                for i = 1, 5000 do
                    client:sendto("test message " .. i, "localhost", 10000)
                end
            end
        })
    end, 1000)
end

udp_performance_test()
```

## 💡 Best Practices

### Message Size Limits
```lua
-- UDP has a practical limit of ~65KB per message
-- For reliability, keep messages under 1500 bytes (typical MTU)

local function send_large_data(data, host, port)
    local chunk_size = 1000  -- Safe chunk size
    local chunks = {}
    
    -- Split data into chunks
    for i = 1, #data, chunk_size do
        table.insert(chunks, data:sub(i, i + chunk_size - 1))
    end
    
    -- Send each chunk with sequence number
    for i, chunk in ipairs(chunks) do
        local packet = json.encode({
            sequence = i,
            total = #chunks,
            data = chunk
        })
        socket:sendto(packet, host, port)
    end
end
```

### Reliable UDP Pattern
```lua
-- Add acknowledgment and retry logic for reliable delivery
local function reliable_send(socket, data, host, port, timeout)
    timeout = timeout or 5000
    local message_id = tostring(os.time() * 1000)  -- Unique ID
    
    local packet = json.encode({
        id = message_id,
        data = data,
        type = "message"
    })
    
    local retry_count = 0
    local max_retries = 3
    
    local function send_with_retry()
        retry_count = retry_count + 1
        socket:sendto(packet, host, port)
        
        setTimeout(function()
            if retry_count < max_retries then
                print("Retrying message", message_id, "attempt", retry_count + 1)
                send_with_retry()
            else
                print("Message", message_id, "failed after", max_retries, "attempts")
            end
        end, timeout)
    end
    
    send_with_retry()
end
```

### UDP Error Handling
```lua
local socket = net.UDPSocket()
local is_bound = false

socket:bind("localhost", 8888, {
    bound = function(port)
        is_bound = true
        print("✓ UDP socket bound successfully to port:", port)
    end,
    
    data = function(data, from_host, from_port)
        -- Handle incoming data
    end,
    
    error = function(error)
        print("✗ UDP socket error:", error)
        
        if not is_bound then
            -- Try alternative port
            print("Trying alternative port...")
            socket:bind("localhost", 0, callbacks)  -- Any available port
        end
    end
})
```

## 🚀 Advanced Examples

See the [examples directory](../../examples/) for more comprehensive UDP examples including:
- Network discovery protocols
- Real-time gaming protocols
- IoT sensor networks
- Video streaming protocols
