local Emu = ...
local fmt = string.format

function string.split(inputstr, sep)
  local t={}
  for str in string.gmatch(inputstr, "([^"..(sep or "%s").."]+)") do t[#t+1] = str end
  return t
end

local urldecode = function(url)
  return (url:gsub("%%(%x%x)", function(x) return string.char(tonumber(x, 16)) end))
end

local filterkeys = {
  parentId=function(d,v) return tonumber(d.parentId) == tonumber(v) end,
  name=function(d,v) return d.name == v end,
  type=function(d,v) return d.type == v end,
  enabled=function(d,v) return tostring(d.enabled) == tostring(v) end,
  visible=function(d,v) return tostring(d.visible) == tostring(v) end,
  roomID=function(d,v) return tonumber(d.roomID) == tonumber(v) end,
  interface=function(d,v)
    local ifs = d.interfaces or d.interface or {}
    for _,i in ipairs(ifs) do if i == v then return true end end
  end,
  property=function(d,v)
    local prop,val = v:match("%[([^,]+),(.+)%]")
    if not prop then return false end
    return tostring(d.properties[prop]) == tostring(val)
  end,
}

-- local var = api.get("/devices?property=[lastLoggedUser,"..val.."]") 
local function filter1(q,d)
  for k,v in pairs(q) do 
    if not(filterkeys[k] and filterkeys[k](d,v)) then return false end 
  end
  return true
end

local function filter(q,ds)
  local r = {}
  for _,d in pairs(ds) do if filter1(q,d) then r[#r+1] = d end end
  return r
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

-- Helper function to create response
local function create_response(data, status)
  return data, status or 200
end

local router = API()
local HTTP = router.HTTP
local hc3api = Emu.api.hc3

-- Register all endpoints sorted by path
router:add("POST", "/alarms/v1/partitions/actions/arm", function(path, data, vars, query)
  --return create_response({status = "armed"})
  return nil,301
end)

router:add("DELETE", "/alarms/v1/partitions/actions/arm", function(path, data, vars, query)
  --return create_response({status = "disarmed"})
  return nil,301
end)

router:add("POST", "/alarms/v1/partitions/<id>/actions/arm", function(path, data, vars, query)
  --return create_response({status = "armed"})
  return nil,301
end)

router:add("DELETE", "/alarms/v1/partitions/<id>/actions/arm", function(path, data, vars, query)
  --return create_response({status = "disarmed"})
  return nil,301
end)

router:add("POST", "/alarms/v1/partitions/actions/tryArm", function(path, data, vars, query)
  --return create_response({status = "try_armed"})
  return nil,301
end)

router:add("POST", "/alarms/v1/partitions/<id>/actions/tryArm", function(path, data, vars, query)
  --return create_response({status = "try_armed"})
  return nil,301
end)

router:add("POST", "/callAction", function(path, data, vars, query)
  --return create_response({status = "action_executed"})
  return nil,301
end)

router:add("POST", "/customEvents", function(path, data, vars, query)
  --return create_response({status = "created"}, 201)
  return nil,301
end)

router:add("GET", "/customEvents", function(path, data, vars, query)
  --return create_response({event1 = {name = "testEvent", userdescription = "Test event"}})
  return nil,301
end)

router:add("GET", "/customEvents/<name>", function(path, data, vars, query)
  --return create_response({name = vars.name, userdescription = "Test event"})
  return nil,301
end)

router:add("POST", "/customEvents/<name>", function(path, data, vars, query)
  --return create_response({status = "modified"})
  return nil,301
end)

router:add("PUT", "/customEvents/<name>", function(path, data, vars, query)
  --return create_response({status = "modified"})
  return nil,301
end)

router:add("DELETE", "/customEvents/<name>", function(path, data, vars, query)
  --return create_response({status = "deleted"})
  return nil,301
end)

router:add("POST", "/customEvents/<name>/emit", function(path, data, vars, query)
  --return create_response({status = "emitted"})
  return nil,301
end)

router:add("POST", "/debugMessages", function(path, data, vars, query)
  --return create_response({status = "added"})
  return nil,301
end)

local function indexMap(t,key) local r = {} for _,v in ipairs(t) do r[v[key]] = v end return r end

router:add("GET", "/devices", function(path, data, vars, query)
  local devs = Emu.offline and {} or hc3api.get(path)
  local res = indexMap(devs,'id')
  for id,dev in pairs(Emu.DIR) do
    res[id] = res[id] or dev.device
  end
  return filter(query, res),HTTP.OK
end)

router:add("GET", "/devices/<id>", function(path, data, vars, query)
  if Emu.DIR[vars.id] then
    return Emu.DIR[vars.id].device,HTTP.OK
  elseif Emu.offline then
    return nil,HTTP.NOT_FOUND
  else
    return nil,301
  end
end)

router:add("DELETE", "/devices/<id>", function(path, data, vars, query)
  --return create_response({status = "deleted"})
  return nil,301
end)

router:add("POST", "/devices/<id>/action/<name>", function(path, data, vars, query)
  local id = vars.id
  local dev = Emu.DIR[id]
  if not dev then 
    if Emu.offline then return nil,HTTP.NOT_FOUND else return hc3api.post(path,data) end
  else
    if dev.device.isChild then dev = Emu.DIR[dev.device.parentId] end
    -- Call onAction directly instead of using setTimeout to avoid event loop issues
    dev.env.onAction(id,{ deviceId = id, actionName = vars.name, args = data.args })
    return nil,HTTP.OK
  end
end)

router:add("GET", "/devices/<id>/action/<name>", function(path, data, vars, query)
  local id = vars.id
  local dev = Emu.DIR[id]
  if not dev then 
    if Emu.offline then return nil,HTTP.NOT_FOUND else return hc3api.get(path,data) end
  else
    local action = vars.name
    local data,args = {},{}
    for k,v in pairs(query) do data[#data+1] = {k,v} end
    table.sort(data,function(a,b) return a[1] < b[1] end)
    for _,d in ipairs(data) do args[#args+1] = d[2] end
    -- Call onAction directly instead of using setTimeout to avoid event loop issues
    if dev.device.isChild then dev = Emu.DIR[dev.device.parentId] end
    dev.env.onAction(id,{ deviceId = id, actionName = action, args =args})
    return nil,HTTP.OK
  end
end)

router:add("GET", "/devices/<id>/properties/<name>", function(path, data, vars, query)
  local id,name = vars.id,vars.name
  if id == 1 and (name == "sunriseHour" or name == "sunsetHour") then
    return {value=Emu[name],modified=0},HTTP.OK
  end
  local dev = Emu.DIR[id]
  if not dev then if Emu.offline then return nil,HTTP.NOT_FOUND else return hc3api.get(path) end end
  return {value=dev.device.properties[name],modified=0},HTTP.OK
end)

router:add("GET", "/diagnostics", function(path, data, vars, query)
  --return create_response({status = "ok", version = "1.0.0"})
  return nil,301
end)

router:add("GET", "/energy/devices", function(path, data, vars, query)
  --return create_response({device1 = {id = 1, name = "Energy Meter"}})
  return nil,301
end)

router:add("GET", "/globalVariables", function(path, data, vars, query)
  return create_response({var1 = {name = "var1", value = "foo"}})
  --return nil,301
end)

router:add("GET", "/globalVariables/<name>", function(path, data, vars, query)
  --return create_response({name = vars.name, value = "foo"})
  return nil,301
end)

router:add("POST", "/globalVariables", function(path, data, vars, query)
  --return create_response({name = vars.name, value = "foo"})
  return nil,301
end)

router:add("PUT", "/globalVariables/<name>", function(path, data, vars, query)
  --return create_response({name = vars.name, value = "foo"})
  return nil,301
end)

router:add("GET", "/home", function(path, data, vars, query)
  --return create_response({hcName = "Home Center", currency = "USD"})
  return nil,301
end)

router:add("POST", "/home", function(path, data, vars, query)
  --return create_response({status = "modified"})
  return nil,301
end)

router:add("PUT", "/home", function(path, data, vars, query)
  --return create_response({status = "modified"})
  return nil,301
end)

router:add("GET", "/icons", function(path, data, vars, query)
  --return create_response({icon1 = {id = 1, name = "Light Icon"}})
  return nil,301
end)

router:add("GET", "/iosDevices", function(path, data, vars, query)
  --return create_response({device1 = {id = 1, name = "iPhone"}})
  return nil,301
end)

router:add("GET", "/notificationCenter", function(path, data, vars, query)
  --return create_response({notification1 = {id = 1, message = "Test notification"}})
  return nil,301
end)

router:add("GET", "/panels/climate", function(path, data, vars, query)
  --return create_response({climate1 = {id = 1, temperature = 22}})
  return nil,301
end)

router:add("GET", "/panels/climate/<id>", function(path, data, vars, query)
  --return create_response({id = vars.id, temperature = 22})
  return nil,301
end)

router:add("GET", "/panels/family", function(path, data, vars, query)
  --return create_response({family1 = {id = 1, name = "Family"}})
  return nil,301
end)

router:add("GET", "/panels/favoriteColors", function(path, data, vars, query)
  --return create_response({color1 = {id = 1, name = "Blue"}})
  return nil,301
end)

router:add("GET", "/panels/favoriteColors/v2", function(path, data, vars, query)
  --return create_response({color1 = {id = 1, name = "Blue", version = "2"}})
  return nil,301
end)

router:add("GET", "/panels/humidity", function(path, data, vars, query)
  --return create_response({humidity1 = {id = 1, value = 45}})
  return nil,301
end)

router:add("GET", "/panels/location", function(path, data, vars, query)
  --return create_response({location1 = {id = 1, name = "Home"}})
  return nil,301
end)

router:add("GET", "/panels/notifications", function(path, data, vars, query)
  --return create_response({notification1 = {id = 1, message = "Panel notification"}})
  return nil,301
end)

router:add("GET", "/panels/sprinklers", function(path, data, vars, query)
  --return create_response({sprinkler1 = {id = 1, name = "Garden Sprinkler"}})
  return nil,301
end)


router:add("GET","/plugins/<id>/variables",function(path, data, vars, query) 
  local dev = Emu.DIR[vars.id]
  if dev then
    local vars,res = dev.vars or {},{}
    for k,v in pairs(vars) do res[#res+1] = { name=k, value=v } end
    return res,HTTP.OK
  end
  return Emu.apihc3.restricted.get(path)
end)

router:add("GET","/plugins/<id>/variables/<name>",function(path, data, vars, query) 
  local dev = Emu.DIR[vars.id]
  if dev then
    if dev.device.isProxy then return Emu.api.hc3.restricted.get(path) end
    local value = (dev.vars or {})[vars.name]
    if value~=nil then return { name=vars.name, value=value },HTTP.OK
    else return nil,HTTP.NOT_FOUND end
  end
  return Emu.api.hc3.restricted.get(path)
end)

router:add("POST","/plugins/<id>/variables",function(path, data, vars, query) 
  local dev = Emu.DIR[vars.id]
  if dev then
    if dev.device.isProxy then return Emu.api.hc3.restricted.post(path,data) end
    dev.vars = dev.vars or {}
    local var = dev.vars[vars.name]
    if var then return nil,HTTP.CONFLICT
    else dev.vars[data.name] = data.value Emu:saveState() return nil,HTTP.CREATED end
  end
  return Emu.api.hc3.restricted.post(path,data)
end)

router:add("PUT","/plugins/<id>/variables/<name>",function(path, data, vars, query)
  local dev = Emu.DIR[vars.id]
  if dev then
    if dev.device.isProxy then return Emu.api.hc3.restricted.put(path,data) end
    local value = (dev.vars or {})[vars.name]
    if value~=nil then dev.vars[vars.name] = data.value Emu:saveState() return nil,HTTP.OK
    else return nil,HTTP.NOT_FOUND end
  end
  return Emu.api.hc3.restricted.put(path,data)
end)

router:add("DELETE","/plugins/<id>/variables/<name>",function(path, data, vars, query) 
  local dev = Emu.DIR[vars.id]
  if dev then
    if dev.device.isProxy then return Emu.api.hc3.restricted.delete(path,data) end
    local var = (dev.vars or {})[vars.name]
    if var~=nil then dev.vars[vars.name] = nil Emu:saveState() return nil,HTTP.OK
    else return nil,HTTP.NOT_FOUND end
  end
  return Emu.api.hc3.restricted.delete(path,data)
end)

router:add("DELETE","/plugins/<id>/variables",function(path, data, vars, query) 
  local dev = Emu.DIR[vars.id]
  if dev then
    if dev.device.isProxy then return Emu.api.hc3.restricted.delete(path,data) end
    dev.vars = {}
    Emu:saveState()
    return nil,HTTP.OK
  end
  return Emu.api.hc3.restricted.delete(path,data)
end)

router:add("POST","/plugins/interfaces",function(path, data, vars, query) 
  local dev = Emu.DIR[vars.id]
  if dev then
    if dev.device.isProxy then return Emu.api.hc3.restricted.delete(path,data) end
    -- ToDo, add interfaces
  end
  return Emu.api.hc3.restricted.delete(path,data)
end)

router:add("POST", "/plugins/callUIEvent", function(path, data, vars, query)
  --return create_response({status = "ui_event_called"})
  local dev = Emu.DIR[data.deviceID]
  if not dev then return nil,400 end
  
  if data.elementName:sub(1,2) == "__" then
    --   data.elementName = data.elementName:sub(3)
    local actionName = data.elementName:sub(3)
    local val = tonumber(data.values[1]) or data.values[1]
    local args = {
      deviceId=dev.device.id,
      actionName=actionName,
      args={val}
    }
    if dev.device.isChild then dev = Emu.DIR[dev.device.parentId] end
    local env = Emu.DIR[dev.device.id].env
    return env.onAction(dev.device.id,args)
  else
    -- Call onUIEvent directly instead of using setTimeout to avoid event loop issues
    dev.env.onUIEvent(data.deviceID,data)
  end
  return nil,HTTP.OK
end)

router:add("POST", "/plugins/createChildDevice", function(path, data, vars, query)
  local data = data
  local parent = data.parentId
  local dev = Emu.DIR[parent]
  if not dev then if Emu.offline then return nil,HTTP.NOT_FOUND else return hc3api.post(path,data) end end
  if dev.device.isProxy then
    local child = hc3api.post(path,data) -- create child on HC3
    if not child then 
      Emu:WARNING("Failed to create child device",json.encode(data or {}))
      return nil,HTTP.BAD_REQUEST
    end
    child.isProxy,child.isChild = true, true
    local ui = Emu.lib.ui.viewLayout2UI(
      child.properties.viewLayout,
      child.properties.uiCallbacks or {}
    )
    local cdev = { device=child, UI=ui, headers=dev.headers }
    Emu:addEmbeds(cdev)
    Emu:registerDevice(cdev)
    ---Emu:INFO(fmt("HC3 proxy child created: %s %s",child.id,child.name))
    return child,HTTP.OK
  end
  local dev = Emu:createChild(data)
  if dev then return dev,HTTP.OK else return nil,HTTP.BAD_REQUEST end
end)

router:add("POST", "/plugins/publishEvent", function(path, data, vars, query)
  --return create_response({status = "published"})
  return nil,301
end)

router:add("DELETE", "/plugins/removeChildDevice/<id>", function(path, data, vars, query)
  local id = vars.id
  local dev = Emu.DIR[id]
  if not dev then 
    if Emu.offline then return nil,HTTP.NOT_FOUND else return hc3api.delete(path) end
  elseif dev.device.isChild then
    Emu.DIR[id] = nil
    if dev.device.isProxy then
      hc3api.delete("/plugins/removeChildDevice/"..id)
    end
    return nil,HTTP.OK
  else return nil,HTTP.NOT_IMPLEMENTED end
end)

router:add("POST", "/plugins/restart", function(path, data, vars, query)
  local dev = Emu.DIR[data.deviceId]
  if dev then
    for ref,typ in pairs(dev.env.plugin._timers or {}) do
      if typ == 'timer' then dev.env.clearTimeout(ref) end
      if typ == 'interv' then dev.env.clearInterval(ref) end
    end
    Emu:restartQA(dev.device.id)
    return nil,HTTP.OK
  end
  --return create_response({status = "restarted"})
  return nil,301
end)

router:add("POST", "/plugins/updateProperty", function(path, data, vars, query)
  local id = data.deviceId
  local dev = Emu.DIR[id]
  if not dev then if Emu.offline then 
    return nil,HTTP.NOT_FOUND else return hc3api.post(path,data) end
  else
    local prop = data.propertyName
    local value = data.value
    if dev.device.properties[prop] ~= value then
      -- Generate refreshState event
      if not dev.device.isProxy then
        Emu:refreshEvent('DevicePropertyUpdatedEvent',{
          id = id,
          property = prop,
          newValue = value,
          oldValue = dev.device.properties[prop]
        })
      end
      if dev.watches and dev.watches[prop] then
        local watch = dev.watches[prop]
        if watch[1] == nil then watch = {watch} end
        for _,w in ipairs(watch) do
          local str = type(w.fmt)=='func'..'tion' and w.fmt(value) or string.format(w.fmt,value)
          Emu:updateView(id,{componentName=w.id,propertyName=w.prop,newValue=str})
        end
      end
      dev.device.properties[prop] = value
      if dev.device.isProxy then return hc3api.post("/plugins/updateProperty",data) end
    end
    return nil,HTTP.OK
  end
end)

router:add("POST", "/plugins/updateView", function(path, data, vars, query)
  --return create_response({status = "view_updated"})
  local id = data.deviceId
  local dev = Emu.DIR[id]
  if not dev then 
    if Emu.offline then return nil,HTTP.NOT_FOUND else return hc3api.post(path,data) end
  else
    -- Call updateView directly instead of using setTimeout to avoid event loop issues
    Emu:updateView(id,data)
    if dev.device.isProxy then return hc3api.post(path,data) end
    return nil,HTTP.OK
  end
end)

router:add("GET", "/profiles", function(path, data, vars, query)
  --return create_response({profiles = {profile1 = {id = 1, name = "Admin"}}})
  return nil,301
end)

router:add("GET", "/profiles/<id>", function(path, data, vars, query)
  --return create_response({id = vars.id, name = "Profile" .. vars.id})
  return nil,301
end)

router:add("GET", "/proxy", function(path, data, vars, query)
  --return create_response({status = "ok", proxied = true})
  return nil,301
end)

router:add("POST", "/quickApp", function(path, data, vars, query)
  --return create_response({id = 1, status = "imported"})
  return nil,301
end)

local function findFile(name,files)
  for i,f in ipairs(files) do if f.name == name then return f,i end end
end

router:add("GET", "/quickApp/<id>/info", function(path, data, vars, query)
  local info = Emu:getQuickApp(vars.id)
  return info,HTTP.OK
end)

router:add("GET", "/quickApp/info", function(path, data, vars, query)
  local info = Emu:getQuickApps()
  return info,HTTP.OK
end)

router:add("GET", "/quickApp/<id>/files", function(path, data, vars, query)
  local dev = Emu.DIR[vars.id]
  if not (dev and dev.files) then if Emu.offline then return nil,HTTP.NOT_FOUND else return nil,301 end end
  local files = {}
  for name,_ in ipairs(dev.files) do
    files[#files+1] = { name = name, isOpen=false, type='lua', isMain = name == 'main' }
  end
  return files,HTTP.OK
end)

router:add("POST", "/quickApp/<id>/files", function(path, data, vars, query)
  local dev = Emu.DIR[vars.id]
  if not dev then if Emu.offline then return nil,HTTP.NOT_FOUND else return nil,301 end end
  local files = dev.files or {}
  if files[data.name] then return nil,HTTP.CONFLICT end
  files[data.name] = { path = nil, content = data.content }
  Emu.api.post("/plugins/restart",{deviceId=dev.device.id})
  return nil,HTTP.CREATED
end)

router:add("PUT", "/quickApp/<id>/files", function(path, data, vars, query)
  print("PUTFILES")
  local dev = Emu.DIR[vars.id]
  if not dev then if Emu.offline then return nil,HTTP.NOT_FOUND else return nil,301 end end
  local files = dev.files or {}
  for _,nf in ipairs(data) do
    if not files[nf.name] then return nil,HTTP.NOT_FOUND end
  end
  for _,nf in ipairs(data) do
    files[nf.name].content = nf.content
  end
  Emu.api.post("/plugins/restart",{deviceId=dev.device.id})
  return nil,HTTP.OK
end)

router:add("GET", "/quickApp/<id>/files/<name>", function(path, data, vars, query)
  local dev = Emu.DIR[vars.id]
  if not dev then if Emu.offline then return nil,HTTP.NOT_FOUND else return nil,301 end end
  local files = dev.files or {}
  local f =  files[vars.name]
  if f then return {name = vars.name, content = f.content, isMain = f.isMain, isOpen=false, type='lua'},HTTP.OK else return nil,HTTP.NOT_FOUND end
end)

router:add("PUT", "/quickApp/<id>/files/<name>", function(path, data, vars, query)
  local dev = Emu.DIR[vars.id]
  if not dev then if Emu.offline then return nil,HTTP.NOT_FOUND else return nil,301 end end
  local files = dev.files or {}
  if not files[vars.name] then return nil,HTTP.NOT_FOUND end
  files[vars.name].content = data.content
  Emu.api.post("/plugins/restart",{deviceId=dev.device.id})
  return nil,HTTP.OK
end)

router:add("DELETE", "/quickApp/<id>/files/<name>", function(path, data, vars, query)
  local dev = Emu.DIR[vars.id]
  if not dev then if Emu.offline then return nil,HTTP.NOT_FOUND else return nil,301 end end
  local files = dev.files or {}
  if not files[vars.name] then return nil,HTTP.NOT_FOUND end
  files[vars.name] = nil
  Emu.api.post("/plugins/restart",{deviceId=dev.device.id})
  return nil,HTTP.OK
end)

router:add("GET", "/quickApp/export/<id>", function(path, data, vars, query)
  local dev = Emu.DIR[vars.id]
  if not dev then if Emu.offline then return nil,HTTP.NOT_FOUND else return nil,301 end end
  local fqa = Emu.lib.getFQA(dev.device.id)
  if fqa then return json.encodeFast(fqa),HTTP.OK else return nil,HTTP.NOT_FOUND end
end)

router:add("POST", "/quickApp/import", function(path, data, vars, query)
  --return create_response({status = "imported"})
  return nil,301
end)

router:add("GET", "/refreshStates", function(path, data, vars, query)
  --return create_response({
  --  events = {
  --    {id = 1, type = "deviceUpdate", timestamp = os.time()},
  --    {id = 2, type = "systemEvent", timestamp = os.time()}
  --  },
  --  last = 2
  --})
  return nil,301
end)

router:add("GET", "/rooms", function(path, data, vars, query)
  return nil,301
  --return create_response({room1 = {id = 1, name = "Living Room"}})
end)

router:add("POST", "/rooms", function(path, data, vars, query)
  --return create_response({id = 1, status = "created"}, 201)
  return nil,301
end)

router:add("GET", "/rooms/<id>", function(path, data, vars, query)
  --return create_response({id = vars.id, name = "Room" .. vars.id})
  return nil,301
end)

router:add("POST", "/rooms/<id>", function(path, data, vars, query)
  --return create_response({id = vars.id, status = "modified"})
  return nil,301
end)

router:add("PUT", "/rooms/<id>", function(path, data, vars, query)
  --return create_response({id = vars.id, status = "modified"})
  return nil,301
end)

router:add("DELETE", "/rooms/<id>", function(path, data, vars, query)
  --return create_response({status = "deleted"})
  return nil,301
end)

router:add("GET", "/sections", function(path, data, vars, query)
  --return create_response({section1 = {id = 1, name = "Main Section"}})
  return nil,301
end)

router:add("POST", "/sections", function(path, data, vars, query)
  --return create_response({id = 1, status = "created"}, 201)
  return nil,301
end)

router:add("GET", "/sections/<id>", function(path, data, vars, query)
  --return create_response({id = vars.id, name = "Section" .. vars.id})
  return nil,301
end)

router:add("POST", "/sections/<id>", function(path, data, vars, query)
  --return create_response({id = vars.id, status = "modified"})
  return nil,301
end)

router:add("PUT", "/sections/<id>", function(path, data, vars, query)
  --return create_response({id = vars.id, status = "modified"})
  return nil,301
end)

router:add("DELETE", "/sections/<id>", function(path, data, vars, query)
  --return create_response({status = "deleted"})
  return nil,301
end)

router:add("GET", "/settings", function(path, data, vars, query)
  --return create_response({setting = "value"})
  return nil,301
end)

router:add("GET", "/settings/<name>", function(path, data, vars, query)
  --return create_response({name = vars.name, value = "setting_value"})
  return nil,301
end)

router:add("GET", "/users", function(path, data, vars, query)
  --return create_response({user1 = {id = 1, name = "Admin User"}})
  return nil,301
end)

router:add("GET", "/weather", function(path, data, vars, query)
  --return create_response({temperature = 22.5, humidity = 45})
  return nil,301
end)

router:add("POST", "/weather", function(path, data, vars, query)
  --return create_response({status = "modified"})
  return nil,301
end)

router:add("PUT", "/weather", function(path, data, vars, query)
  --return create_response({status = "modified"})
  return nil,301
end)

Emu.lib.router = router