local net = {}
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
          local res = { status = response.code, data = response.body }
          local success, err = pcall(options.success, res)
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
  setmetatable(self, { __tostring = function(_) return "TCPSocket object: "..tostring(self.socket) end })

  function self:_wrap(conn_id) self.socket = conn_id return self end
  
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

-- MQTT client implementation following Fibaro HC3 API
function net.MQTTClient(options)
  local options = options or {}
  local self = {}
  self.conn_id = _PY.mqtt_client_create()  -- Remove the false parameter
  
  function self:addEventListener(eventName, callback)
    local success, err = pcall(_PY.mqtt_client_add_event_listener, self.conn_id, eventName, callback)
    if not success then
      print("Error adding MQTT event listener: " .. tostring(err))
    end
  end
  
  function self:connect(uri, options)
    local success, err = pcall(_PY.mqtt_client_connect, self.conn_id, uri, options)
    if not success then
      print("Error connecting MQTT: " .. tostring(err))
    end
  end
  
  function self:disconnect(options)
    local success, err = pcall(_PY.mqtt_client_disconnect, self.conn_id, options)
    if not success then
      print("Error disconnecting MQTT: " .. tostring(err))
    end
  end
  
  function self:subscribe(topic_or_topics, options)
    local success, result = pcall(_PY.mqtt_client_subscribe, self.conn_id, topic_or_topics, options)
    if not success then
      print("Error subscribing MQTT: " .. tostring(result))
      return nil
    end
    return result
  end
  
  function self:unsubscribe(topic_or_topics, options)
    local success, result = pcall(_PY.mqtt_client_unsubscribe, self.conn_id, topic_or_topics, options)
    if not success then
      print("Error unsubscribing MQTT: " .. tostring(result))
      return nil
    end
    return result
  end
  
  function self:publish(topic, payload, options)
    local success, result = pcall(_PY.mqtt_client_publish, self.conn_id, topic, payload, options)
    if not success then
      print("Error publishing MQTT: " .. tostring(result))
      return nil
    end
    return result
  end
  
  local pstr = "MQTTClient object: "..tostring(self):match("%s(.*)")
  setmetatable(self,{__tostring = function(_) return pstr end})
  return self
end

function net.MQTTClientTls(options)
  local options = options or {}
  local self = {}
  self.conn_id = _PY.mqtt_client_create()  -- Remove the true parameter
  
  function self:addEventListener(eventName, callback)
    local success, err = pcall(_PY.mqtt_client_add_event_listener, self.conn_id, eventName, callback)
    if not success then
      print("Error adding MQTT TLS event listener: " .. tostring(err))
    end
  end
  
  function self:connect(uri, options)
    local success, err = pcall(_PY.mqtt_client_connect, self.conn_id, uri, options)
    if not success then
      print("Error connecting MQTT TLS: " .. tostring(err))
    end
  end
  
  function self:disconnect(options)
    local success, err = pcall(_PY.mqtt_client_disconnect, self.conn_id, options)
    if not success then
      print("Error disconnecting MQTT TLS: " .. tostring(err))
    end
  end
  
  function self:subscribe(topic_or_topics, options)
    local success, result = pcall(_PY.mqtt_client_subscribe, self.conn_id, topic_or_topics, options)
    if not success then
      print("Error subscribing MQTT TLS: " .. tostring(result))
      return nil
    end
    return result
  end
  
  function self:unsubscribe(topic_or_topics, options)
    local success, result = pcall(_PY.mqtt_client_unsubscribe, self.conn_id, topic_or_topics, options)
    if not success then
      print("Error unsubscribing MQTT TLS: " .. tostring(result))
      return nil
    end
    return result
  end
  
  function self:publish(topic, payload, options)
    local success, result = pcall(_PY.mqtt_client_publish, self.conn_id, topic, payload, options)
    if not success then
      print("Error publishing MQTT TLS: " .. tostring(result))
      return nil
    end
    return result
  end
  
  local pstr = "MQTTClientTls object: "..tostring(self):match("%s(.*)")
  setmetatable(self,{__tostring = function(_) return pstr end})
  return self
