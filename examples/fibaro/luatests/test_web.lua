-- TCP Server and Client Demo
-- Demonstrates PLua Python TCP server extension and Lua client with bidirectional communication
--%%name:Web test

FIBTEST:setup{name='Web test',tests=7 }

--%%name:HTTPServer

local server = net.HTTPServer()

function QuickApp:onInit()
  self:debug(self.name, self.id)

  -- Start the HTTP server
  server:start('localhost', 8072, function(method, path, body, headers)
    local response = "Echo " .. tostring(body)
    self:debug("[Server] " .. method .. " " .. path .. " -> " .. response:gsub("\n", "\\n"))
    self:debug("[Server headers] " .. json.encode(headers))
    return response, 200, {["X-Custom-Header"] = "custom_value"}
  end)

  -- Give the server a moment to start, then begin client requests
  setTimeout(function()
    local http = net.HTTPClient()

    local messages = {
      "Hello from HTTP client!",
      "How are you?", 
      "I'm fine, thank you!",
      "What's your name?",
      "My name is John Doe.",
      "What's your favorite color?",
      "My favorite color is blue"
    }

    local function sendMessages(n)
      if n <= #messages then
        http:request("http://localhost:8072/api/test", {
          options = {
            method = "POST",
            data = messages[n]
          },
          success = function(response)
            self:debug("[Client] Received:", response.data:gsub("\n", "\\n"))
            FIBTEST:assert(response.status == 200, "Expected status 200, got " .. response.status)
            setTimeout(function() sendMessages(n + 1) end, 500)
          end,
          error = function(err)
            self:debug("[Client] Error:", err)
          end
        })
      else
        self:debug("[Client] All messages sent")
        setTimeout(function()
          self:debug("Stopping server...")
          server:stop()
        end, 1000)
      end
    end

    self:debug("Starting HTTP client test...")
    sendMessages(1)
  end, 1000)  -- Wait 1 second for server to start
end