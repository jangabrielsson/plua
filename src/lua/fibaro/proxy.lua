local Emu = ...

local fmt = string.format
local start

-- Deploys a proxy QuickApp to the HC3 system 
-- @param name - The name for the proxy device
-- @param devTempl - The device template to use for creating the proxy
-- @return - The created device object from HC3
local function deployProxy(name,headers)
  -- The Lua code that will be installed on the HC3 proxy device
  -- This code creates a QuickApp that can communicate with the emulator
  local code = [[
local fmt = string.format
local con = nil
local ip,port = nil,nil
  
function QuickApp:onInit()
  self:debug("Started", self.name, self.id)
  quickApp = self
  con = self:internalStorageGet("con") or {}
  ip = con.ip
  port = con.port
  local actionUrl,uiUrl = "",""
  if ip and port then
    actionUrl = "http://"..ip..":"..port.."/api/devices/%s/action/%s"
    uiUrl = "http://"..ip..":"..port.."/api/plugins/callUIEvent"
  end
  print(actionUrl)
  print(uiUrl)
  local send
  
  -- Actions that are handled directly by the proxy rather than forwarded to the emulator
  local IGNORE={ MEMORYWATCH=true,APIFUN=true,CONNECT=true }
  
  -- Establishes connection settings for the proxy to communicate with the emulator
  -- @param con - Table containing connection parameters (ip, port)
  function quickApp:CONNECT(con)
    con = con or {}
    self:internalStorageSet("con",con)
    ip = con.ip
    port = con.port
    if ip and port then
      actionUrl = "http://"..ip..":"..port.."/api/devices/%s/action/%s"
      uiUrl = "http://"..ip..":"..port.."/api/plugins/callUIEvent"
    end
    print(actionUrl)
    print(uiUrl)
    self:debug("Connected")
  end
  
  -- Handles actions called on the proxy device
  -- Either handles them locally (for special actions) or forwards them to the emulator
  -- @param action - Action data with actionName and args
  function quickApp:actionHandler(action)
    if IGNORE[action.actionName] then
      print(action.actionName)
      return quickApp:callAction(action.actionName, table.unpack(action.args))
    end
    json.util.InitArray(action.args)
    local data = { args = action.args }
    local url = fmt(actionUrl,action.deviceId,action.actionName)
    net:HTTPClient():request(url,{
      optiones = {
        method = "POST",
        headers = {
          ["Content-Type"] = "application/json",
        },
        data = json.encode(data)
      },
      success = function(resp) print("success",resp.status) end,
      error = function(err) self:error(err) end,
    })
  end
  
  -- Forwards UI events from HC3 to the emulator
  function quickApp:UIHandler(ev) 
    --send({type='ui',deviceId=self.id,value=ev}) 
    local data = { 
      deviceID = ev.deviceId or ev.deviceID, 
      eventType = ev.eventType,
      elementName = ev.elementName,
      value = ev.value
    }
    net:HTTPClient():request(uiUrl,{
      options = {
        method = "POST",
        headers = {
          ["Content-Type"] = "application/json",
        },
        data = json.encode(data)
      },
      success = function(resp) print("success",resp.status) end,
      error = function(err) self:error(err) end,
    })
  end
  
  -- Override the initChildDevices function to prevent default behavior
  function quickApp:initChildDevices(_) end
  
end
]]

  local uiCallbacks,viewLayout,uiView,_ = Emu:createUI(headers.UI or {})

  local props = {
    apiVersion = "1.3",
    quickAppVariables = headers.vars or {},
    viewLayout = viewLayout,
    uiView = uiView,
    uiCallbacks = uiCallbacks,
    useUiView=false,
    typeTemplateInitialized = true,
  }
  local fqa = {
    apiVersion = "1.3",
    name = name,
    type = headers.type,
    initialProperties = props,
    initialInterfaces = headers.interfaces or {},
    files = {{name="main", isMain=true, isOpen=false, type='lua', content=code}},
  }
  local res,code2 = Emu.lib.uploadFQA(fqa)
  return res
end

-- Creates a proxy device on the HC3 system
-- @param devTempl - The device template containing name, type and other properties
-- @return - The created proxy device or nil if creation failed
local function createProxy(headers) 
  headers.type = headers.type or "com.fibaro.binarySwitch"
  headers.name = headers.name or "myQA"
  local device = deployProxy(headers.name.."_Proxy",headers)
  if not device then return Emu:ERROR("Can't create proxy on HC3") end
  device.id = math.floor(device.id)
  Emu:INFO(fmt("Proxy installed: %s %s",device.id,headers.name))
  device.isProxy = true
  Emu.proxyId = device.id -- Just save the last proxy to be used for restricted API calls
  Emu.api.hc3.post("/devices/"..device.id.."/action/CONNECT",{args={{ip=Emu.lib.IPAddress,port=Emu.lib.webport}}})
  return { device=device, UI=headers.UI, headers=headers }
end

-- Finds and handles existing proxy devices on the HC3 system
-- If multiple proxies with the same name exist, it keeps only the newest one
-- @param d - The device object containing the name to search for
-- @param headers - Headers containing device type information
-- @return - The existing proxy device if found and valid, nil otherwise
local function existingProxy(name,headers)
---@diagnostic disable-next-line: undefined-global
  local proxies = Emu.api.hc3.get("/devices?name="..urlencode(name.."_Proxy")) or {}
  if #proxies == 0 then return end
  table.sort(proxies,function(a,b) return a.id >= b.id end)
  for i = 2,#proxies do                        -- More than 1 proxy, delete older ones
    Emu:DEBUG(fmt("Old Proxy deleted: %s %s",proxies[i].id,proxies[i].name))
    Emu.api.hc3.delete("/devices/"..proxies[i].id)
  end
  local device = proxies[1]
  if proxies[1].type ~= headers.type then      -- Wrong type, delete and create new
    Emu:INFO(fmt("Existing Proxy of wrong type, deleted: %s %s",device.id,device.name))
    Emu.api.hc3.delete("/devices/"..proxies[1].id)
  else
    device.isProxy = true
    Emu:INFO(fmt("Existing Proxy found: %s %s",device.id,device.name))
    local ui = Emu.lib.ui.viewLayout2UI(
      device.properties.viewLayout,
      device.properties.uiCallbacks or {}
    )
    local info = { device=device, UI=ui, headers=headers }
    local children = Emu.api.hc3.get("/devices?parentId="..device.id) or {}
    for _,child in ipairs(children) do
      child.isProxy,child.isChild = true, true
      local ui = Emu.lib.ui.viewLayout2UI(
        child.properties.viewLayout,
        child.properties.uiCallbacks or {}
      )
      local cdev = { device=child, UI=ui, headers=headers }
      Emu:addEmbeds(cdev)
      Emu:registerDevice(cdev)
      Emu:INFO(fmt("Existing Child proxy found: %s %s",child.id,child.name))
    end
    Emu:saveState()
    Emu.proxyId = device.id -- Just save the last proxy to be used for restricted API calls
    Emu.api.hc3.post("/devices/"..device.id.."/action/CONNECT",{args={{ip=Emu.config.IPAddress,port=Emu.config.webport}}})
    return info
  end
end

return {
  createProxy = createProxy,
  existingProxy = existingProxy,
}