end

-- MQTT QoS constants
net.QoS = {
    AT_MOST_ONCE = 0,
    AT_LEAST_ONCE = 1,
    EXACTLY_ONCE = 2,
}

-- Synchronous TCP Functions (for coroutine-based programming)
-- These functions work with coroutines to provide synchronous-looking async operations

function net.tcp_connect_sync(host, port)
  local co = coroutine.running()
  if not co then
    error("net.tcp_connect_sync must be called from within a coroutine")
  end
  
  _PY.tcp_connect(host, port, function(success, conn_id, message)
    coroutine.resume(co, success, conn_id, message)
  end)
  
  return coroutine.yield()
end

function net.tcp_write_sync(conn_id, data)
  local co = coroutine.running()
  if not co then
    error("net.tcp_write_sync must be called from within a coroutine")
  end
  
  _PY.tcp_write(conn_id, data, function(success, bytes_written, message)
    coroutine.resume(co, success, bytes_written, message)
  end)
  
  return coroutine.yield()
end

function net.tcp_read_sync(conn_id, pattern)
  local co = coroutine.running()
  if not co then
    error("net.tcp_read_sync must be called from within a coroutine")
  end
  
  _PY.tcp_read(conn_id, pattern, function(success, data, message)
    coroutine.resume(co, success, data, message)
  end)
  
  return coroutine.yield()
end

function net.tcp_close_sync(conn_id)
  local co = coroutine.running()
  if not co then
    error("net.tcp_close_sync must be called from within a coroutine")
  end
  
  _PY.tcp_close(conn_id, function(success, message)
    coroutine.resume(co, success, message)
  end)
  
  return coroutine.yield()
end

-- Alternative: Direct synchronous functions (blocking, no coroutines needed)
-- These use the Python synchronous TCP functions directly

function net.tcp_connect_direct(host, port)
  return _PY.tcp_connect_sync(host, port)
end

function net.tcp_write_direct(conn_id, data)
  return _PY.tcp_write_sync(conn_id, data)
end

function net.tcp_read_direct(conn_id, pattern)
  return _PY.tcp_read_sync(conn_id, pattern)
end

function net.tcp_close_direct(conn_id)
  return _PY.tcp_close_sync(conn_id)
end

-------------------- Extra net utilities, not standard Fibaro ------------------
-- Create TCP server

local tcp_server_create = _PY.tcp_server_create
local tcp_server_start = _PY.tcp_server_start
local tcp_server_add_event_listener = _PY.tcp_server_add_event_listener
local tcp_server_close = _PY.tcp_server_close

function net.TCPServer(debugFlag)
  local self = { _debug = debugFlag}
  self.server_id = tcp_server_create()

  local function debug(...) 
    if self._debug then print("[Server] "..tostring(self.server_id), string.format(...)) end
  end

  debug("Created TCP server with id %s", tostring(self.server_id))
  
  function self:start(host, port, callback)
    tcp_server_add_event_listener(self.server_id, "client_connected", function(client_id, addr)
      debug("Client connected: %s from %s", tostring(client_id), tostring(addr))
      local stat,res = pcall(callback,net.TCPSocket():_wrap(client_id), addr)
      if not stat then
        self._debug = true
        debug("Error in callback: %s", tostring(res))
      end
    end)
    
    tcp_server_add_event_listener(self.server_id, "client_disconnected", function(client_id, addr)
      debug("Client disconnected: %s from %s", tostring(client_id), tostring(addr))
    end)
    
    tcp_server_add_event_listener(self.server_id, "error", function(error_msg)
      debug("TCP Server error: %s", tostring(error_msg))
    end)
    
    tcp_server_start(self.server_id, host, port)
    debug("TCP Server started on %s:%s",host, port)
  end
  
  function self:stop()
    if self.server_id then
      tcp_server_close(self.server_id)
      debug("TCP Server stopped")
      self.server_id = nil
    end
  end
  
  return self
end

