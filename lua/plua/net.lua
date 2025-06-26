local net = {}
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
      body = options.options and options.options.data or nil
    }
    
    -- Create a callback function that will handle the response
    local callback = function(response)
      if response.error then
        -- Call error callback if provided
        if options.error then
          local success, err = pcall(options.error, response.code or 0)
          if not success then
            print("Error in HTTP error callback: " .. tostring(err))
          end
        end
      else
        -- Call success callback if provided
        if options.success then
          local success, err = pcall(options.success, response)
          if not success then
            print("Error in HTTP success callback: " .. tostring(err))
          end
        end
      end
    end
    
    -- Make the async HTTP request
    _PY.http_request_async(request_table, callback)
  end
  return self
end

-- opts = { success = function(data) end, error = function(err) end }
function net.TCPSocket(opts)
  local opts = opts or {}
  local self = { opts = opts, socket = nil }

  function self:connect(ip, port, opts)
    local opts = opts or {}
    _PY.tcp_connect(ip, port, function(success, conn_id, message)
      if not success then
        if opts.error then
          local success, err_msg = pcall(opts.error, message)
          if not success then
            print("Error in TCP connect error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      self.socket = conn_id
      if opts.success then
        local success, err_msg = pcall(opts.success)
        if not success then
          print("Error in TCP connect success callback: " .. tostring(err_msg))
        end
      end
    end)
  end

  function self:read(opts)
    local opts = opts or {}
    if not self.socket then
      if opts.error then
        local success, err_msg = pcall(opts.error, "Not connected")
        if not success then
          print("Error in TCP read error callback: " .. tostring(err_msg))
        end
      end
      return
    end
    _PY.tcp_read(self.socket, 1024, function(success, data, message)
      if not success then
        if opts.error then
          local success, err_msg = pcall(opts.error, message)
          if not success then
            print("Error in TCP read error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      if opts.success then
        local success, err_msg = pcall(opts.success, data)
        if not success then
          print("Error in TCP read success callback: " .. tostring(err_msg))
        end
      end
    end)
  end

  function self:readUntil(delimiter, opts)
    local opts = opts or {}
    if not self.socket then
      if opts.error then
        local success, err_msg = pcall(opts.error, "Not connected")
        if not success then
          print("Error in TCP readUntil error callback: " .. tostring(err_msg))
        end
      end
      return
    end
    _PY.tcp_read_until(self.socket, delimiter, 8192, function(success, data, message)
      if not success then
        if opts.error then
          local success, err_msg = pcall(opts.error, message)
          if not success then
            print("Error in TCP readUntil error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      if opts.success then
        local success, err_msg = pcall(opts.success, data)
        if not success then
          print("Error in TCP readUntil success callback: " .. tostring(err_msg))
        end
      end
    end)
  end

  function self:write(data, opts)
    local opts = opts or {}
    if not self.socket then
      if opts.error then
        local success, err_msg = pcall(opts.error, "Not connected")
        if not success then
          print("Error in TCP write error callback: " .. tostring(err_msg))
        end
      end
      return
    end
    _PY.tcp_write(self.socket, data, function(success, bytes_written, message)
      if not success then
        if opts.error then
          local success, err_msg = pcall(opts.error, message)
          if not success then
            print("Error in TCP write error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      if opts.success then
        local success, err_msg = pcall(opts.success)
        if not success then
          print("Error in TCP write success callback: " .. tostring(err_msg))
        end
      end
    end)
  end

  function self:close()
    if self.socket then
      _PY.tcp_close(self.socket, function(success, message)
        if not success then
          print("Error closing TCP connection: " .. tostring(message))
        end
      end)
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
    _PY.udp_send_to(self.socket, data, ip, port, function(err)
      if err then
        if opts.error then
          local success, err_msg = pcall(opts.error, err)
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
    end)
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
    _PY.udp_receive(self.socket, function(data, ip, port, err)
      if err then
        if opts.error then
          local success, err_msg = pcall(opts.error, err)
          if not success then
            print("Error in UDP receive error callback: " .. tostring(err_msg))
          end
        end
        return
      end
      if opts.success then
        local success, err_msg = pcall(opts.success, data, ip, port)
        if not success then
          print("Error in UDP receive success callback: " .. tostring(err_msg))
        end
      end
    end)
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

-- WebSocket client implementations following Fibaro HC3 API
function net.WebSocketClient(options)
  local options = options or {}
  local self = {}
  self.conn_id = _PY.websocket_client_create(false)  -- non-TLS
  
  function self:addEventListener(eventName, callback)
    local success, err = pcall(_PY.websocket_add_event_listener, self.conn_id, eventName, callback)
    if not success then
      print("Error adding WebSocket event listener: " .. tostring(err))
    end
  end
  
  function self:connect(url, headers)
    local success, err = pcall(_PY.websocket_connect, self.conn_id, url, headers)
    if not success then
      print("Error connecting WebSocket: " .. tostring(err))
    end
  end
  
  function self:send(data)
    local success, err = pcall(_PY.websocket_send, self.conn_id, data)
    if not success then
      print("Error sending WebSocket data: " .. tostring(err))
    end
    return success
  end
  
  function self:isOpen()
    local success, result = pcall(_PY.websocket_is_open, self.conn_id)
    if not success then
      print("Error checking WebSocket status: " .. tostring(result))
      return false
    end
    return result
  end
  
  function self:close()
    local success, err = pcall(_PY.websocket_close, self.conn_id)
    if not success then
      print("Error closing WebSocket: " .. tostring(err))
    end
  end
  
  local pstr = "WebSocketClient object: "..tostring(self):match("%s(.*)")
  setmetatable(self,{__tostring = function(_) return pstr end})
  return self
end

function net.WebSocketClientTls(options)
  local options = options or {}
  local self = {}
  self.conn_id = _PY.websocket_client_create(true)  -- TLS
  
  function self:addEventListener(eventName, callback)
    local success, err = pcall(_PY.websocket_add_event_listener, self.conn_id, eventName, callback)
    if not success then
      print("Error adding WebSocket TLS event listener: " .. tostring(err))
    end
  end
  
  function self:connect(url, headers)
    local success, err = pcall(_PY.websocket_connect, self.conn_id, url, headers)
    if not success then
      print("Error connecting WebSocket TLS: " .. tostring(err))
    end
  end
  
  function self:send(data)
    local success, err = pcall(_PY.websocket_send, self.conn_id, data)
    if not success then
      print("Error sending WebSocket TLS data: " .. tostring(err))
    end
    return success
  end
  
  function self:isOpen()
    local success, result = pcall(_PY.websocket_is_open, self.conn_id)
    if not success then
      print("Error checking WebSocket TLS status: " .. tostring(result))
      return false
    end
    return result
  end
  
  function self:close()
    local success, err = pcall(_PY.websocket_close, self.conn_id)
    if not success then
      print("Error closing WebSocket TLS: " .. tostring(err))
    end
  end
  
  local pstr = "WebSocketClientTls object: "..tostring(self):match("%s(.*)")
  setmetatable(self,{__tostring = function(_) return pstr end})
  return self
end

return net