net = {}
_PY = _PY or {}

-- Creates a new HTTP client object.
-- @return A table representing the HTTP client.
function net.HTTPClient()
  local self = {}
  -- url is string
  -- options = { options = { method = "get", headers = {}, data = "...", timeout = 10000 }, success = function(response) end, error = function(status) end }
  function self:request(url, options)
    -- Create the request table for http_request_async
    local request_table = {
      url = url,
      method = options.options and options.options.method or "GET",
      headers = options.options and options.options.headers or {},
      body = options.options and options.options.data or nil,
      timeout = options.options and options.options.timeout or 30
    }
    
    -- Create a callback function that will handle the response
    local callback = function(response)
      if response.error then
        -- Call error callback if provided
        if options.error then
          -- For timeout errors, pass "timeout" string. For other errors, pass the error message or status code
          local error_param = response.error:lower() == "timeout" and "timeout" or (response.error or response.code or 0)
          local success, err = pcall(options.error, error_param)
          if not success then
            print("Error in HTTP error callback: " .. tostring(err))
          end
        end
      else
        -- Call success callback if provided
        if options.success then
          local res = { status = response.code, data = response.body }
          local success, err = pcall(options.success, res)
          if not success then
            print("Error in HTTP success callback: " .. tostring(err))
          end
        end
      end
    end
    
    -- Make the async HTTP request
    local callback_id = _PY.registerCallback(callback)
    _PY.http_request_async(request_table, callback_id)
  end
  return self
end

