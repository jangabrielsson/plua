net = {}
_PY = _PY or {}

-- Creates a new HTTP client object.
-- @return A table representing the HTTP client.
function net.HTTPClient()
  local self = {}
  -- url is string
  -- options = { options = { method = "get", headers = {}, data = "...", timeout = 10000 }, success = function(response) end, error = function(status) end }
  function self:request(url, options)
    -- Extract options for call_http
    local call_options = {
      method = options.options and options.options.method or "GET",
      headers = options.options and options.options.headers or {},
      data = options.options and options.options.data or nil,
      timeout = options.options and options.options.timeout or 30
    }
    
    -- Create a callback function that adapts call_http response to net.HTTPClient format
    local callback = function(err, response)
      if err then
        -- Call error callback if provided
        if options.error then
          -- For timeout errors, pass "timeout" string. For other errors, pass the error message
          local error_param = err:lower():find("timeout") and "timeout" or err
          local success, callback_err = pcall(options.error, error_param)
          if not success then
            print("Error in HTTP error callback: " .. tostring(callback_err))
          end
        end
      else
        -- Call success callback if provided
        if options.success then
          -- Adapt call_http response format to net.HTTPClient format
          local res = { 
            status = response.status, 
            data = response.text,  -- call_http uses 'text', net.HTTPClient expects 'data'
            headers = response.headers  -- Include headers in the response
          }
          local success, callback_err = pcall(options.success, res)
          if not success then
            print("Error in HTTP success callback: " .. tostring(callback_err))
          end
        end
      end
    end
    
    -- Use our existing call_http function
    local callback_id = _PY.registerCallback(callback)
    _PY.call_http(url, call_options, callback_id)
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
  local self = { opts = opts, socket = nil, ready = false, pending_operations = {} }

  -- Create UDP socket automatically when constructor is called
  local function createSocket()
    local callback = function(result)
      if result.success then
        self.socket = result.socket_id
        self.ready = true
        _PY.print("UDP socket created with ID: " .. tostring(result.socket_id))
        
        -- Process any pending operations
        for _, operation in ipairs(self.pending_operations) do
          operation()
        end
        self.pending_operations = {}
      else
        print("Error creating UDP socket: " .. tostring(result.message))
        self.ready = false
        
        -- Fail any pending operations
        for _, operation in ipairs(self.pending_operations) do
          -- Call with error
          if operation.error then
            operation.error("Socket creation failed: " .. tostring(result.message))
          end
        end
        self.pending_operations = {}
      end
    end
    local callback_id = _PY.registerCallback(callback)
    _PY.udp_create_socket(callback_id)
  end
  
  -- Create socket immediately
  createSocket()

  function self:sendTo(data, ip, port, opts)
    local opts = opts or {}
    
    local function doSend()
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
        if not result.success then
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
    
    if self.ready then
      doSend()
    else
      -- Queue the operation for when socket is ready
      table.insert(self.pending_operations, doSend)
    end
  end

  function self:receive(opts)
    local opts = opts or {}
    
    local function doReceive()
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
        if not result.success then
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
    
    if self.ready then
      doReceive()
    else
      -- Queue the operation for when socket is ready
      table.insert(self.pending_operations, doReceive)
    end
  end

  -- Convenience method that delegates to sendTo for compatibility
  function self:send(host, port, data, opts)
    return self:sendTo(data, host, port, opts)
  end

  function self:close()
    if self.socket then
      _PY.udp_close(self.socket)
      self.socket = nil
      self.ready = false
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
    self.callback_id = _PY.registerCallback(connection_callback,true)
    _PY.tcp_server_start(self.server, host, port, self.callback_id)
  end

  function self:stop()
    _PY.tcp_server_stop(self.server,self.callback_id)
    _PY.clearRegisteredCallback(self.callback_id)
  end

  return self
end

function net.TCPEchoServer(host,port, system, nodebug)
  local self = net.TCPServer()
  self:start(host,port,function(client_socket, client_ip, client_port)
    if not nodebug then print("Client connected:", client_ip, client_port) end
    
    local function echo()
      -- Read data from the client
      client_socket:read({
        success = function(data)
          if not data or data == "" then return end
          -- Echo received data back to the client
          client_socket:send(data, {
            success = function()
              echo()  -- Continue echoing
            end,
            error = function(err)
              print("Error sending tcp echo:", err)
            end
          })
        end
      })
    end
    echo()
  end)
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
      local data, status_code, response_headers = nil, 404, nil
      
      -- Call the user's callback with method, path, payload, and headers
      if callback then
        local success, result_data, result_status, result_headers = pcall(callback, request.method, request.path, request.body, request.headers)
        if success then
          data = result_data or '{"error": "No data returned"}'
          status_code = result_status or 200
          response_headers = result_headers
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
      _PY.http_server_respond(request.request_id, data, status_code, "application/json", response_headers)
    end
    
    -- Register the request callback and start the server (persistent callback for multiple requests)
    self.callback_id = _PY.registerCallback(request_callback, true)  -- true = persistent
    _PY.http_server_start(self.server, host, port, self.callback_id)
  end
  
  function self:stop()
    if self.server then
      _PY.clearRegisteredCallback(self.callback_id)
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

