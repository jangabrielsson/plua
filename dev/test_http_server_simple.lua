-- Simple HTTP Server test

local server = net.HTTPServer()

-- Start server that handles different endpoints
server:start('localhost', 8090, function(method, path, body)
  print("Request:", method, path, "Body:", body or "(empty)")
  
  if path == "/api/hello" then
    return '{"message": "Hello World!"}', 200
  elseif path == "/api/echo" and method == "POST" then
    return '{"echo": "' .. (body or "") .. '"}', 200
  elseif path == "/api/status" then
    return '{"status": "OK", "server": "PLua HTTP Server"}', 200
  else
    return '{"error": "Not found"}', 404
  end
end)

print("HTTP Server started on localhost:8090")
print("Try these endpoints:")
print("  GET  http://localhost:8090/api/hello")
print("  GET  http://localhost:8090/api/status") 
print("  POST http://localhost:8090/api/echo")
print("  GET  http://localhost:8090/invalid (should return 404)")

-- Test with HTTP client
setTimeout(function()
  local client = net.HTTPClient()
  
  -- Test GET /api/hello
  client:request("http://localhost:8090/api/hello", {
    options = { method = "GET" },
    success = function(response)
      print("GET /api/hello ->", response.status, response.data)
    end,
    error = function(err)
      print("Error:", err)
    end
  })
  
  -- Test POST /api/echo
  setTimeout(function()
    client:request("http://localhost:8090/api/echo", {
      options = { 
        method = "POST",
        data = "Hello from client!"
      },
      success = function(response)
        print("POST /api/echo ->", response.status, response.data)
      end,
      error = function(err)
        print("Error:", err)
      end
    })
  end, 500)
  
  -- Test 404
  setTimeout(function()
    client:request("http://localhost:8090/invalid", {
      options = { method = "GET" },
      success = function(response)
        print("GET /invalid ->", response.status, response.data)
      end,
      error = function(err)
        print("Error:", err)
      end
    })
  end, 1000)
  
  -- Stop server after tests
  setTimeout(function()
    print("Stopping server...")
    server:stop()
  end, 2000)
  
end, 1000)
