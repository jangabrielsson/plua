-- Cleaned up version showing consistent function callback style

function net.TCPSocket(opts)
  local opts = opts or {}
  local self = { opts = opts, socket = nil }
  setmetatable(self, { __tostring = function(_) return "TCPSocket object: "..tostring(self.socket) end })

  -- Connect to a TCP server
  -- callback(success, error_message)
  function self:connect(ip, port, callback)
    local result_callback = function(result)
      if callback then
        if result.success then
          self.socket = result.conn_id
          callback(true, nil)
        else
          callback(false, result.message)
        end
      end
    end
    
    local callback_id = _PY.registerCallback(result_callback)
    _PY.tcp_connect(ip, port, callback_id)
  end

  -- Write data to the socket
  -- callback(success)
  function self:write(data, callback)
    if not self.socket then
      if callback then callback(false) end
      return
    end
    
    local result_callback = function(result)
      if callback then
        callback(result.success)
      end
    end
    
    local callback_id = _PY.registerCallback(result_callback)
    _PY.tcp_write(self.socket, data, callback_id)
  end

  -- Read data from the socket
  -- callback(data, error_message) - data is nil on error
  function self:read(callback)
    if not self.socket then
      if callback then callback(nil, "Not connected") end
      return
    end
    
    local result_callback = function(result)
      if callback then
        if result.success then
          callback(result.data, nil)
        else
          callback(nil, result.message)
        end
      end
    end
    
    local callback_id = _PY.registerCallback(result_callback)
    _PY.tcp_read(self.socket, 1024, callback_id)
  end

  -- Alias for read with simpler name
  function self:receive(callback)
    self:read(callback)
  end

  function self:close()
    if self.socket then
      local callback = function(result)
        if not result.success then
          print("Error closing TCP connection: " .. tostring(result.message))
        end
      end
      
      local callback_id = _PY.registerCallback(callback)
      _PY.tcp_close(self.socket, callback_id)
      self.socket = nil
    end
  end

  return self
end