-- WebSocket Client implementation following Fibaro API
function net.WebSocketClient(options)
  local self = {
    conn_id = nil,
    event_listeners = {},
    connected = false,
    options = options or {}
  }
  
  setmetatable(self, { __tostring = function(_) return "WebSocketClient object: "..tostring(self.conn_id) end })
  
  -- Add event listener for WebSocket events
  function self:addEventListener(event_name, callback)
    if not self.event_listeners[event_name] then
      self.event_listeners[event_name] = {}
    end
    table.insert(self.event_listeners[event_name], callback)
  end
  
  -- Internal method to fire events
  function self:_fireEvent(event_name, ...)
    local listeners = self.event_listeners[event_name]
    if listeners then
      for _, callback in ipairs(listeners) do
        local success, err = pcall(callback, ...)
        if not success then
          print("Error in WebSocket " .. event_name .. " event callback: " .. tostring(err))
        end
      end
    end
  end
  
  -- Connect to WebSocket server
  function self:connect(url, headers)
    if self.connected then
      self:_fireEvent("error", "Already connected")
      return
    end
    
    -- Create a single callback function that will handle all WebSocket events
    local event_callback = function(event_data)
      if event_data.event == "connected" then
        self.conn_id = event_data.conn_id
        self.connected = true
        self:_fireEvent("connected")
      elseif event_data.event == "disconnected" then
        self.connected = false
        self:_fireEvent("disconnected")
      elseif event_data.event == "error" then
        self:_fireEvent("error", event_data.error)
      elseif event_data.event == "dataReceived" then
        self:_fireEvent("dataReceived", event_data.data)
      end
    end
    
    -- Register the callback and make the connection (mark as persistent for multiple events)
    local callback_id = _PY.registerCallback(event_callback, true)  -- true = persistent
    self.callback_id = callback_id  -- Store for cleanup
    local headers = headers or self.options.headers or nil
    self.conn_id = _PY.websocket_connect(url, callback_id, headers)
  end
  
  -- Send data through WebSocket
  function self:send(data)
    if not self.connected or not self.conn_id then
      self:_fireEvent("error", "Not connected")
      return
    end
    
    -- Optional: Add callback for send completion if needed
    _PY.websocket_send(self.conn_id, tostring(data))
  end
  
  -- Check if WebSocket is open
  function self:isOpen()
    if not self.conn_id then
      return false
    end
    return _PY.websocket_is_open(self.conn_id)
  end
  
  -- Close WebSocket connection
  function self:close()
    if self.conn_id then
      _PY.websocket_close(self.conn_id)
      self.conn_id = nil
      self.connected = false
      
      -- Clean up persistent callback if we have it
      if self.callback_id then
        _PY.clearRegisteredCallback(self.callback_id)
        self.callback_id = nil
      end
    end
  end
  
  return self
end

