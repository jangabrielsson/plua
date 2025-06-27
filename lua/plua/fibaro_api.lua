local fmt = string.format

function string.split(inputstr, sep)
  local t={}
  for str in string.gmatch(inputstr, "([^"..(sep or "%s").."]+)") do t[#t+1] = str end
  return t
end

local urldecode = function(url)
  return (url:gsub("%%(%x%x)", function(x) return string.char(tonumber(x, 16)) end))
end

local function API()
  local self = {}
  self.HTTP = {
    OK=200, CREATED=201, ACCEPTED=202, NO_CONTENT=204,MOVED_PERMANENTLY=301, FOUND=302, NOT_MODIFIED=304,
    BAD_REQUEST=400, UNAUTHORIZED=401, FORBIDDEN=403, NOT_FOUND=404,METHOD_NOT_ALLOWED=405, NOT_ACCEPTABLE=406,
    PROXY_AUTHENTICATION_REQUIRED=407, REQUEST_TIMEOUT=408, CONFLICT=409, GONE=410, LENGTH_REQUIRED=411,
    INTERNAL_SERVER_ERROR=500, NOT_IMPLEMENTED=501
  }
  
  self.DIR = { GET={}, POST={}, PUT={}, DELETE={} }
  
  local converts = {
    ['<id>'] = function(v) return tonumber(v) end,
    ['<name>'] = function(v) return v end,
  }
  
  function self:add(...)
    local args = {...}
    local method,path,handler,force = args[1],args[2],args[3],args[4]
    if type(path) == 'function' then -- shift args
      method,handler,force = args[1],args[2],args[3] 
      method,path = method:match("(.-)(/.+)") -- split method and path
    end
    local path = string.split(path,'/')
    local d = self.DIR[method:upper()]
    for _,p in ipairs(path) do
      local p0 = p
      p = ({['<id>']=true,['<name>']=true})[p] and '_match' or p
      local d0 = d[p]
      if d0 == nil then d[p] = {} end
      if p == '_match' then d._fun = converts[p0] d._var = p0:sub(2,-2) end
      d = d[p]
    end
    assert(force==true or d._handler == nil,fmt("Duplicate path: %s/%s",method,path))
    d._handler = handler
  end
  
  local function parseQuery(queryStr)
    local params = {}
    local query = urldecode(queryStr)
    local p = query:split("&")
    for _,v in ipairs(p) do
      local k,v = v:match("(.-)=(.*)")
      params[k] = tonumber(v) or v
    end
    return params
  end
  
  function self:getRoute(method,path)
    local pathStr,queryStr = path:match("(.-)%?(.*)") 
    path = pathStr or path
    local query = queryStr and parseQuery(queryStr) or {}
    local path = string.split(path,'/')
    local d,vars = self.DIR[method:upper()],{}
    for _,p in ipairs(path) do
      if d._match and not d[p] then 
        local v = d._fun(p)
        if v == nil then return nil,vars end
        vars[d._var] =v 
        p = '_match'
      end
      local d0 = d[p]
      if d0 == nil then return nil,vars end
      d = d0
    end
    return d._handler,vars,query
  end
  return self
end

-- Usage:
-- local router = API()
-- router:add("GET", "/api/devices", function(data, queryParameters)
--   return {status = "ok"},200
-- end)
-- router:add("POST", "/api/devices", function(data, queryParameters)
--   return {status = "ok"},200
-- end)
-- router:add("PUT", "/api/devices/<id>", function(data, queryParameters)
--   return {status = "ok"},200
-- end)
-- router:add("DELETE", "/api/devices/<id>", function(data, queryParameters)
--   return {status = "ok"},200
-- end)

-- Create a global router instance that gets set up once
local router = nil

-- Function to set up the router with all endpoints (called once)
local function setup_router()
  if router then
    return router  -- Already set up
  end
  
  router = API()
  
  -- Helper function to create response
  local function create_response(data, status)
    return data, status or 200
  end
  
-- Helper function to create a redirect response
local function create_redirect_response(hostname, port)
  return {
    _redirect = true,
    hostname = hostname,
    port = port or 80
  }
end

  -- Register all endpoints sorted by path
  router:add("POST", "/alarms/v1/partitions/actions/arm", function(data, queryParameters)
    --return create_response({status = "armed"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("DELETE", "/alarms/v1/partitions/actions/arm", function(data, queryParameters)
    --return create_response({status = "disarmed"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/alarms/v1/partitions/<id>/actions/arm", function(data, queryParameters, vars)
    --return create_response({status = "armed"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("DELETE", "/alarms/v1/partitions/<id>/actions/arm", function(data, queryParameters, vars)
    --return create_response({status = "disarmed"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/alarms/v1/partitions/actions/tryArm", function(data, queryParameters)
    --return create_response({status = "try_armed"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/alarms/v1/partitions/<id>/actions/tryArm", function(data, queryParameters, vars)
    --return create_response({status = "try_armed"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/callAction", function(data, queryParameters)
    --return create_response({status = "action_executed"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/customEvents", function(data, queryParameters)
    --return create_response({status = "created"}, 201)
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/customEvents", function(data, queryParameters)
    --return create_response({event1 = {name = "testEvent", userdescription = "Test event"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/customEvents/<name>", function(data, queryParameters, vars)
    --return create_response({name = vars.name, userdescription = "Test event"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/customEvents/<name>", function(data, queryParameters, vars)
    --return create_response({status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("PUT", "/api/customEvents/<name>", function(data, queryParameters, vars)
    --return create_response({status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("DELETE", "/api/customEvents/<name>", function(data, queryParameters, vars)
    --return create_response({status = "deleted"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/customEvents/<name>/emit", function(data, queryParameters, vars)
    --return create_response({status = "emitted"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/debugMessages", function(data, queryParameters)
    --return create_response({status = "added"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/devices", function(data, queryParameters)
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/devices/<id>", function(data, queryParameters, vars)
    --return create_response({id = vars.id, name = "Device" .. vars.id})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("DELETE", "/api/devices/<id>", function(data, queryParameters, vars)
    --return create_response({status = "deleted"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/devices/<id>/action/<name>", function(data, queryParameters, vars)
    --return create_response({status = "action_executed", deviceId = vars.id, action = vars.name})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/diagnostics", function(data, queryParameters)
    --return create_response({status = "ok", version = "1.0.0"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/energy/devices", function(data, queryParameters)
    --return create_response({device1 = {id = 1, name = "Energy Meter"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/globalVariables", function(data, queryParameters)
    --return create_response({var1 = {name = "var1", value = "foo"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/globalVariables/<name>", function(data, queryParameters, vars)
    --return create_response({name = vars.name, value = "foo"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/home", function(data, queryParameters)
    --return create_response({hcName = "Home Center", currency = "USD"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/home", function(data, queryParameters)
    --return create_response({status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("PUT", "/api/home", function(data, queryParameters)
    --return create_response({status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/icons", function(data, queryParameters)
    --return create_response({icon1 = {id = 1, name = "Light Icon"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/iosDevices", function(data, queryParameters)
    --return create_response({device1 = {id = 1, name = "iPhone"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/notificationCenter", function(data, queryParameters)
    --return create_response({notification1 = {id = 1, message = "Test notification"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/panels/climate", function(data, queryParameters)
    --return create_response({climate1 = {id = 1, temperature = 22}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/panels/climate/<id>", function(data, queryParameters, vars)
    --return create_response({id = vars.id, temperature = 22})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/panels/family", function(data, queryParameters)
    --return create_response({family1 = {id = 1, name = "Family"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/panels/favoriteColors", function(data, queryParameters)
    --return create_response({color1 = {id = 1, name = "Blue"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/panels/favoriteColors/v2", function(data, queryParameters)
    --return create_response({color1 = {id = 1, name = "Blue", version = "2"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/panels/humidity", function(data, queryParameters)
    --return create_response({humidity1 = {id = 1, value = 45}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/panels/location", function(data, queryParameters)
    --return create_response({location1 = {id = 1, name = "Home"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/panels/notifications", function(data, queryParameters)
    --return create_response({notification1 = {id = 1, message = "Panel notification"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/panels/sprinklers", function(data, queryParameters)
    --return create_response({sprinkler1 = {id = 1, name = "Garden Sprinkler"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/plugins/<id>/variables", function(data, queryParameters, vars)
    --return create_response({key1 = "value1", key2 = "value2"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/plugins/<id>/variables", function(data, queryParameters, vars)
    --return create_response({status = "created"}, 201)
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("DELETE", "/api/plugins/<id>/variables", function(data, queryParameters, vars)
    --return create_response({status = "deleted"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/plugins/<id>/variables/<name>", function(data, queryParameters, vars)
    --return create_response({value = "test_value"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/plugins/<id>/variables/<name>", function(data, queryParameters, vars)
    --return create_response({status = "updated"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("PUT", "/api/plugins/<id>/variables/<name>", function(data, queryParameters, vars)
    --return create_response({status = "updated"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("DELETE", "/api/plugins/<id>/variables/<name>", function(data, queryParameters, vars)
    --return create_response({status = "deleted"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/plugins/callUIEvent", function(data, queryParameters)
    --return create_response({status = "ui_event_called"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/plugins/createChildDevice", function(data, queryParameters)
    --return create_response({id = 1, status = "created"}, 201)
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/plugins/publishEvent", function(data, queryParameters)
    --return create_response({status = "published"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/plugins/removeChildDevice/<id>", function(data, queryParameters, vars)
    --return create_response({status = "deleted"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/plugins/restart", function(data, queryParameters)
    --return create_response({status = "restarted"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/plugins/updateProperty", function(data, queryParameters)
    --return create_response({status = "property_updated"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/plugins/updateView", function(data, queryParameters)
    --return create_response({status = "view_updated"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/profiles", function(data, queryParameters)
    --return create_response({profiles = {profile1 = {id = 1, name = "Admin"}}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/profiles/<id>", function(data, queryParameters, vars)
    --return create_response({id = vars.id, name = "Profile" .. vars.id})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/proxy", function(data, queryParameters)
    --return create_response({status = "ok", proxied = true})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/quickApp", function(data, queryParameters)
    --return create_response({id = 1, status = "imported"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/quickApp/<id>/files", function(data, queryParameters, vars)
    --return create_response({{name = "main.lua", content = "print('Hello')", isMain = true}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/quickApp/<id>/files", function(data, queryParameters, vars)
    --return create_response({status = "created"}, 201)
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("PUT", "/api/quickApp/<id>/files", function(data, queryParameters, vars)
    --return create_response({status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/quickApp/<id>/files/<name>", function(data, queryParameters, vars)
    --return create_response({name = vars.name, content = "print('Hello')", isMain = true})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/quickApp/<id>/files/<name>", function(data, queryParameters, vars)
    --return create_response({status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("PUT", "/api/quickApp/<id>/files/<name>", function(data, queryParameters, vars)
    --return create_response({status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("DELETE", "/api/quickApp/<id>/files/<name>", function(data, queryParameters, vars)
    --return create_response({status = "deleted"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/quickApp/export/<id>", function(data, queryParameters, vars)
    --return create_response({name = "test.fqa", content = "exported content"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/quickApp/import", function(data, queryParameters)
    --return create_response({status = "imported"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/refreshStates", function(data, queryParameters)
    --return create_response({
    --  events = {
    --    {id = 1, type = "deviceUpdate", timestamp = os.time()},
    --    {id = 2, type = "systemEvent", timestamp = os.time()}
    --  },
    --  last = 2
    --})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/rooms", function(data, queryParameters)
    return create_redirect_response(fibaro.hc3_url, 80)
    --return create_response({room1 = {id = 1, name = "Living Room"}})
  end)
  
  router:add("POST", "/api/rooms", function(data, queryParameters)
    --return create_response({id = 1, status = "created"}, 201)
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/rooms/<id>", function(data, queryParameters, vars)
    --return create_response({id = vars.id, name = "Room" .. vars.id})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/rooms/<id>", function(data, queryParameters, vars)
    --return create_response({id = vars.id, status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("PUT", "/api/rooms/<id>", function(data, queryParameters, vars)
    --return create_response({id = vars.id, status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("DELETE", "/api/rooms/<id>", function(data, queryParameters, vars)
    --return create_response({status = "deleted"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/sections", function(data, queryParameters)
    --return create_response({section1 = {id = 1, name = "Main Section"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/sections", function(data, queryParameters)
    --return create_response({id = 1, status = "created"}, 201)
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/sections/<id>", function(data, queryParameters, vars)
    --return create_response({id = vars.id, name = "Section" .. vars.id})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/sections/<id>", function(data, queryParameters, vars)
    --return create_response({id = vars.id, status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("PUT", "/api/sections/<id>", function(data, queryParameters, vars)
    --return create_response({id = vars.id, status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("DELETE", "/api/sections/<id>", function(data, queryParameters, vars)
    --return create_response({status = "deleted"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/settings", function(data, queryParameters)
    --return create_response({setting = "value"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/settings/<name>", function(data, queryParameters, vars)
    --return create_response({name = vars.name, value = "setting_value"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/users", function(data, queryParameters)
    --return create_response({user1 = {id = 1, name = "Admin User"}})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("GET", "/api/weather", function(data, queryParameters)
    --return create_response({temperature = 22.5, humidity = 45})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("POST", "/api/weather", function(data, queryParameters)
    --return create_response({status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  
  router:add("PUT", "/api/weather", function(data, queryParameters)
    --return create_response({status = "modified"})
    return create_redirect_response(fibaro.hc3_url, fibaro.hc3_port)
  end)
  return router
end

-- Helper function to create a normal response
local function create_response(data, status_code)
  status_code = status_code or 200
  return data, status_code
end

local function fibaroapi(method, path, data, queryParameters)
  print("FIBAROAPI called")
  print("fibaroapi called:", method, path, data, queryParameters)
  
  -- Ensure router is set up (only happens once)
  local router = setup_router()
  
  -- Try to get route from router
  local handler, vars, query = router:getRoute(method, path)
  
  if handler then
    local response_data, status_code = handler(data, query or queryParameters, vars)
    
    -- Check if this is a redirect response
    if response_data and response_data._redirect then
      return response_data
    end
    
    -- Return just the data, not the data and status code as a list
    return response_data
  end
  
  -- Default response for unknown endpoints
  return {status = "ok", method = method, path = path}
end

_PY.fibaroapi = fibaroapi