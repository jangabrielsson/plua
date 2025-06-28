local fmt = string.format
local _DEBUG = false
_PY = _PY or {}

-- Use synchronous functions directly for MobDebug compatibility
local tcp_connect_sync = _PY.tcp_connect_sync
local tcp_write_sync = _PY.tcp_write_sync
local tcp_read_sync = _PY.tcp_read_sync
local tcp_close_sync = _PY.tcp_close_sync
local tcp_set_timeout_sync = _PY.tcp_set_timeout_sync

local function debug(...) if _DEBUG then print(...) end end

local socket = {}

local function tcp()
  local self = { conn_id = nil }
  
  function self:connect(host, port)
    debug("Connecting to " .. host .. " on port " .. port)
    
    local success, conn_id, message = tcp_connect_sync(host, tonumber(port))
    
    if success then 
      debug("Connected") 
      self.conn_id = conn_id
      return conn_id, message 
    else 
      debug("Failed to connect: " .. message) 
      return nil, message 
    end
  end
  
  function self:settimeout(timeout)
    if self.conn_id then
      debug("Setting timeout to " .. tostring(timeout))
      
      local success, message = tcp_set_timeout_sync(self.conn_id, timeout)
      
      if success then 
        debug("Timeout set:", message) 
      else 
        debug("Failed to set timeout: " .. message) 
      end
    else
      debug("No connection to set timeout")
    end
  end
  
  function self:send(data, i, j)
    if self.conn_id then
      debug("Sending data: " .. data, i, j)
      
      local success, len, message = tcp_write_sync(self.conn_id, data)
      
      if success then 
        debug("Sent", len) 
        return len, nil 
      else 
        debug("Failed to send: " .. message) 
        return nil, message 
      end
    else
      debug("No connection to send data")
      return nil, "No connection to send data"
    end
  end
  
  function self:receive(pattern_or_n, m)
    if self.conn_id then
      debug("Receiving data", pattern_or_n, m)
      
      local success, data, message = tcp_read_sync(self.conn_id, pattern_or_n)
      
      if success then 
        data = tostring(data)
        debug("Received: " .. '"' .. data .. '"', message) 
        return data, #data
      else 
        debug("Failed to receive: " .. tostring(message)) 
        return nil, message
      end
    else
      debug("No connection to receive data")
      return nil, "No connection to receive data"
    end
  end
  
  function self:close() 
    if self.conn_id then
      debug("Closing connection")
      
      local success, message = tcp_close_sync(self.conn_id)
      
      if success then 
        debug("Closed") 
      else 
        debug("Failed to close: " .. message) 
      end
      
      self.conn_id = nil
    else
      debug("No connection to close")
    end
  end
  
  setmetatable(self, { __tostring = function() return fmt("[tcp conn_id=%s]", self.conn_id or -1) end })
  return self
end

function socket.tcp()
  debug("Requesting tcp socket")
  return tcp()
end

return socket