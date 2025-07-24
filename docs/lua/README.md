# plua Lua API Documentation

Welcome to the plua Lua API documentation! plua provides a rich set of built-in modules and capabilities that extend standard Lua with async networking, timers, JSON handling, and more.

## 📚 Core Modules

### 🌐 Networking
- **[HTTP Client & Server](HTTPClient.md)** - Make HTTP requests and create HTTP servers
- **[TCP Sockets](TCPSocket.md)** - TCP client and server functionality
- **[UDP Sockets](UDPSocket.md)** - UDP socket communication
- **[WebSockets](WebSocket.md)** - WebSocket clients and servers

### ⏰ Async Operations
- **[Timers](Timers.md)** - setTimeout, clearTimeout, and setInterval

### 📄 Data Handling
- **JSON** - Built-in `json.encode()` and `json.decode()`

### 🔧 Utility Functions
- **[PLUA Module](Plua.md)** - Built-in utility functions for file operations, browser integration, and runtime access

### 🔧 Fibaro and QuickApp Support
- **[Fibaro functions](Fibaro.md)** - fibaro.* functions supported
- **[QuickApp functions](QuickApp.md)** - QuickApp classes

## 🚀 Quick Start Examples

### Simple HTTP Request
```lua
local http = net.HTTPClient()
http:request("https://api.github.com/users/octocat", {
    success = function(response)
        print("Status:", response.status)
        print("Data:", response.data)
    end,
    error = function(error)
        print("Error:", error)
    end
})
```

### WebSocket Echo Server
```lua
local echoServer = net.WebSocketEchoServer("localhost", 8080, true)
print("WebSocket echo server running on ws://localhost:8080")
```

### Simple Timer
```lua
setTimeout(function()
    print("This runs after 2 seconds!")
end, 2000)
```

## 🎯 Key Features

### **Async by Design**
All network operations are asynchronous and callback-based, allowing your Lua scripts to handle multiple operations concurrently without blocking.

### **Fibaro HC3 Compatible**
The networking APIs follow Fibaro Home Center 3 specifications, making it easy to migrate QuickApps and scenes.

### **JavaScript-style Timers**
Familiar `setTimeout`, `clearTimeout`, and `setInterval` functions work just like in JavaScript.

### **Built-in JSON Support**
No need to require external libraries - JSON encoding and decoding are built-in.

## 📖 Module Documentation

| Module | Description | Key Functions |
|--------|-------------|---------------|
| [HTTPClient](HTTPClient.md) | HTTP client and server | `net.HTTPClient()`, `net.HTTPServer()` |
| [TCPSocket](TCPSocket.md) | TCP networking | `net.TCPSocket()`, `net.TCPServer()` |
| [UDPSocket](UDPSocket.md) | UDP networking | `net.UDPSocket()` |
| [WebSocket](WebSocket.md) | WebSocket communication | `net.WebSocketClient()`, `net.WebSocketServer()` |
| [Timers](Timers.md) | Async timers | `setTimeout()`, `clearTimeout()`, `setInterval()` |
| [PLUA](Plua.md) | Built-in utility functions | `PLUA.readFile()`, `PLUA.openBrowser()`, `PLUA.base64Encode()` |

## 🔧 Development Patterns

### Error Handling
```lua
-- Always provide error callbacks for network operations
local client = net.TCPSocket()
client:connect("example.com", 80, {
    success = function()
        print("Connected!")
    end,
    error = function(err)
        print("Connection failed:", err)
    end
})
```

### Resource Cleanup
```lua
-- Remember to close connections
local ws = net.WebSocketClient()
-- ... use websocket ...
ws:close()  -- Clean up when done
```

### JSON Handling
```lua
-- Encoding
local data = {name = "Alice", age = 30}
local json_string = json.encode(data)

-- Decoding
local success, result = pcall(json.decode, json_string)
if success then
    print("Name:", result.name)
else
    print("JSON parse error:", result)
end
```

## 🏃‍♂️ Running Examples

To run the examples in this documentation:

1. **Start plua:**
   ```bash
   plua your_script.lua
   ```

2. **With API server:**
   ```bash
   plua --api-port 8888 your_script.lua
   ```

3. **Interactive REPL:**
   ```bash
   plua
   ```

## 📚 Additional Resources

- **[Web REPL Examples](../WEB_REPL_HTML_EXAMPLES.md)** - HTML rendering in the web interface
- **[REST API Documentation](../api/README.md)** - HTTP API reference
- **[Main README](../../README.md)** - Project overview and installation

## 🤝 Contributing

Found an issue with the documentation? Want to add examples? Please contribute to the [plua repository](https://github.com/jangabrielsson/plua).
