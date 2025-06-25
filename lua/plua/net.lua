
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
          options.error(response.code or 0)
        end
      else
        -- Call success callback if provided
        if options.success then
          options.success(response)
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
    _PY.tcp_connect(ip, port, function(socket, err)
      if err then
        if opts.error then opts.error(err) end
        return
      end
      self.socket = socket
      if opts.success then opts.success() end
    end)
  end

  function self:read(opts)
    local opts = opts or {}
    if not self.socket then
      if opts.error then opts.error("Not connected") end
      return
    end
    _PY.tcp_read(self.socket, function(data, err)
      if err then
        if opts.error then opts.error(err) end
        return
      end
      if opts.success then opts.success(data) end
    end)
  end

  function self:readUntil(delimiter, opts)
    local opts = opts or {}
    if not self.socket then
      if opts.error then opts.error("Not connected") end
      return
    end
    _PY.tcp_read_until(self.socket, delimiter, function(data, err)
      if err then
        if opts.error then opts.error(err) end
        return
      end
      if opts.success then opts.success(data) end
    end)
  end

  function self:write(data, opts)
    local opts = opts or {}
    if not self.socket then
      if opts.error then opts.error("Not connected") end
      return
    end
    _PY.tcp_write(self.socket, data, function(err)
      if err then
        if opts.error then opts.error(err) end
        return
      end
      if opts.success then opts.success() end
    end)
  end

  function self:close()
    if self.socket then
      _PY.tcp_close(self.socket)
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
      if opts.error then opts.error("Not connected") end
      return
    end
    _PY.udp_send_to(self.socket, data, ip, port, function(err)
      if err then
        if opts.error then opts.error(err) end
        return
      end
      if opts.success then opts.success() end
    end)
  end

  function self:receive(opts)
    local opts = opts or {}
    if not self.socket then
      if opts.error then opts.error("Not connected") end
      return
    end
    _PY.udp_receive(self.socket, function(data, ip, port, err)
      if err then
        if opts.error then opts.error(err) end
        return
      end
      if opts.success then opts.success(data, ip, port) end
    end)
  end

  function self:close()
    if self.socket then
      _PY.udp_close(self.socket)
      self.socket = nil
    end
  end
end

return net