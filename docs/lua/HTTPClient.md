# HTTP Client & Server API

The `net.HTTPClient()` and `net.HTTPServer()` provide comprehensive HTTP functionality for making requests and hosting web services.

## 📡 HTTP Client

### Basic Usage

```lua
local http = net.HTTPClient()
```

### Making Requests

#### GET Request
```lua
local http = net.HTTPClient()
http:request("https://jsonplaceholder.typicode.com/posts/1", {
    success = function(response)
        print("Status:", response.status)
        print("Data:", response.data)
        
        -- Parse JSON response
        local success, json_data = pcall(json.decode, response.data)
        if success then
            print("Title:", json_data.title)
        end
    end,
    error = function(error)
        print("Request failed:", error)
    end
})
```

#### POST Request with JSON
```lua
local http = net.HTTPClient()

local post_data = {
    title = "My Post",
    body = "This is the post content",
    userId = 1
}

http:request("https://jsonplaceholder.typicode.com/posts", {
    options = {
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json"
        },
        data = json.encode(post_data),
        timeout = 30
    },
    success = function(response)
        print("Created post, status:", response.status)
        print("Response:", response.data)
    end,
    error = function(error)
        print("POST failed:", error)
    end
})
```

#### Custom Headers and Authentication
```lua
local http = net.HTTPClient()
http:request("https://api.github.com/user", {
    options = {
        method = "GET",
        headers = {
            ["Authorization"] = "token your-github-token",
            ["User-Agent"] = "plua2-app/1.0"
        },
        timeout = 15
    },
    success = function(response)
        local user = json.decode(response.data)
        print("GitHub user:", user.login)
    end,
    error = function(error)
        print("GitHub API error:", error)
    end
})
```

### Request Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `method` | string | HTTP method (GET, POST, PUT, DELETE, etc.) | "GET" |
| `headers` | table | HTTP headers | `{}` |
| `data` | string | Request body data | `nil` |
| `timeout` | number | Request timeout in seconds | 30 |

### Response Object

The success callback receives a response object with:
- `status` - HTTP status code (200, 404, etc.)
- `data` - Response body as string

## 🖥️ HTTP Server

### Basic Server

```lua
local server = net.HTTPServer()

server:start("localhost", 8080, {
    request = function(request_id, method, path, headers, body)
        print(string.format("[%s] %s %s", request_id, method, path))
        
        if path == "/" then
            server:response(request_id, 200, "Hello from plua2 HTTP server!")
        elseif path == "/api/time" then
            local response = json.encode({
                time = os.date(),
                timestamp = os.time()
            })
            server:response(request_id, 200, response, "application/json")
        else
            server:response(request_id, 404, "Not Found")
        end
    end,
    
    started = function()
        print("HTTP server started on http://localhost:8080")
    end,
    
    error = function(error)
        print("Server error:", error)
    end
})
```

### JSON API Server

```lua
local server = net.HTTPServer()
local users = {
    {id = 1, name = "Alice", email = "alice@example.com"},
    {id = 2, name = "Bob", email = "bob@example.com"}
}

server:start("localhost", 8081, {
    request = function(request_id, method, path, headers, body)
        local response_headers = {["Content-Type"] = "application/json"}
        
        if method == "GET" and path == "/api/users" then
            -- Return all users
            server:response(request_id, 200, json.encode(users), "application/json")
            
        elseif method == "GET" and path:match("^/api/users/(%d+)$") then
            -- Return specific user
            local user_id = tonumber(path:match("^/api/users/(%d+)$"))
            local user = nil
            for _, u in ipairs(users) do
                if u.id == user_id then
                    user = u
                    break
                end
            end
            
            if user then
                server:response(request_id, 200, json.encode(user), "application/json")
            else
                server:response(request_id, 404, json.encode({error = "User not found"}), "application/json")
            end
            
        elseif method == "POST" and path == "/api/users" then
            -- Create new user
            local success, new_user = pcall(json.decode, body)
            if success and new_user.name then
                new_user.id = #users + 1
                table.insert(users, new_user)
                server:response(request_id, 201, json.encode(new_user), "application/json")
            else
                server:response(request_id, 400, json.encode({error = "Invalid JSON or missing name"}), "application/json")
            end
            
        else
            server:response(request_id, 404, json.encode({error = "Endpoint not found"}), "application/json")
        end
    end,
    
    started = function()
        print("JSON API server started on http://localhost:8081")
        print("Try: curl http://localhost:8081/api/users")
    end
})
```

