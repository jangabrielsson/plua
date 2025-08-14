-- Test HTTP server with custom headers

-- Simple JSON encode for testing
local function json_encode(obj)
  if type(obj) == "table" then
    local result = "{"
    local first = true
    for k, v in pairs(obj) do
      if not first then result = result .. "," end
      result = result .. '"' .. tostring(k) .. '":"' .. tostring(v) .. '"'
      first = false
    end
    return result .. "}"
  else
    return '"' .. tostring(obj) .. '"'
  end
end

local server = net.HTTPServer()

server:start('localhost', 8073, function(method, path, body, headers)
  print("Request headers:", json_encode(headers))
  
  -- Return custom headers
  local response_headers = {
    ["X-Custom-Header"] = "test-value",
    ["X-Server"] = "PLua-Server",
    ["X-Time"] = tostring(os.time())
  }
  
  print("Returning headers:", json_encode(response_headers))
  return '{"message": "Hello with headers!"}', 200, response_headers
end)

print("HTTP Server started on localhost:8073")

-- Test with client
setTimeout(function()
  local client = net.HTTPClient()
  
  client:request("http://localhost:8073/test", {
    options = { 
      method = "POST",
      data = "test data",
      headers = {
        ["X-Client-Header"] = "client-value"
      }
    },
    success = function(response)
      print("Response status:", response.status)
      print("Response data:", response.data)
      print("Response object keys:")
      for k, v in pairs(response) do
        print("  " .. tostring(k) .. ": " .. type(v))
      end
      
      -- Check for our custom headers
      if response.headers then
        print("X-Custom-Header:", response.headers["X-Custom-Header"] or response.headers["x-custom-header"])
        print("X-Server:", response.headers["X-Server"] or response.headers["x-server"])
        print("X-Time:", response.headers["X-Time"] or response.headers["x-time"])
      end
    end,
    error = function(err)
      print("Error:", err)
    end
  })
  
  setTimeout(function()
    server:stop()
  end, 2000)
  
end, 1000)