function net.EchoServer(host,port,debugFlag)
  assert(type(host) == "string", "host must be a string")
  assert(type(port) == "number", "port must be a number")
  local server = net.TCPServer()
  local function debug(...) 
    if debugFlag then print("[Echo]",string.format(...)) end
  end
  server:start(host, port, function(client, addr)
    local function echo()
      client:read({
        success = function(data)
          debug("Received from client %s: %s", tostring(client), data:gsub("\n", "\\n"))
          local reply = "Echo: " .. data
          debug("Sending echo: %s", reply:gsub("\n", "\\n"))
          client:write(reply, {
            success = function()
              debug("Echo sent to client %s", tostring(client))
              setTimeout(echo,0)
            end,
            error = function(err)
              debug("Failed to send echo to client %s: %s", tostring(client), tostring(err))
            end
          })
        end,
        error = function(err)
          debug("Failed to read from client %s: %s", tostring(client), tostring(err))
        end
      })
    end
    echo()
  end)
  return server
end

------------- WebSocket Server ------------------
local websocket_server_create = _PY.websocket_server_create
local websocket_server_start = _PY.websocket_server_start
local websocket_server_add_event_listener = _PY.websocket_server_add_event_listener
local websocket_server_send = _PY.websocket_server_send
local websocket_server_close = _PY.websocket_server_close

function net.WebSocketServer(debugFlag)
  local self = { _debug = debugFlag }
  local server_id = websocket_server_create()
  self.server_id = server_id
  
  local function debug(...) 
    if self._debug then print("[Server] "..tostring(self.server_id), string.format(...)) end
  end
  
  debug("Created WS server with id: %s", tostring(server_id))
  
  
  function self:start(host, port, callbacks)
    assert(type(host) == "string", "host must be a string")
    assert(type(port) == "number", "port must be a number")
    self.callbacks = callbacks
    
    -- Register server event listeners
    websocket_server_add_event_listener(server_id, "client_connected", function(client)
      debug("Client connected: %s", tostring(client))
      if self.callbacks.connected then
        local stat,res = pcall(self.callbacks.connected, client)
        if not stat then
          debug("Error in connected callback: %s", tostring(res))
        end
      end
    end)
    
    websocket_server_add_event_listener(server_id, "message", function(client, msg)
      debug("Received from client: %s", msg)
      if self.callbacks.receive then
        local stat,res = pcall(self.callbacks.receive, client, msg)
        if not stat then
          debug("Error in callback: %s", tostring(res))
        end
      end
    end)
    
    websocket_server_add_event_listener(server_id, "client_disconnected", function(client)
      if self.callbacks.disconnected then
        local stat,res = pcall(self.callbacks.disconnected, client)
        if not stat then
          debug("Error in disconnected callback: %s", tostring(res))
        end
      end
    end)
    
    websocket_server_add_event_listener(server_id, "error", function(err)
      debug("Error: %s", tostring(err))
      if self.callbacks.error then
        local stat,res = pcall(self.callbacks.error, err)
        if not stat then
          debug("Error in error callback: %s", tostring(res))
        end
      end
    end)
    
    websocket_server_start(server_id, host, port)
    debug("Listening on ws://%s:%s", host, port)
  end
  
  function self:send(client, msg)
    if not self.server_id then
      return false, "Server not started"
    end
    return websocket_server_send(self.server_id, client, msg)
  end
  
  function self:stop()
    if self.server_id then
      websocket_server_close(self.server_id)
      self.server_id = nil
    end
  end
  
  return self
end

function net.WebSocketEchoServer(host,port,debugFlag)
  
  local server = net.WebSocketServer(debugFlag)
  
  local function debug(...) 
    if debugFlag then print("[EchWS] "..tostring(server.server_id), string.format(...)) end
  end
  
  server:start(host, port, {
    receive = function(client, msg)
      debug("Received from client: %s", msg)
      server:send(client, "Echo "..msg)
    end,
    connected = function(client)
      debug("Client connected: %s", tostring(client))
    end,
    disconnected = function(client)
      debug("Client disconnected: %s", tostring(client))
    end
  })
  return server
end

return net