-- WebSocket Client TLS (secure) implementation
function net.WebSocketClientTls(options)
  -- For TLS, we just use the same implementation since the Python side
  -- handles SSL automatically based on the URL scheme (wss://)
  return net.WebSocketClient(options)
end

-- WebSocket Server implementation
function net.WebSocketServer(options,system)
  local self = {
    server_id = nil,
    running = false,
    clients = {},
    callbacks = {},
    system = system or false,
    options = options or {}
  }

  setmetatable(self, { __tostring = function(_) return "WebSocketServer object: "..tostring(self.server_id) end })
  
  -- Start the WebSocket server
  function self:start(host, port, callbacks)
    if self.running then
      if callbacks and callbacks.error then
        callbacks.error("Server already running")
      end
      return
    end
    
    self.callbacks = callbacks or {}
    
    -- Create server and get server ID
    self.server_id = _PY.websocket_server_create()
    
    -- Create callback function to handle server events
    local server_callback = function(event_data)
      if event_data.event == "started" then
        self.running = true
        if self.callbacks.started then
          local success, err = pcall(self.callbacks.started)
          if not success then
            print("Error in WebSocket server started callback: " .. tostring(err))
          end
        end
      elseif event_data.event == "connected" then
        local client_id = event_data.client_id
        self.clients[client_id] = { id = client_id, connected = true }
        if self.callbacks.connected then
          local success, err = pcall(self.callbacks.connected, client_id)
          if not success then
            print("Error in WebSocket server connected callback: " .. tostring(err))
          end
        end
      elseif event_data.event == "disconnected" then
        local client_id = event_data.client_id
        if self.clients[client_id] then
          self.clients[client_id].connected = false
          self.clients[client_id] = nil
        end
        if self.callbacks.disconnected then
          local success, err = pcall(self.callbacks.disconnected, client_id)
          if not success then
            print("Error in WebSocket server disconnected callback: " .. tostring(err))
          end
        end
      elseif event_data.event == "receive" then
        local client_id = event_data.client_id
        local data = event_data.data
        if self.callbacks.receive then
          local success, err = pcall(self.callbacks.receive, client_id, data)
          if not success then
            print("Error in WebSocket server receive callback: " .. tostring(err))
          end
        end
      elseif event_data.event == "error" then
        local error_msg = event_data.error
        if self.callbacks.error then
          local success, err = pcall(self.callbacks.error, error_msg)
          if not success then
            print("Error in WebSocket server error callback: " .. tostring(err))
          end
        end
      end
    end
    
    -- Register the callback and start the server
    local system = self.system or false
    local callback_id = _PY.registerCallback(server_callback, true, system)  -- persistent
    self.callback_id = callback_id
    
    _PY.websocket_server_start(self.server_id, host, port, callback_id)
  end
  
  -- Send data to a specific client
  function self:send(client_id, data)
    if not self.running or not self.server_id then
      if self.callbacks.error then
        self.callbacks.error("Server not running")
      end
      return
    end
    
    if not self.clients[client_id] or not self.clients[client_id].connected then
      if self.callbacks.error then
        self.callbacks.error("Client " .. tostring(client_id) .. " not connected")
      end
      return
    end
    
    _PY.websocket_server_send(self.server_id, client_id, tostring(data))
  end
  
  -- Stop the server
  function self:stop()
    if not self.running then
      return
    end
    
    if self.server_id then
      _PY.websocket_server_stop(self.server_id)
      self.running = false
      self.clients = {}
      
      -- Clean up persistent callback
      if self.callback_id then
        _PY._callback_registry[self.callback_id] = nil
        _PY._persistent_callbacks[self.callback_id] = nil
        self.callback_id = nil
      end
    end
  end
  
  -- Check if server is running
  function self:isRunning()
    if not self.server_id then
      return false
    end
    return _PY.websocket_server_is_running(self.server_id)
  end
  
  -- Get list of connected clients
  function self:getClients()
    local client_list = {}
    for client_id, client_info in pairs(self.clients) do
      if client_info.connected then
        table.insert(client_list, client_id)
      end
    end
    return client_list
  end
  
  return self
end

-- WebSocket Echo Server utility function
function net.WebSocketEchoServer(host, port, debugFlag)
  
  local server = net.WebSocketServer(nil,true)
  
  local function debug(...) 
    if debugFlag then print("[EchWS] "..tostring(server.server_id), string.format(...)) end
  end
  
  server:start(host, port, {
    receive = function(client, msg)
      debug("Received from client: %s", msg)
      server:send(client, "Echo: "..msg)
    end,
    connected = function(client)
      debug("Client connected: %s", tostring(client))
    end,
    error = function(err)
      debug("Server error: %s", tostring(err))
    end,
    disconnected = function(client)
      debug("Client disconnected: %s", tostring(client))
    end,
    started = function()
      debug("Echo server started on %s:%d", host, port)
    end
  })
  return server
end

-- ============================================================================
-- MQTT Client Implementation (Fibaro HC3 Compatible)
-- ============================================================================

-- QoS enum following Fibaro spec
net.QoS = {
  AT_MOST_ONCE = 0,
  AT_LEAST_ONCE = 1,
  EXACTLY_ONCE = 2
}

-- Connect return codes following Fibaro spec
net.MQTTConnectReturnCode = {
  CONNECTION_ACCEPTED = 0,
  UNACCEPTABLE_PROTOCOL_VERSION = 1,
  IDENTIFIER_REJECTED = 2,
  SERVER_UNAVAILABLE = 3,
  BAD_USERNAME_OR_PASSWORD = 4,
  NOT_AUTHORIZED = 5
}

-- MQTT Client namespace
net.Client = {}

-- Main MQTT Client creation function (Fibaro style)
function net.Client.connect(uri, options)
  local self = {
    client_id = nil,
    connected = false,
    event_listeners = {},
    callback_id = nil,
    event_callback_ids = {}
  }
  
  -- Connect to MQTT broker
  local options = options or {}
  local callback = nil
  if options and options.callback then
    callback = options.callback
    options.callback = nil -- Remove from options so not sent to Python
  end
  local callback_id = callback and _PY.registerCallback(callback, true) or nil  -- true = persistent for multiple events
  self.callback_id = callback_id  -- Store for cleanup
  self.client_id = _PY.mqtt_client_connect(uri, options, callback_id)
  
  -- Disconnect method
  function self:disconnect(options)
    if not self.client_id then
      return
    end
    
    options = options or {}
    
    local callback = nil
    if options.callback then
      callback = function(error_code)
        options.callback(error_code)
      end
    end
    
    local callback_id = callback and _PY.registerCallback(callback) or nil
    _PY.mqtt_client_disconnect(self.client_id, callback_id)
    
    -- Clean up persistent callback if we have it
    if self.callback_id then
      _PY.clearRegisteredCallback(self.callback_id)
      self.callback_id = nil
    end
  end

  -- Subscribe method
  function self:subscribe(topics, options)
    if not self.client_id then
      return nil
    end
    
    options = options or {}
    
    local callback = nil
    if options.callback then
      callback = function(error_code)
        options.callback(error_code)
      end
    end
    
    local callback_id = callback and _PY.registerCallback(callback) or nil
    return _PY.mqtt_client_subscribe(self.client_id, topics, options, callback_id)
  end

  -- Unsubscribe method
  function self:unsubscribe(topics, options)
    if not self.client_id then
      return nil
    end
    
    options = options or {}
    
    local callback = nil
    if options.callback then
      callback = function(error_code)
        options.callback(error_code)
      end
    end
    
    local callback_id = callback and _PY.registerCallback(callback) or nil
    return _PY.mqtt_client_unsubscribe(self.client_id, topics, options, callback_id)
  end

  -- Publish method
  function self:publish(topic, payload, options)
    if not self.client_id then
      return nil
    end
    
    options = options or {}
    
    local callback = nil
    if options.callback then
      callback = function(error_code)
        options.callback(error_code)
      end
    end
    
    local callback_id = callback and _PY.registerCallback(callback) or nil
    return _PY.mqtt_client_publish(self.client_id, topic, payload, options, callback_id)
  end

  -- Add event listener (EventTarget API)
  function self:addEventListener(event_name, callback)
    if not self.client_id or not callback then
      return
    end
    
    -- Store the callback locally
    self.event_listeners[event_name] = callback
    
    -- Create wrapper callback for Python
    local wrapper_callback = function(event_data)
      if self.event_listeners[event_name] then
        self.event_listeners[event_name](event_data)
      end
    end
    
    local callback_id = _PY.registerCallback(wrapper_callback, true)  -- true = persistent for multiple events
    self.event_callback_ids[event_name] = callback_id  -- Store for cleanup
    _PY.mqtt_client_add_event_listener(self.client_id, event_name, callback_id)
  end

  -- Remove event listener
  function self:removeEventListener(event_name)
    if not self.client_id then
      return
    end
    
    -- Remove local callback
    self.event_listeners[event_name] = nil
    
    -- Clean up persistent callback
    if self.event_callback_ids and self.event_callback_ids[event_name] then
      _PY.clearRegisteredCallback(self.event_callback_ids[event_name])
      self.event_callback_ids[event_name] = nil
    end
    
    -- Remove from Python side
    _PY.mqtt_client_remove_event_listener(self.client_id, event_name)
  end

  -- Check if connected
  function self:isConnected()
    if not self.client_id then
      return false
    end
    
    return _PY.mqtt_client_is_connected(self.client_id)
  end

  -- Get client info
  function self:getInfo()
    if not self.client_id then
      return nil
    end
    
    return _PY.mqtt_client_get_info(self.client_id)
  end
  
  return self
end

-- Legacy support: Keep the old MQTTClient for backward compatibility
function net.MQTTClient()
  local self = setmetatable({}, {})
  
  function self:connect(uri, options)
    -- Delegate to the new implementation
    local client = net.Client.connect(uri, options)
    -- Copy methods to self for backward compatibility
    for k, v in pairs(client) do
      if type(v) == "function" then
        self[k] = v
      else
        self[k] = v
      end
    end
    return self
  end
  
  return self
end

-- Return the net module for require()
-- Also create mqtt alias for Fibaro compatibility
mqtt = {
  Client = net.Client,
  QoS = net.QoS,
  MQTTConnectReturnCode = net.MQTTConnectReturnCode
}

return net