### File Server Example

```lua
local server = net.HTTPServer()

server:start("localhost", 8082, {
    request = function(request_id, method, path, headers, body)
        if path == "/" then
            local html = [[
<!DOCTYPE html>
<html>
<head><title>plua2 File Server</title></head>
<body>
    <h1>Welcome to plua2!</h1>
    <p>This is a simple HTTP server written in Lua.</p>
    <ul>
        <li><a href="/api/time">Current Time</a></li>
        <li><a href="/api/status">Server Status</a></li>
    </ul>
</body>
</html>]]
            server:response(request_id, 200, html, "text/html")
            
        elseif path == "/api/time" then
            local time_data = {
                current_time = os.date("%Y-%m-%d %H:%M:%S"),
                unix_timestamp = os.time(),
                server = "plua2"
            }
            server:response(request_id, 200, json.encode(time_data), "application/json")
            
        elseif path == "/api/status" then
            local status = {
                status = "running",
                uptime_seconds = os.time() - start_time,
                lua_version = _VERSION
            }
            server:response(request_id, 200, json.encode(status), "application/json")
            
        else
            server:response(request_id, 404, "Page not found", "text/plain")
        end
    end,
    
    started = function()
        start_time = os.time()
        print("File server started on http://localhost:8082")
    end
})
```

## 🧪 Testing Examples

### Test HTTP Client
```lua
-- Test with a public API
local http = net.HTTPClient()

print("Testing HTTP client...")
http:request("https://httpbin.org/json", {
    success = function(response)
        print("✓ HTTP request successful")
        print("Status:", response.status)
        local data = json.decode(response.data)
        print("Slideshow title:", data.slideshow.title)
    end,
    error = function(error)
        print("✗ HTTP request failed:", error)
    end
})
```

### Test HTTP Server
```lua
-- Start a simple test server
local server = net.HTTPServer()

server:start("localhost", 8083, {
    request = function(request_id, method, path, headers, body)
        print("Request:", method, path)
        
        local response = {
            method = method,
            path = path,
            timestamp = os.time(),
            message = "Hello from plua2!"
        }
        
        server:response(request_id, 200, json.encode(response), "application/json")
    end,
    
    started = function()
        print("✓ Test server started on http://localhost:8083")
        print("Test with: curl http://localhost:8083/test")
    end,
    
    error = function(error)
        print("✗ Server error:", error)
    end
})

-- Auto-stop after 30 seconds
setTimeout(function()
    server:stop()
    print("Test server stopped")
end, 30000)
```

## 🔧 Server Methods

### `server:start(host, port, callbacks)`
Start the HTTP server.

**Parameters:**
- `host` - Host to bind to (e.g., "localhost", "0.0.0.0")
- `port` - Port number to listen on
- `callbacks` - Table with callback functions

**Callbacks:**
- `request(request_id, method, path, headers, body)` - Handle incoming requests
- `started()` - Server started successfully
- `error(error_message)` - Error occurred

### `server:response(request_id, status_code, data, content_type)`
Send response to a request.

**Parameters:**
- `request_id` - Request ID from the request callback
- `status_code` - HTTP status code (200, 404, 500, etc.)
- `data` - Response body
- `content_type` - MIME type (optional, defaults to "text/plain")

### `server:stop()`
Stop the HTTP server.

## 💡 Best Practices

### Error Handling
```lua
-- Always handle both success and error cases
local http = net.HTTPClient()
http:request(url, {
    success = function(response)
        if response.status == 200 then
            -- Handle success
        else
            print("HTTP error status:", response.status)
        end
    end,
    error = function(error)
        -- Handle network/timeout errors
        print("Request error:", error)
    end
})
```

### JSON Validation
```lua
-- Safely parse JSON responses
local success, data = pcall(json.decode, response.data)
if success then
    print("Valid JSON:", data)
else
    print("Invalid JSON received")
end
```

### Server Resource Management
```lua
-- Keep track of server instances for cleanup
local servers = {}

local server = net.HTTPServer()
table.insert(servers, server)

-- Cleanup on shutdown
for _, srv in ipairs(servers) do
    srv:stop()
end
```

## 🚀 Advanced Examples

See the [examples directory](../../examples/) for more comprehensive HTTP client and server examples.