-- opts = { timeout = 10000 } -- timeout in milliseconds
function net.TCPSocket(opts)
  local opts = opts or {}
  local self = { 
    opts = opts, 
    socket = nil,
    timeout = opts.timeout or 10000  -- Default 10 second timeout
  }
  setmetatable(self, { __tostring = function(_) return "TCPSocket object: "..tostring(self.socket) end })

  function self:_wrap(conn_id) self.socket = conn_id return self end
  
  function self:connect(ip, port, callbacks)
    local callbacks = callbacks or {}
    
    -- Create a callback function that will handle the connection result
    local result_callback = function(result)
      if not result.success then
        if callbacks.error then
          local success, err_msg = pcall(callbacks.error, result.message)
          if not success then
            print("Error in TCP connect error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      self.socket = result.conn_id
      if callbacks.success then
        local success, err_msg = pcall(callbacks.success)
        if not success then
          print("Error in TCP connect success callback: " .. tostring(err_msg))
        end
      end
    end
    
    -- Register the callback and make the connection
    local callback_id = _PY.registerCallback(result_callback)
    _PY.tcp_connect(ip, port, callback_id)
  end

  function self:read(callbacks)
    local callbacks = callbacks or {}
    if not self.socket then
      if callbacks.error then
        local success, err_msg = pcall(callbacks.error, "Not connected")
        if not success then
          print("Error in TCP read error callback: " .. tostring(err_msg))
        end
      end
      return
    end
    
    -- Create a callback function that will handle the read result
    local result_callback = function(result)
      if not result.success then
        if callbacks.error then
          local success, err_msg = pcall(callbacks.error, result.message)
          if not success then
            print("Error in TCP read error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      if callbacks.success then
        local success, err_msg = pcall(callbacks.success, result.data)
        if not success then
          print("Error in TCP read success callback: " .. tostring(err_msg))
        end
      end
    end
    
    -- Register the callback and make the read
    local callback_id = _PY.registerCallback(result_callback)
    _PY.tcp_read(self.socket, 1024, callback_id)
  end

  function self:readUntil(delimiter, callbacks)
    local callbacks = callbacks or {}
    if not self.socket then
      if callbacks.error then
        local success, err_msg = pcall(callbacks.error, "Not connected")
        if not success then
          print("Error in TCP readUntil error callback: " .. tostring(err_msg))
        end
      end
      return
    end
    
    -- Create a callback function that will handle the read result
    local result_callback = function(result)
      if not result.success then
        if callbacks.error then
          local success, err_msg = pcall(callbacks.error, result.message)
          if not success then
            print("Error in TCP readUntil error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      if callbacks.success then
        local success, err_msg = pcall(callbacks.success, result.data)
        if not success then
          print("Error in TCP readUntil success callback: " .. tostring(err_msg))
        end
      end
    end
    
    -- Register the callback and make the read
    local callback_id = _PY.registerCallback(result_callback)
    _PY.tcp_read_until(self.socket, delimiter, 8192, callback_id)
  end

  -- Fibaro API uses 'send' method name
  function self:send(data, callbacks)
    local callbacks = callbacks or {}
    if not self.socket then
      if callbacks.error then
        local success, err_msg = pcall(callbacks.error, "Not connected")
        if not success then
          print("Error in TCP send error callback: " .. tostring(err_msg))
        end
      end
      return
    end
    
    -- Create a callback function that will handle the write result
    local result_callback = function(result)
      if not result.success then
        if callbacks.error then
          local success, err_msg = pcall(callbacks.error, result.message)
          if not success then
            print("Error in TCP send error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      if callbacks.success then
        local success, err_msg = pcall(callbacks.success)
        if not success then
          print("Error in TCP send success callback: " .. tostring(err_msg))
        end
      end
    end
    
    -- Register the callback and make the write
    local callback_id = _PY.registerCallback(result_callback)
    _PY.tcp_write(self.socket, data, callback_id)
  end

  -- Keep write method as alias for backward compatibility
  function self:write(data, callbacks)
    return self:send(data, callbacks)
  end

  function self:close()
    if self.socket then
      -- Create a callback function that will handle the close result
      local callback = function(result)
        if not result.success then
          print("Error closing TCP connection: " .. tostring(result.message))
        end
      end
      
      -- Register the callback and close the connection
      local callback_id = _PY.registerCallback(callback)
      _PY.tcp_close(self.socket, callback_id)
      self.socket = nil
    end
  end

  local pstr = "TCPSocket object: "..tostring(self):match("%s(.*)")
  setmetatable(self,{__tostring = function(_) return pstr end})
  return self
end

-- net.UDPSocket(opts)
-- UDPSocket:sendTo(data, ip, port, callbacks)
-- UDPSocket:receive(callbacks)
-- UDPSocket:close()
-- opts = { success = function(data) end, error = function(err) end }
function net.UDPSocket(opts)
  local opts = opts or {}
  local self = { opts = opts, socket = nil }

  -- Create UDP socket automatically when constructor is called
  local function createSocket()
    local callback = function(result)
      if result.success then
        self.socket = result.socket_id
      else
        print("Error creating UDP socket: " .. tostring(result.message))
      end
    end
    local callback_id = _PY.registerCallback(callback)
    _PY.udp_create_socket(callback_id)
  end
  
  -- Create socket immediately
  createSocket()

  function self:sendTo(data, ip, port, opts)
    local opts = opts or {}
    if not self.socket then
      if opts.error then
        local success, err_msg = pcall(opts.error, "Not connected")
        if not success then
          print("Error in UDP sendTo error callback: " .. tostring(err_msg))
        end
      end
      return
    end
    
    -- Create a callback function that will handle the send result
    local callback = function(result)
      if result.error then
        if opts.error then
          local success, err_msg = pcall(opts.error, result.error)
          if not success then
            print("Error in UDP sendTo error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      if opts.success then
        local success, err_msg = pcall(opts.success)
        if not success then
          print("Error in UDP sendTo success callback: " .. tostring(err_msg))
        end
      end
    end
    
    -- Register the callback and send the data
    local callback_id = _PY.registerCallback(callback)
    _PY.udp_send_to(self.socket, data, ip, port, callback_id)
  end

  function self:receive(opts)
    local opts = opts or {}
    if not self.socket then
      if opts.error then
        local success, err_msg = pcall(opts.error, "Not connected")
        if not success then
          print("Error in UDP receive error callback: " .. tostring(err_msg))
        end
      end
      return
    end
    
    -- Create a callback function that will handle the receive result
    local callback = function(result)
      if result.error then
        if opts.error then
          local success, err_msg = pcall(opts.error, result.error)
          if not success then
            print("Error in UDP receive error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      if opts.success then
        local success, err_msg = pcall(opts.success, result.data, result.ip, result.port)
        if not success then
          print("Error in UDP receive success callback: " .. tostring(err_msg))
        end
      end
    end
    
    -- Register the callback and start receiving
    local callback_id = _PY.registerCallback(callback)
    _PY.udp_receive(self.socket, callback_id)
  end

  -- Convenience method that delegates to sendTo for compatibility
  function self:send(host, port, data, opts)
    return self:sendTo(data, host, port, opts)
  end

  function self:close()
    if self.socket then
      _PY.udp_close(self.socket)
      self.socket = nil
    end
  end

  local pstr = "UDPSocket object: "..tostring(self):match("%s(.*)")
  setmetatable(self,{__tostring = function(_) return pstr end})
  return self
end


function net.TCPServer()
  local self = {}
  self.server = _PY.tcp_server_create()

  -- Start server on host:port -- default to localhost
  -- Callback called when a client connects
  -- callback = function(client_tcp_socket, client_ip, client_port)
  function self:start(host, port, callback)
    local host = host or "localhost"
    
    -- Create a callback function that will handle client connections
    local connection_callback = function(result)
      if not result.success then
        print("Error accepting client connection:", result.error or "Unknown error")
        return
      end
      
      -- Create a TCPSocket object for the connected client
      local client_socket = net.TCPSocket()
      client_socket.socket = result.conn_id  -- Set the connection ID directly
      
      -- Call the user's callback with the client socket and connection info
      if callback then
        local success, err = pcall(callback, client_socket, result.client_ip, result.client_port)
        if not success then
          print("Error in TCP server client callback: " .. tostring(err))
        end
      end
    end
    
    -- Register the connection callback and start the server
    local callback_id = _PY.registerCallback(connection_callback)
    _PY.tcp_server_start(self.server, host, port, callback_id)
  end
  
  function self:stop()
    if self.server then
      -- Create a callback function that will handle the stop result
      local callback = function(result)
        if not result.success then
          print("Error stopping TCP server: " .. tostring(result.message))
        else
          print("TCP Server stopped successfully")
        end
      end
      
      -- Register the callback and stop the server
      local callback_id = _PY.registerCallback(callback)
      _PY.tcp_server_stop(self.server, callback_id)
      self.server = nil
    end
  end
  
  return self
end

function net.HTTPServer()
  local self = {}
  self.server = _PY.http_server_create()

  -- Start server on host:port -- default to localhost
  -- Callback called when an HTTP request arrives
  -- callback = function(method, path, payload) return data, status_code end
  -- The callback is responsible for encoding data to json if needed using json.encode()
  function self:start(host, port, callback)
    local host = host or "localhost"
    
    -- Create a callback function that will handle HTTP requests
    local request_callback = function(request)
      local data, status_code = nil, 404
      
      -- Call the user's callback with method, path, and payload
      if callback then
        local success, result_data, result_status = pcall(callback, request.method, request.path, request.body)
        if success then
          data = result_data or '{"error": "No data returned"}'
          status_code = result_status or 200
        else
          print("Error in HTTP server request callback: " .. tostring(result_data))
          -- Send error response
          data = '{"error": "Internal server error"}'
          if json and json.encode then
            data = json.encode({error = "Internal server error"})
          end
          status_code = 500
        end
      else
        -- No callback provided, send 404
        data = '{"error": "Not found"}'
        if json and json.encode then
          data = json.encode({error = "Not found"})
        end
        status_code = 404
      end
      
      -- Send the response back via Python
      _PY.http_server_respond(request.request_id, data, status_code, "application/json")
    end
    
    -- Register the request callback and start the server (persistent callback for multiple requests)
    local callback_id = _PY.registerCallback(request_callback, true)  -- true = persistent
    _PY.http_server_start(self.server, host, port, callback_id)
  end
  
  function self:stop()
    if self.server then
      -- Create a callback function that will handle the stop result
      local callback = function(result)
        if not result.success then
          print("Error stopping HTTP server: " .. tostring(result.message))
        else
          print("HTTP Server stopped successfully")
        end
      end
      
      -- Register the callback and stop the server
      local callback_id = _PY.registerCallback(callback)
      _PY.http_server_stop(self.server, callback_id)
      self.server = nil
    end
  end
  
  return self
end

-- Return the net module for require()
return net