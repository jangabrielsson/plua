-- Comprehensive network test demonstrating HTTP server and client

-- Load JSON module
local json = _PY.loadPythonModule("json") or require("json") or {}

-- Fallback JSON functions if module loading fails
if not json.encode then
  json.encode = function(data)
    if type(data) == "table" then
      local result = "{"
      local first = true
      for k, v in pairs(data) do
        if not first then result = result .. "," end
        result = result .. '"' .. tostring(k) .. '":' 
        if type(v) == "string" then
          result = result .. '"' .. tostring(v) .. '"'
        elseif type(v) == "table" then
          result = result .. json.encode(v)
        else
          result = result .. tostring(v)
        end
        first = false
      end
      return result .. "}"
    else
      return '"' .. tostring(data) .. '"'
    end
  end
end

if not json.decode then
  json.decode = function(str)
    -- Simple JSON decode - just return empty table for testing
    return {}
  end
end

-- Test 1: HTTP Server with JSON API
local http_server = net.HTTPServer()

-- API data store
local users = {
  {id = 1, name = "Alice", email = "alice@example.com"},
  {id = 2, name = "Bob", email = "bob@example.com"}
}

-- Start HTTP server with REST-like API
http_server:start('localhost', 8075, function(method, path, body)
  print(string.format("[Server] %s %s", method, path))
  
  -- Parse JSON body if present
  local data = nil
  if body and body ~= "" then
    local success, parsed = pcall(json.decode, body)
    if success then
      data = parsed
    end
  end
  
  -- Handle different API endpoints
  if path == "/api/users" and method == "GET" then
    return json.encode({users = users}), 200
    
  elseif path == "/api/users" and method == "POST" and data then
    -- Add new user
    local new_user = {
      id = #users + 1,
      name = data.name or "Unknown",
      email = data.email or "unknown@example.com"
    }
    table.insert(users, new_user)
    return json.encode(new_user), 201
    
  elseif path:match("^/api/users/(%d+)$") and method == "GET" then
    local user_id = tonumber(path:match("^/api/users/(%d+)$"))
    for _, user in ipairs(users) do
      if user.id == user_id then
        return json.encode(user), 200
      end
    end
    return json.encode({error = "User not found"}), 404
    
  elseif path == "/api/health" and method == "GET" then
    return json.encode({
      status = "healthy",
      timestamp = os.time(),
      server = "PLua HTTP Server"
    }), 200
    
  else
    return json.encode({error = "Endpoint not found"}), 404
  end
end)

print("🚀 HTTP Server started on localhost:8075")
print("Available endpoints:")
print("  GET  /api/health")
print("  GET  /api/users")
print("  POST /api/users")
print("  GET  /api/users/{id}")

-- Test the API after server starts
setTimeout(function()
  local client = net.HTTPClient()
  
  print("\n📡 Testing API endpoints...")
  
  -- Test 1: Health check
  client:request("http://localhost:8075/api/health", {
    options = { method = "GET" },
    success = function(response)
      print("✅ Health check:", response.status, response.data)
    end,
    error = function(err)
      print("❌ Health check error:", err)
    end
  })
  
  -- Test 2: Get all users
  setTimeout(function()
    client:request("http://localhost:8075/api/users", {
      options = { method = "GET" },
      success = function(response)
        print("✅ Get users:", response.status, response.data)
      end,
      error = function(err)
        print("❌ Get users error:", err)
      end
    })
  end, 300)
  
  -- Test 3: Create a new user
  setTimeout(function()
    local new_user_data = json.encode({
      name = "Charlie",
      email = "charlie@example.com"
    })
    
    client:request("http://localhost:8075/api/users", {
      options = { 
        method = "POST",
        data = new_user_data,
        headers = {
          ["Content-Type"] = "application/json"
        }
      },
      success = function(response)
        print("✅ Create user:", response.status, response.data)
      end,
      error = function(err)
        print("❌ Create user error:", err)
      end
    })
  end, 600)
  
  -- Test 4: Get specific user
  setTimeout(function()
    client:request("http://localhost:8075/api/users/1", {
      options = { method = "GET" },
      success = function(response)
        print("✅ Get user 1:", response.status, response.data)
      end,
      error = function(err)
        print("❌ Get user 1 error:", err)
      end
    })
  end, 900)
  
  -- Test 5: Get non-existent user (should 404)
  setTimeout(function()
    client:request("http://localhost:8075/api/users/999", {
      options = { method = "GET" },
      success = function(response)
        print("✅ Get user 999:", response.status, response.data)
      end,
      error = function(err)
        print("❌ Get user 999 error:", err)
      end
    })
  end, 1200)
  
  -- Test 6: Invalid endpoint (should 404)
  setTimeout(function()
    client:request("http://localhost:8075/api/invalid", {
      options = { method = "GET" },
      success = function(response)
        print("✅ Invalid endpoint:", response.status, response.data)
      end,
      error = function(err)
        print("❌ Invalid endpoint error:", err)
      end
    })
  end, 1500)
  
  -- Stop server after all tests
  setTimeout(function()
    print("\n🔌 Stopping HTTP server...")
    http_server:stop()
  end, 2000)
  
end, 1000)  -- Wait 1 second for server to start
