
local mobdebug = require("mobdebug")
_PY.mobdebug.on()
local class = require("class")
require("fibaro.json")
local fpath = package.searchpath("fibaro", package.path) or ""
fpath = fpath:sub(1,-(#"fibaro.lua"+1))
local libpath = fpath.."fibaro".._PY.config.fileseparator
local rsrcpath = fpath.."rsrc".._PY.config.fileseparator
local fmt = string.format
local function loadLib(name,...) return loadfile(libpath..name..".lua","t",_G)(...) end
_print = print
local DEVICEID = 5555-1

--@class 'Emulator'
Emulator = {}
class 'Emulator'

function Emulator:__init()
  self.config = _PY.config or {}
  self.config.hc3_url = os.getenv("HC3_URL")
  if self.config.hc3_url and self.config.hc3_url:sub(-1) == '/' then
    self.config.hc3_url = self.config.hc3_url:sub(1, -2)  -- Remove trailing slash
  end
  self.config.hc3_user = os.getenv("HC3_USER")
  self.config.hc3_password = os.getenv("HC3_PASSWORD")
  if self.config.hc3_user and self.config.hc3_password then
    self.config.hc3_creds = _PY.base64_encode(self.config.hc3_user..":"..self.config.hc3_password)
  end
  self.config.IPAddress = _PY.config.host_ip
  self.config.webport = _PY.config.runtime_config.api_config.port
  self.DIR = {}
  self.lib = { 
    loadLib = loadLib,
    openWebBrowser = _PY.open_web_interface_browser,
    fileExist = _PY.fileExist,
    getCwd = _PY.getcwd,
    listDir = _PY.listdir,
    getAvailableColors = _PY.get_available_colors,
    listUserFunctions = _PY.list_user_functions,
    readFile = _PY.readFile,
    writeFile = _PY.writeFile,
    millitime = _PY.millitime,
    base64Encode = _PY.base64_encode,
    base64Decode = _PY.base64_decode,
    mobdebug = _PY.mobdebug,
  }
  self.lib.userTime = os.time
  self.lib.userDate = os.date
  self.offline = false
  
  self.EVENT = {}
  self.debugFlag = false
  
  local api = {}
  function api.get(path) return self:API_CALL("GET", path) end
  function api.post(path, data) return self:API_CALL("POST", path, data) end
  function api.put(path, data) return self:API_CALL("PUT", path, data) end
  function api.delete(path) return self:API_CALL("DELETE", path) end
  self.api = api
  
  local hc3api = {}
  function hc3api.get(path) return self:HC3_CALL("GET", path) end
  function hc3api.post(path, data) return self:HC3_CALL("POST", path, data) end
  function hc3api.put(path, data) return self:HC3_CALL("PUT", path, data) end
  function hc3api.delete(path) return self:HC3_CALL("DELETE", path) end
  self.api.hc3 = hc3api
  
  local restricted = {}
  local function cr(method,path,data)
    if self.offline then
      self:WARNING("api.hc3.restricted: Offline mode")
      return nil,408
    end
    path = path:gsub("^/api/","/")
    local res = self.lib.sendSyncHc3(json.encode({method=method,path=path,data=data}))
    if res == nil then return nil,408 end
    local stat,data = pcall(json.decode,res)
    if stat then
      if data[1] then return data[2],data[3]
      else return nil,501 end
    end
    return nil,501
  end
  function restricted.get(path) return cr('get',path) end
  function restricted.post(path, data) return cr('post',path,data) end
  function restricted.put(path, data) return cr('put',path,data) end
  function restricted.delete(path) return cr('delete',path) end
  self.api.hc3.restricted = restricted

  local orgTime,orgDate,timeOffset = os.time,os.date,0
  
  local function round(x) return math.floor(x+0.5) end
  local function userTime(a) 
    return a == nil and round(_PY.millitime() + timeOffset) or orgTime(a) 
  end
  local function userDate(a, b) 
    return b == nil and orgDate(a, userTime()) or orgDate(a, round(b)) 
  end

  local function getTimeOffset() return timeOffset end
  local function setTimeOffset(offs) timeOffset = offs end
  self.lib.userTime = userTime
  self.lib.userDate = userDate
  function self:setTimeOffset(offs) setTimeOffset(offs) end

  loadLib("utils",self)
  loadLib("fibaro_api",self)
  loadLib("tools",self)
  self.lib.ui = loadLib("ui",self)
end

function Emulator:DEBUG(...) if self.debugFlag then print(...) end end
function Emulator:INFO(...) self.lib.__fibaro_add_debug_message(__TAG, self.lib.logStr(...), "INFO", false) end 
function Emulator:WARNING(...) self.lib.__fibaro_add_debug_message(__TAG, self.lib.logStr(...), "WARNING", false) end 
function Emulator:ERROR(...) self.lib.__fibaro_add_debug_message(__TAG, self.lib.logStr(...), "ERROR", false) end 

function Emulator:registerDevice(info)
  if info.device.id == nil then DEVICEID = DEVICEID + 1; info.device.id = DEVICEID end
  self.DIR[info.device.id] = { 
    device = info.device, files = info.files, env = info.env, headers = info.headers,
    UI = info.UI, UImap = info.UImap, watches = info.watches,
  }
end

function Emulator:getQuickApps()
  local quickApps = {}
  for id, info in pairs(self.DIR) do
    if info.UI then
      quickApps[#quickApps + 1] = { UI = info.UI, device = info.device }
    end
  end
  return quickApps
end

function Emulator:getQuickApp(id)
  local info = self.DIR[id or ""]
  if info then return { UI = info.UI, device = info.device } end
end

function Emulator:saveState() end
function Emulator:loadState() end

local function loadFile(env,path,name,content)
  if not content then
    local file = io.open(path, "r")
    assert(file, "Failed to open file: " .. path)
    content = file:read("*all")
    file:close()
  end
  local func, err = load(content, path, "t", env)
  if func then func() env._G = env return true
  else error(err) end
end

function Emulator:loadResource(fname,parseJson)
  local file = io.open(rsrcpath..fname, "r")
  assert(file, "Failed to open file: " .. fname)
  local content = file:read("*all")
  file:close()
  if parseJson then return json.decode(content) end
  return content
end

local embedUIs = require("fibaro.embedui")

function Emulator:addEmbeds(info)
  local dev = info.device
  local props = dev.properties or {}
  props.uiCallbacks = props.uiCallbacks or {}
  info.UImap = info.UImap or {}
  local embeds = embedUIs.UI[dev.type]
  if embeds then
    for i,v in ipairs(embeds) do
      table.insert(info.UI,i,v)
    end
    for _,cb in ipairs(self.lib.ui.UI2uiCallbacks(embeds) or{}) do
      props.uiCallbacks[#props.uiCallbacks+1] = cb
    end
    self.lib.ui.extendUI(info.UI,info.UImap)
    info.watches = embedUIs.watches[dev.type] or {}
  end
end

function Emulator:createUI(UI) -- Move to ui.lua ? 
  local UImap = self.lib.ui.extendUI(UI)
  local uiCallbacks,viewLayout,uiView
  if UI and #UI > 0 then
    uiCallbacks,viewLayout,uiView = self.lib.ui.compileUI(UI)
  else
    viewLayout = json.decode([[{
        "$jason": {
          "body": {
            "header": {
              "style": { "height": "0" },
              "title": "quickApp_device_57"
            },
            "sections": { "items": [] }
          },
          "head": { "title": "quickApp_device_57" }
        }
      }
  ]])
    viewLayout['$jason']['body']['sections']['items'] = json.initArray({})
    uiView = json.initArray({})
    uiCallbacks = json.initArray({})
  end
  
  return uiCallbacks,viewLayout,uiView,UImap
end

local deviceTypes = nil

function Emulator:createInfoFromContent(filename,content)
  local info = {}
  local preprocessed,headers = self:processHeaders(filename,content)
  local orgUI = table.copy(headers.UI or {})
  if headers.offline and headers.proxy then
    headers.proxy = false
    self:WARNING("Offline mode, proxy disabled")
  end
  if not headers.offline then
    loadLib("helper",self)
    self.lib.startHelper()
  end
  if headers.proxy then
    local proxylib = loadLib("proxy",self)
    info = proxylib.existingProxy(headers.name or "myQA",headers)
    if not info then
      info = proxylib.createProxy(headers)
    else -- Existing proxy, mau need updates
      local proxyupdate = headers.proxyupdate or ""
      local ifs = proxyupdate:match("interfaces")
      local qvars = proxyupdate:match("vars")
      local ui = proxyupdate:match("ui")
      if ifs or qvars or ui then
        local parts = {}
        if ifs then parts.interfaces = headers.interfaces or {} end
        if qvars then parts.props = {quickAppVariables = headers.vars or {}} end
        if ui then parts.UI = orgUI end
        setTimeout(function()
          require("mobdebug").on()
          self.lib.updateQAparts(info.device.id,parts,true)
        end,100)
      end
    end
  end
  
  if not info.device then
    if deviceTypes == nil then deviceTypes = self:loadResource("devices.json",true) end
    headers.type = headers.type or 'com.fibaro.binarySwitch'
    local dev = deviceTypes[headers.type]
    assert(dev,"Unknown device type: "..headers.type)
    dev = table.copy(dev)
    if not headers.id then DEVICEID = DEVICEID + 1 end
    dev.id = headers.id or DEVICEID
    dev.name = headers.name or "MyQA"
    dev.enabled = true
    dev.visible = true
    info.device = dev
    dev.interfaces = headers.interfaces or {}
  end
  
  local dev = info.device
  info.files = headers.files or {}
  local props = dev.properties or {}
  props.quickAppVariables = headers.vars or {}
  props.quickAppUuid = headers.uid
  props.manufacturer = headers.manufacturer
  props.model = headers.model
  props.role = headers.role
  props.description = headers.description
  props.uiCallbacks,props.viewLayout,props.uiView,info.UImap = self:createUI(headers.UI or {})
  info.files.main = { path=filename, content=preprocessed }
  local specProps = {
    uid='quickAppUuid',manufacturer='manufacturer',
    mode='model',role='deviceRole',
    description='userDescription'
  }
  props.uiCallbacks = props.uiCallbacks or {}
  local embeds = embedUIs.UI[headers.type]
  if embeds then
    for i,v in ipairs(embeds) do
      table.insert(headers.UI,i,v)
    end
    for _,cb in ipairs(self.lib.ui.UI2uiCallbacks(embeds) or{}) do
      props.uiCallbacks[#props.uiCallbacks+1] = cb
    end
    self.lib.ui.extendUI(headers.UI,info.UImap)
    info.watches = embedUIs.watches[headers.type] or {}
  end
  info.UI = headers.UI
  for _,prop in ipairs(specProps) do
    if headers[prop] then props[prop] = headers[prop] end
  end
  info.headers = headers
  return info
end

function Emulator:createInfoFromFile(filename)
  -- Read the file content
  local file = io.open(filename, "r")
  assert(file, "Failed to open file: " .. filename)
  local content = file:read("*all")
  file:close()
  return self:createInfoFromContent(filename,content)
end

function Emulator:createChild(data)
  local info = { UI = {}, headers = {} }
  if deviceTypes == nil then deviceTypes = self:loadResource(rsrcpath.."devices.json",true) end
  local typ = data.type or 'com.fibaro.binarySwitch'
  local dev = deviceTypes[typ]
  assert(dev,"Unknown device type: "..typ)
  dev = table.copy(dev)
  DEVICEID = DEVICEID + 1
  dev.id = DEVICEID
  dev.parentId = data.parentId
  dev.name = data.name or "MyChild"
  dev.enabled = true
  dev.visible = true
  dev.isChild = true
  info.device = dev
  local props = dev.properties or {}
  if data.initialProperties and data.initialProperties.uiView then
    local uiView = data.initialProperties.uiView
    local callbacks = data.initialProperties.uiCallbacks or {}
    info.UI = self.lib.ui.uiView2UI(uiView,callbacks)
  end
  props.uiCallbacks,props.viewLayout,props.uiView,info.UImap = self:createUI(info.UI or {})
  self:addEmbeds(info)
  info.env = self.DIR[dev.parentId].env
  info.device = dev
  self:registerDevice(info)
  return dev
end

function Emulator:saveQA(fname,id)
  local info = self.DIR[id]
  local fqa = self.lib.getFQA(id)
  self.lib.writeFile(fname,json.encode(fqa))
  self:INFO("Saved QA to",fname)
end

function Emulator:installQuickAppFile(path)
  local file = io.open(path, "r")
  assert(file, "Failed to open file: " .. path)
  local content = file:read("*all")
  file:close()
  local info = self:createInfoFromContent(path,content)
  self:loadQA(info)
  self:registerDevice(info)
  self:startQA(info.device.id)
  return info
end

function Emulator:loadMainFile(filename)
  local info = self:createInfoFromFile(filename)
  if info.headers.debug then self.debugFlag = true end
  if _PY.config.debug == true then self.debugFlag = true end
  
  if info.headers.offline then
    self.offline = true
    self:DEBUG("Offline mode")
  end
  
  if info.headers.offline then
    -- If main files has offline directive, setup offline routes
    loadLib("offline",self)
    self.lib.setupOfflineRoutes()
  end
  
  if info.headers.time then 
    local timeOffset = info.headers.time
    if type(timeOffset) == "string" then
      timeOffset = self.lib.parseTime(timeOffset)
      self:setTimeOffset(timeOffset-os.time())
      self:DEBUG("Time offset set to", self.lib.userDate("%c"))
    end
  end

  self:loadQA(info)
  
  self:registerDevice(info)
  
  self:startQA(info.device.id)
end

local stdLua = { 
  "string", "table", "math", "os", "io", 
  "package", "coroutine", "debug", "require",
  "setTimeout", "clearTimeout", "setInterval", "clearInterval",
  "setmetatable", "getmetatable", "rawget", "rawset", "rawlen",
  "next", "pairs", "ipairs", "type", "tonumber", "tostring", "pcall", "xpcall",
  "error", "assert", "select", "unpack", "load", "loadstring", "loadfile", "dofile",
  "print",
}

function Emulator:loadQA(info)
  -- Load and execute included files + main file
  local env = { 
    fibaro = { plua = self }, net = net, json = json, api = self.api,
      os = { time = self.lib.userTime, date = self.lib.userDate, getenv = os.getenv, clock = os.clock, difftime = os.difftime },
      __fibaro_add_debug_message = self.lib.__fibaro_add_debug_message, _PY = _PY,
    }
  for _,name in ipairs(stdLua) do env[name] = _G[name] end
  
  info.env = env
  env._G = env
  env._ENV = env
  loadfile(libpath.."fibaro_funs.lua","t",env)()
  loadfile(libpath.."quickapp.lua","t",env)()
  env.__TAG = info.device.name:upper()..info.device.id
  env.plugin.mainDeviceId = info.device.id
  for name,f in pairs(info.files) do
    if name ~= 'main' then loadFile(env,f.path,name,f.content) end
  end
  if info.headers.breakOnLoad then
    local firstLine,onInitLine = self.lib.findFirstLine(info.files.main.content)
    if firstLine then self.lib.mobdebug.setbreakpoint(info.files.main.path,firstLine) end
  end
  loadFile(env,info.files.main.path,'main',info.files.main.content)
end

local function validate(str,typ,key)
  local stat,val = pcall(function() return load("return "..str)() end)
  if not stat then error(fmt("Invalid header %s: %s",key,str)) end
  if typ and type(val) ~= typ then 
    error(fmt("Invalid header %s: expected %s, got %s",key,typ,type(val)))
  end
  return val
end

function Emulator:startQA(id)
  local info = self.DIR[id]
  if info.headers.save then self:saveQA(info.headers.save ,id) end
  if info.headers.project then self.lib.saveProject(id,info,nil) end
  local env = info.env
  local function func()
    if env.QuickApp and env.QuickApp.onInit then
      env.quickApp = env.QuickApp(info.device)
    end
  end

  env.setTimeout(function()
    coroutine.wrapdebug(func, function(err,tb)
      err = err:match(":(%d+: .*)")
      print("Error in QA " .. id .. ": " .. tostring(err))
      print(tb)
    end)() 
  end, 200)
end

local viewProps = {}
function viewProps.text(elm,data) elm.text = data.newValue end
function viewProps.value(elm,data) elm.value = data.newValue end
function viewProps.options(elm,data) elm.options = data.newValue end
function viewProps.selectedItems(elm,data) elm.values = data.newValue end
function viewProps.selectedItem(elm,data) elm.value = data.newValue end

function Emulator:updateView(id,data,noUpdate)
  local info = self.DIR[id]
  local elm = info.UImap[data.componentName or ""]
  if elm then
    if viewProps[data.propertyName] then
      viewProps[data.propertyName](elm,data)
      --print("broadcast_ui_update",data.componentName)
      if not noUpdate then 
        -- Send granular UI update with specific element data (if function available)
        if _PY.broadcast_view_update then
          _PY.broadcast_view_update(id, data.componentName, data.propertyName, data.newValue)
        end
      end
    else
      self:DEBUG("Unknown view property: " .. data.propertyName)
    end
  end
end

function Emulator:HC3_CALL(method, path, data)
  assert(self.config.hc3_creds, "HC3 credentials are not set")
  local url = self.config.hc3_url.."/api"..path
  if type(data) == 'table' then data = json.encode(data) end
  local res = _PY.http_call_sync(
  method, 
  url,
  data,
  {
    ["User-Agent"] = "plua/0.1.0",
    ["Content-Type"] = "application/json",
    ["Authorization"] = "Basic " .. (self.config.hc3_creds or ""),
  }
)

if res.success then
  if tonumber(res.status_code) and res.status_code >= 200 and res.status_code < 300 then
    local data = nil
    _,data = pcall(json.decode, res.data)
    return data, res.status_code
  end
end
return nil, res.status_code, res.error_message
end

function Emulator:API_CALL(method, path, data)
  self:DEBUG("fibaroapi called:", method, path, data and json.encodeFast(data) // 100)
  
  -- Try to get route from router
  local handler, vars, query = self.lib.router:getRoute(method, path)
  if handler then
    local response_data, status_code = handler(path, data, vars, query)
    
    if status_code ~= 301 then 
      return response_data, status_code
    end
  end
  
  if not self.offline then
    -- Handle redirect by making the actual HTTP request to external server
    return self:HC3_CALL(method, path, data)
  end
  
  return nil, self.lib.router.HTTP.NOT_IMPLEMENTED
end

local pollStarted = false
function Emulator:startRefreshStatesPolling()
  if not (self.offline or pollStarted) then
    pollStarted = true
    local result = _PY.pollRefreshStates(0,self.config.hc3_url.."/api/refreshStates?last=", {
      headers = {Authorization = "Basic " .. self.config.hc3_creds}
    })
  end
end

function Emulator:getRefreshStates(last) return _PY.getEvents(last) end

function Emulator:refreshEvent(typ,data) _PY.addEvent(json.encode({type=typ,data=data})) end

local headerKeys = {}
function headerKeys.name(str,info) info.name = str end
function headerKeys.type(str,info) info.type = str end
function headerKeys.state(str,info) info.state = str end
function headerKeys.proxy(str,info,k) info.proxy = validate(str,"boolean",k) end
function headerKeys.proxy_port(str,info,k) info.proxy_port = validate(str,"number",k) end
function headerKeys.offline(str,info,k) info.offline = validate(str,"boolean",k) end
function headerKeys.time(str,info,k) info.time = str end
function headerKeys.uid(str,info,k) info.version =str end
function headerKeys.manufacturer(str,info) info.manufacturer = str end
function headerKeys.model(str,info) info.model = str end
function headerKeys.role(str,info) info.role = str end
function headerKeys.description(str,info) info.description = str end
function headerKeys.latitude(str,info,k) info.latitude = validate(str,"number",k) end
function headerKeys.longitude(str,info,k) info.longitude = validate(str,"number",k) end
function headerKeys.debug(str,info,k) info.debug = validate(str,"boolean",k) end
function headerKeys.save(str,info) info.save = str end
function headerKeys.proxyupdate(str,info) info.proxyupdate = str end
function headerKeys.project(str,info,k) info.project = validate(str,"number",k) end
function headerKeys.nop(str,info,k) validate(str,"boolean",k) end
function headerKeys.interfaces(str,info,k) info.interfaces = validate(str,"table",k) end
function headerKeys.breakonload(str,info,k) info.breakOnLoad = validate(str,"boolean",k) end
function headerKeys.var(str,info,k) 
  local name,value = str:match("^([%w_]+)%s*=%s*(.+)$")
  assert(name,"Invalid var header: "..str)
  info.vars[#info.vars+1] = {name=name,value=validate(value,nil,k)}
end
function headerKeys.u(str,info) info._UI[#info._UI+1] = str end
function headerKeys.file(str,info)
  local path,name = str:match("^([^,]+),(.+)$")
  assert(path,"Invalid file header: "..str)
  if path:sub(1,1) == '$' then
    local lpath = package.searchpath(path:sub(2),package.path)
    if _PY.fileExist(lpath) then path = lpath
    else error(fmt("Library not found: '%s'",path)) end
  end
  if _PY.fileExist(path) then
    info.files[name] = {path = path, content = nil }
  else
    error(fmt("File not found: '%s'",path))
  end
end

local function compatHeaders(code)
  code = code:gsub("%-%-%%%%([%w_]+)=([^\n\r]+)",function(key,str) 
    if key == 'var' then
      str = str:gsub(":","=")
    elseif key == 'debug' then
      str = "true"
    elseif key == 'conceal' then
      str = str:gsub(":","=")
    elseif key == 'webui' then
      key,str = "nop","true"
    end
    return fmt("--%%%%%s:%s",key,str)
  end)
  return code
end

function Emulator:processHeaders(filename,content)
  local shortname = filename:match("([^/\\]+%.lua)")
  local name = shortname:match("(.+)%.lua")
  local headers = {
    name=name or "MyQA",
    type='com.fibaro.binarySwitch',
    files={},
    vars={},
    _UI={},
  }
  local code = "\n"..content
  local eod = code:find("\n%-[%-]+ENDOFHEADERS") -- Embedded headers
  if eod then code = code:sub(1,eod-1) end

  if code:match("%-%-%%%%name=") then code = compatHeaders(code) end
  code:gsub("\n%-%-%%%%([%w_]-):([^\n]*)",function(key,str) 
    str = str:match("^%s*(.-)%s*$") or str
    str = str:match("^(.*)%s* %-%- (.*)$") or str
    if headerKeys[key] then
      headerKeys[key](str,headers,key)
    else print(fmt("Unknown header key: '%s' - ignoring",key)) end 
  end)
  local UI = (nil or {}).UI or {} -- ToDo: extraHeaders
  for _,v in ipairs(headers._UI) do 
    local v0 = validate(v,"table","u")
    UI[#UI+1] = v0
    v0 = v0[1] and v0 or { v0 }
    for _,v1 in ipairs(v0) do
      --local ok,err = Type.UIelement(v1)
      --assert(ok, fmt("Bad UI element: %s - %s",v1,err))
    end
  end
  headers.UI = UI
  headers._UI = nil
  return content,headers
end

return Emulator