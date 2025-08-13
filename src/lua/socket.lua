local fmt = string.format

 -- Enable debug to trace MobDebug communication from VS Code -- Enable debug to trace MobDebug communication from VS Code
local _DEBUG = false
_PY = _PY or {}

-- Use synchronous functions directly for MobDebug compatibility
local tcp_connect_sync = _PY.tcp_connect_sync
local tcp_write_sync = _PY.tcp_write_sync
local tcp_read_sync = _PY.tcp_read_sync
local tcp_close_sync = _PY.tcp_close_sync
local tcp_set_timeout_sync = _PY.tcp_set_timeout_sync
local http_call_sync = _PY.http_call_sync

local function debug(...) 
  if _DEBUG then 
    local timestamp = os.date("%H:%M:%S")
    print("[SOCKET " .. timestamp .. "]", ...) 
  end 
end

-- Helper function to safely convert any error to string
local function safe_tostring(value)
    if type(value) == "string" then
        return value
    elseif type(value) == "userdata" then
        -- Handle Python exception objects that might slip through
        return "Python error: " .. tostring(value)
    else
        return tostring(value)
    end
end

local socket = {}

local function tcp()
  local self = { 
    conn_id = nil,
    _timeout = nil  -- Store timeout for pre-connect settimeout calls
  }
  
  function self:connect(host, port)
    debug("*** CONNECT START ***")
    debug("Connecting to " .. host .. " on port " .. port)
    
    local success, conn_id, message = tcp_connect_sync(host, tonumber(port))
    
    if success then 
      debug("*** CONNECT SUCCESS ***") 
      debug("Connection ID:", conn_id)
      self.conn_id = conn_id
      
      -- Apply stored timeout if we had a pre-connect settimeout call
      if self._timeout ~= nil then
        debug("Applying stored timeout:", self._timeout)
        tcp_set_timeout_sync(self.conn_id, self._timeout)
        self._timeout = nil  -- Clear stored timeout
      end
      
      debug("*** CONNECT RETURNING 1 ***")
      return 1  -- LuaSocket returns 1 on successful connection
    else 
      local error_msg = safe_tostring(message)
      debug("*** CONNECT FAILED ***")
      debug("Error:", error_msg) 
      return nil, error_msg 
    end
  end
  
  function self:settimeout(timeout)
    debug("Setting timeout to", tostring(timeout))
    
    if self.conn_id then
      local success, message = tcp_set_timeout_sync(self.conn_id, timeout)
      
      if success then 
        debug("Timeout set:", message) 
      else 
        local error_msg = safe_tostring(message)
        debug("Failed to set timeout:", error_msg) 
      end
    else
      -- Store timeout for use during connect (LuaSocket compatibility)
      debug("Storing timeout for later use:", timeout)
      self._timeout = timeout
    end
  end
  
  function self:send(data, i, j)
    if self.conn_id then
      debug("Sending data:", #data, "bytes")
      
      local success, len, message = tcp_write_sync(self.conn_id, data)
      
      if success then 
        debug("Sent", len, "bytes") 
        return len, nil 
      else 
        local error_msg = safe_tostring(message)
        debug("Failed to send:", error_msg) 
        return nil, error_msg 
      end
    else
      debug("No connection to send data")
      return nil, "No connection to send data"
    end
  end
  
  function self:receive(pattern_or_n, m)
    if self.conn_id then
      debug("*** RECEIVE START ***")
      debug("Pattern:", pattern_or_n, "Optional:", m)
      
      local success, data, partial = tcp_read_sync(self.conn_id, pattern_or_n)
      
      if success then 
        data = tostring(data)
        debug("*** RECEIVE SUCCESS ***")
        debug("Data length:", #data)
        debug("Data content:", '"' .. data .. '"') 
        return data  -- Return only data on success (LuaSocket compatible)
      else 
        debug("*** RECEIVE FAILED/TIMEOUT ***")
        -- Handle partial data and errors like LuaSocket
        if partial then
          debug("Partial data length:", #partial)
          debug("Partial content:", '"' .. partial .. '"')
          return nil, "timeout", partial  -- LuaSocket format: nil, error, partial
        else
          debug("No partial data - connection closed or other error")
          return nil, "closed"  -- Connection closed or other error
        end
      end
    else
      debug("*** RECEIVE - NO CONNECTION ***")
      return nil, "closed"
    end
  end
  
  function self:close() 
    if self.conn_id then
      debug("Closing connection")
      
      local success, message = tcp_close_sync(self.conn_id)
      
      if success then 
        debug("Closed") 
      else 
        local error_msg = safe_tostring(message)
        debug("Failed to close: " .. error_msg) 
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

-- Synchronous HTTP call function
socket.http_call = function(method, url, headers, payload)
  debug("Making HTTP call:", method, url)
  
  local success, status_code, response_body, error_message = http_call_sync(method, url, headers, payload)
  
  if success then
    debug("HTTP call successful:", status_code)
    return {
      success = true,
      status_code = status_code,
      body = response_body,
      error = nil
    }
  else
    debug("HTTP call failed:", error_message)
    return {
      success = false,
      status_code = status_code,
      body = response_body,
      error = error_message
    }
  end
end

return socket