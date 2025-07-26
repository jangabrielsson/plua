local Emu = ...
local defaultValues = {}
local HTTP = Emu.lib.router.HTTP

local function Store(args)
  local store,data = {},{}
  local idx = args.idx
  defaultValues[args.name] = args.dflts
  return setmetatable(store, {
    __index = function(t,k)
      if k == '_data' then return data
      elseif data[k] then return {data[k],HTTP.OK}
      else return {nil,HTTP.NOT_FOUND} end
    end,
    __newindex = function(t,k,v)
      local method,value = table.unpack(v)
      if method == 'PUT' then
        if data[k] == nil then error({nil,HTTP.NOT_FOUND})
        else data[k] = value end
      elseif method == 'POST' then
        if data[k]~=nil then error({nil,HTTP.CONFLICT})
        else data[k] = value end
      elseif method == 'DELETE' then
        if data[k]~=nil then
          data[k] = nil
        else error({nil,HTTP.NOT_FOUND}) end
      elseif method == 'INIT' then
        data = value
      else error("Bad method") end
    end,
  })
end

local function strip(store,raw) 
  if raw then return store._data end
  local result = {}
  for _,v in pairs(store._data) do result[#result+1] = v end
  return result
end

local function dflts(name,data)
  for k,v in pairs(defaultValues[name] or {}) do
    if data[k] == nil then data[k] = type(v)=='function' and v() or v end
  end
  return data
end

local store = {
  globalVariables = Store{
    name="globalVariables",idx='name',
    dflts = { 
      readOnly = false,
      isEnum = false,
      enumValues = {},
      created = Emu.lib.userTime,
      modified = Emu.lib.userTime
    },
  },
  rooms = Store{
    name="rooms",idx='id',
    dflts = {
      sectionID = 219,
      isDefault = true,
      visible = true,
      icon = "room_boy",
      iconExtension = "png",
      iconColor = "purple",
      defaultSensors = {},
      meters = {
        energy = 0
      },
      defaultThermostat = nil,
      sortOrder = 1,
      category = "pantry"
    },
  },
  sections = Store{
    name="sections",idx='id',
  },
  customEvents = Store{
    name="customEvents",idx='name',
  },
  ['settings/location'] = Store{
    name="settings/location",idx=nil,
  },
  ['panels/location'] = Store{
    name="panels/location",idx='id',
  },
  ['settings/info'] = Store{
    name="settings/info",idx=nil,
  },
  home = Store{
    name="home",idx=nil,
  },
  weather = Store{
    name="weather",idx=nil,
  }
}

local function setup()

  Emu.lib.loadLib("offline_data",Emu,store)
  
  function Emu.EVENT._sunset_updated()
  end

  local REFRESH_EVENTS = {}
  function REFRESH_EVENTS.GlobalVariableAddedEvent(data) 
    Emu:refreshEvent('GlobalVariableAddedEvent', {
      variableName = data.name,
      value = data.value,
    })
  end
  function REFRESH_EVENTS.GlobalVariableChangedEvent(data,name,oldData)
    if data.value == oldData.value then return end
    Emu:refreshEvent('GlobalVariableChangedEvent', {
      variableName = name,
      newValue = data.value,
      oldValue = oldData.value,
    })
  end
  function REFRESH_EVENTS.GlobalVariableRemovedEvent(data,name) 
    Emu:refreshEvent('GlobalVariableRemovedEvent', {
      variableName = name,
    })
  end

  local function REFRESH(data,typ,...)
    local code = data[2]
    if code < 206 and REFRESH_EVENTS[typ] then
      REFRESH_EVENTS[typ](data[1],...)
    end
    return data
  end

  local function add(path,method)
    local function fun(...)
      local args = {...}
      local _,data = pcall(method,...)
      local res,code = table.unpack(data or {nil,200})
      return res,code
    end
    Emu.lib.router:add(path,fun,true)
  end
  
  local gvs = store.globalVariables
  add("GET/globalVariables", function(path, data, vars, query)
    return {strip(gvs),HTTP.OK}
  end)
  add("GET/globalVariables/<name>", function(path, data, vars, query)
    return gvs[vars.name]
  end)
  add("POST/globalVariables", function(path, data, vars, query)
    local data = dflts('globalVariables',data)
    gvs[data.name or ".."] = {'POST',data}
    return REFRESH({data,HTTP.CREATED},'GlobalVariableAddedEvent')
  end)
  add("PUT/globalVariables/<name>", function(path, data, vars, query)
    local name  = vars.name
    local oldData = gvs[name][1]
    gvs[name] = {'PUT',data}
    return REFRESH({data,HTTP.OK},'GlobalVariableChangedEvent',name,oldData)
  end)
  add("DELETE/globalVariables/<name>", function(path, data, vars, query)
    gvs[vars.name] = {'DELETE'}
    return REFRESH({nil,HTTP.OK},'GlobalVariableRemovedEvent',vars.name)
  end)
  
  add("GET/rooms", function(path, data, vars, query)
    return {strip(store.rooms),HTTP.OK}
  end)
  add("GET/rooms/<id>", function(path, data, vars, query)
    return store.rooms[vars.id]
  end)
  add("POST/rooms", function(path, data, vars, query)
    local data = dflts('rooms',data)
    store.rooms[vars.id] = {'POST',data}
    return {data,HTTP.CREATED}
  end)
  add("PUT/rooms/<id>", function(path, data, vars, query)
    store.rooms[vars.id] = {'PUT',data}
  end)
  add("DELETE/rooms/<id>", function(path, data, vars, query)
    store.rooms[vars.id] = {'DELETE'}
  end)
  
  add("GET/sections", function(path, data, vars, query)
    return {strip(store.sections),HTTP.OK}
  end)
  add("GET/sections/<id>", function(path, data, vars, query)
    return store.sections[vars.id]
  end)
  add("POST/sections", function(path, data, vars, query)
    local data = dflts('sections',data)
    store.sections[vars.id] = {'POST',data}
    return {data,HTTP.CREATED}
  end)
  add("PUT/sections/<id>", function(path, data, vars, query)
    store.sections[vars.id] = {'PUT',data}
  end)
  add("DELETE/sections/<id>", function(path, data, vars, query)
    store.sections[vars.id] = {'DELETE'}
  end)
  
  add("GET/customEvents", function(path, data, vars, query)
    return {strip(store.customEvents),HTTP.OK}
  end)
  add("GET/customEvents/<name>", function(path, data, vars, query)
    return store.customEvents[vars.name]
  end)
  add("POST/customEvents", function(path, data, vars, query)
    local data = dflts('customEvents',data)
    store.customEvents[data.name] = {'POST',data}
    return {data,HTTP.CREATED}
  end)
  add("POST/customEvents/<name>", function(path, data, vars, query)
    Emu:refreshEvent('CustomEvent', {
      name = vars.name,
    })
    return {nil,HTTP.OK}
  end)
  add("PUT/customEvents/<name>", function(path, data, vars, query)
    store.customEvents[vars.name] = {'PUT',data}
  end)
  add("DELETE/customEvents/<name>", function(path, data, vars, query)
    store.customEvents[vars.name] = {'DELETE'}
  end)
  
  add("GET/settings/location", function(path, data, vars, query)
    return {strip(store['settings/location'],true),HTTP.OK}
  end)
  add("PUT/settings/location", function(path, data, vars, query)
    for k,v in pairs(data) do
      store['settings/location'][k] = {'PUT',v}
    end
    return {data,HTTP.OK}
  end)
  
  add("GET/settings/info", function(path, data, vars, query)
    return {strip(store['settings/info'],true),HTTP.OK}
  end)
  add("PUT/settings/location", function(path, data, vars, query)
    for k,v in pairs(data) do
      store['settings/location'][k] = {'PUT',v}
    end
    return {data,HTTP.OK}
  end)
  add("GET/panels/location", function(path, data, vars, query)
    return {strip(store['panels/location']),HTTP.OK}
  end)
    
  add("GET/home", function(path, data, vars, query)
    return {strip(store['home'],true),HTTP.OK}
  end)
  add("PUT/home", function(path, data, vars, query)
    for k,v in pairs(data) do
      store['home'][k] = {'PUT',v}
    end
    return {data,HTTP.OK}
  end)

  add("GET/iosDevices", function(path, data, vars, query)
    return {{},HTTP.OK}
  end)

  add("GET/debugMessages", function(path, data, vars, query)
    return {{},HTTP.OK}
  end)

  add("GET/weather", function(path, data, vars, query)
    return {strip(store.weather,true),HTTP.OK}
  end)
  add("PUT/weather", function(path, data, vars, query)
    for k,v in pairs(data) do
      store.weather[k] = {'PUT',v}
    end
    return {data,HTTP.OK}
  end)

  add("GET/alarms/v1/partitions", function(path, data, vars, query)
    local alarms = {}
    return {alarms,HTTP.OK}
  end)

  add("GET/alarms/v1/partitions/<id>", function(path, data, vars, query)
    local alarms = {}
    return {alarms,HTTP.OK}
  end)

  add("GET/alarms/v1/devices", function(path, data, vars, query)
    local devices = {}
    return {devices,HTTP.OK}
  end)

  add("GET/notificationCenter", function(path, data, vars, query)
    return {{},HTTP.OK}
  end)

  add("GET/profiles", function(path, data, vars, query)
    return {{},HTTP.OK}
  end)

  add("GET/profiles/<id>", function(path, data, vars, query)
    return {{},HTTP.OK}
  end)

  add("GET/icons", function(path, data, vars, query)
    return {{},HTTP.OK}
  end)

  add("GET/users", function(path, data, vars, query)
    return {{},HTTP.OK}
  end)

end

Emu.lib.setupOfflineRoutes = setup