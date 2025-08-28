
local mobdebug = require("mobdebug")
_PY.mobdebug.on()
local class = require("class")
json = require("json")
require("json")
local fpath = package.searchpath("fibaro", package.path) or ""
fpath = fpath:sub(1,-(#"fibaro.lua"+1))
local libpath = fpath.."fibaro".._PY.config.fileSeparator
local rsrcpath = fpath.."rsrc".._PY.config.fileSeparator
local fmt = string.format
local function loadLib(name,...) return loadfile(libpath..name..".lua","t",_G)(...) end
_print = print
local pluaConf = {}
local DEVICEID = 5555-1
local lfs = require("lfs")

local function loadLuaFile(filename)
  if not _PY.file_exists(filename) then return {} end
  if _PY.is_directory(filename) then return {} end
  local f, err = loadfile(filename, "t", _G)
  if not f then error(fmt("Failed to load %s: %s",filename,err)) end
  local stat,res = pcall(f)
  if not stat then  error(fmt("Error in %s: %s",filename,res)) end
  if type(res) ~= "table" then
    error(fmt("Invalid config file %s: expected table, got %s",filename,type(res)))
  end
  return res
end

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
  if not lfs.attributes(self.config.tempdir) then
    lfs.mkdir(self.config.tempdir)
  end
  self.config.IPAddress = _PY.config.host_ip
  self.config.headers = _PY.python_2_lua_table(_PY.config.headers)
  if _PY.config.webport then
    self.config.webport = _PY.config.webport
  else
    self.config.webport = 8080  -- Default port if not set
  end
  self.offline = _PY.config.offline or false
  self.DIR = {}
  self.lib = { 
    loadLib = loadLib,
    log = loadLib("log",self),
    readFile = _PY.fread_file,
    writeFile = _PY.fwrite_file,
    millitime = _PY.milli_time,
    base64Encode = _PY.base64_encode,
    base64Decode = _PY.base64_decode,
    mobdebug = _PY.mobdebug,
    utime = _PY.utime,
  }
  self.lib.userTime = os.time
  self.lib.userDate = os.date
  
  self.EVENT = {}
  setmetatable(self.EVENT, { __newindex = function(t,k,v) rawset(t,k, t[k] or {}) table.insert(t[k],v) end })
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
    return a == nil and round(_PY.milli_time() + timeOffset) or orgTime(a) 
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
  
  local localPluaConf = loadLuaFile(_PY.config.cwd.._PY.config.fileSeparator..".plua")
  local homePluaConf =loadLuaFile(_PY.config.homedir.._PY.config.fileSeparator..".plua/config.lua")
  pluaConf = table.merge(homePluaConf,localPluaConf)
end

function Emulator:post(event)
  local typ = event.type
  local styp = "_"..typ
  for _,f in ipairs(self.EVENT[styp] or {}) do f(event,self) end
  setTimeout(function()
    for _,f in ipairs(self.EVENT[typ] or {}) do f(event,self) end
  end,0)
end

function Emulator:DEBUG(...) if self.debugFlag then print(...) end end
function Emulator:INFO(...) self.lib.__fibaro_add_debug_message(__TAG, self.lib.logStr(...), "INFO", false) end 
function Emulator:WARNING(...) self.lib.__fibaro_add_debug_message(__TAG, self.lib.logStr(...), "WARNING", false) end 
function Emulator:ERROR(...) self.lib.__fibaro_add_debug_message(__TAG, self.lib.logStr(...), "ERROR", false) end 

function Emulator:registerDevice(info)
  if info.device.id == nil then DEVICEID = DEVICEID + 1; info.device.id = DEVICEID end
  self:DEBUG("Registering device with ID: " .. tostring(info.device.id))
  self.DIR[info.device.id] = { 
    device = info.device, files = info.files, env = info.env, headers = info.headers,
    UI = info.UI, UImap = info.UImap, watches = info.watches,
  }
  self:DEBUG("Device registered. Total devices in DIR: " .. table.maxn(self.DIR))
end

local gbgcolor = os.getenv("PLUA_QA_COLOR") or "lightgrey"

local tileX, tileY = 20,20
function Emulator:registerQAGlobally(qa) -- QuickApp object (mother or child)
  _G["QA"..qa.id] = qa
  local info = self.DIR[qa.id]
  if info.restarted then return end
  local bgcolor = info.headers.qacolor or gbgcolor
  local openWindow = self.config.desktop
  if openWindow == nil then openWindow = info.headers and info.headers.desktop end
  if openWindow then
    local dim = self.lib.getScreenDimension()
    local success = self.lib.createQuickAppWindow(qa.id, "Auto-opened Desktop Window", 400, 400, tileX, tileY, bgcolor)
    if success then
      tileX = tileX + 400 + 10
    end
  end
end

function Emulator:getQuickApps()
  local quickApps = {}
  for id, info in pairs(self.DIR) do
    self:DEBUG("  ID: " .. tostring(id) .. ", has UI: " .. tostring(info.UI ~= nil))
    if info.UI then
      quickApps[#quickApps + 1] = { UI = info.UI, device = info.device }
    end
  end
  return quickApps
end

function Emulator:getQuickApp(id)
  id = tonumber(id)
  self:DEBUG("Looking for QuickApp with ID: " .. tostring(id))
  local info = self.DIR[id or ""]
  if info then 
    self:DEBUG("Found QuickApp with ID " .. tostring(id))
    return { UI = info.UI, device = info.device }
  else
    self:DEBUG("QuickApp with ID " .. tostring(id) .. " not found in DIR")
    -- List available IDs for debugging
    local available = {}
    for did, _ in pairs(self.DIR) do
      available[#available + 1] = tostring(did)
    end
    self:DEBUG("Available IDs: " .. table.concat(available, ", "))
    return nil
  end
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
  local path = rsrcpath..fname
  local file = io.open(path)
  assert(file, "Failed to open file: " .. path)
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
local proxylib = nil

function Emulator:createInfoFromContent(filename,content,extraHeaders)
  local info = {}
  local preprocessed,headers = self:processHeaders(filename,content,extraHeaders)
  local orgUI = table.copy(headers.UI or {})
  if self.offline then headers.offline = true end
  
  if headers.offline and headers.proxy then
    headers.proxy = false
    self:WARNING("Offline mode, proxy disabled")
  end
  if headers.noproxy then headers.proxy = false end
  if not headers.offline then
    if not self.lib.startHelper then loadLib("helper",self) end
    self.lib.startHelper()
  end
  if headers.proxy then
    if proxylib == nil then proxylib = loadLib("proxy",self) end
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

function Emulator:createInfoFromFile(filename,extraHeaders)
  -- Read the file content
  if filename:match("%.fqa$") then
    -- If it's a FQA file, Unpack andload it as a QuickApp
    local path = self.config.tempdir..self.lib.createTempName(".lua")
    local content = self.lib.readFile(filename)
    local _,fqa = pcall(json.decode, content)
    assert(fqa, "Failed to decode FQA file: " .. filename)
    self.lib.unpackFQAAux(nil, fqa, path)
    filename = path
  end
  local file = io.open(filename, "r")
  assert(file, "Failed to open file: " .. filename)
  local content = file:read("*all")
  file:close()
  return self:createInfoFromContent(filename,content,extraHeaders)
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
  local parentInfo = self.DIR[data.parentId]
  info.headers.desktop = parentInfo.headers.desktop
  info.env = parentInfo.env
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

function Emulator:installQuickAppFile(path,options)
  options = options or {}
  local extraHeaders = options.headers or {}
  local file = io.open(path, "r")
  assert(file, "Failed to open file: " .. path)
  local content = file:read("*all")
  file:close()
  local info = self:createInfoFromContent(path,content,extraHeaders)
  self:loadQA(info,options.env or {})
  self:registerDevice(info)
  self:startQA(info.device.id)
  return info
end

function Emulator:loadMainFile(filenames,greet)
  local filename = filenames[1] -- our main file
  local extraHeaders = self.config.headers
  local info = self:createInfoFromFile(filename,extraHeaders)
  if _PY.config.debug == true then self.debugFlag = true end
  if info.headers.debug then self.debugFlag = true end
  
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
  
  if greet and not _PY.config.nogreet then
    local color = _PY.config.environment == 'zerobrane' and "yellow" or "orange"
    _print(self.lib.log.colorStr(color,fmt("Fibaro SDK, %s, (%.4fs)",
    self.offline and "offline" or "online",
    self.lib.millitime()-self.config.startTime)
  )
)
end

self:loadQA(info)

self:registerDevice(info)

self:startQA(info.device.id)
for i=2, #filenames do self.lib.loadQA(filenames[i]) end
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

function Emulator:loadQA(info,envAdds)
  -- Load and execute included files + main file
  envAdds = envAdds or {}
  local env = { 
    fibaro = { plua = self }, net = net, json = json, api = self.api, 
    os = { time = self.lib.userTime, date = self.lib.userDate, getenv = os.getenv, clock = os.clock, difftime = os.difftime },
    __fibaro_add_debug_message = self.lib.__fibaro_add_debug_message, _PY = _PY,
  }
  for _,name in ipairs(stdLua) do env[name] = _G[name] end
  for k,v in pairs(envAdds) do env[k] = v end
  
  info.env = env
  env._G = env
  env._ENV = env
  env.type = function(e) local t = type(e) return t == "table" and e.__USERDATA and "userdata" or t end
  loadfile(libpath.."fibaro_funs.lua","t",env)()
  local ff,erf = loadfile(libpath.."quickapp.lua","t",env)
  if ff then ff()
  else 
    error(erf) 
  end
  env.__TAG = info.device.name:upper()..info.device.id
  env.plugin.mainDeviceId = info.device.id
  self:post({ type = "qaEnvSetup", info = info})
  local fileEntries = {}
  local n = 0; for _,_ in pairs(info.files) do n=n+1 end
  for name,f in pairs(info.files) do fileEntries[f.order or n] = f; f.name = name end
  for _,f in ipairs(fileEntries) do
    if f.name ~= 'main' then loadFile(env,f.path,f.name,f.content) end
  end
  if info.headers.breakOnLoad then
    local firstLine,onInitLine = self.lib.findFirstLine(info.files.main.content)
    if firstLine then self.lib.mobdebug.setbreakpoint(info.files.main.path,firstLine) end
  end
  loadFile(env,info.files.main.path,'main',info.files.main.content)
end

function Emulator:restartQA(id)
  self:INFO("Restarting QA",id,"in 3sec")
  setTimeout(function() 
    local info = self.DIR[id]
    info.restarted = true
    self:loadQA(info)
    self:startQA(info.device.id)
  end,3*1000)
end

local venv = setmetatable({}, { __index = function(t,k) return os.getenv(k) end })
local function validate(str,typ,key)
  local stat,val = pcall(function() return load("return "..str, nil, "t", {env = venv, plua = pluaConf, config = pluaConf})() end)
  if not stat then error(fmt("Invalid header %s: %s",key,str)) end
  if typ and type(val) ~= typ then 
    error(fmt("Invalid header %s: expected %s, got %s",key,typ,type(val)))
  end
  return val
end

function Emulator:startQA(id)
  local info = self.DIR[id]
  if info.headers.save then self:saveQA(info.headers.save ,id) end
  if info.headers.project then self.lib.saveProject(info.headers.project,info,nil) end
  local env = info.env
  local function func()
    if env.QuickApp and env.QuickApp.onInit then
      env.quickApp = env.QuickApp(info.device)
    end
  end
  
  --env.setTimeout(function()
  coroutine.wraptest = coroutine.wraptest
  if coroutine.wraptest then return coroutine.wraptest(func,info) end
  coroutine.wrapdebug(func, function(err,tb)
    err = err:match(":(%d+: .*)")
    print("Error in QA " .. id .. ": " .. tostring(err))
    print(tb)
  end)() 
  --end, 0)
end

local viewProps = {}
function viewProps.text(elm,data) elm.text = data.newValue end
function viewProps.value(elm,data) elm.value = data.newValue end
function viewProps.options(elm,data) elm.options = data.newValue end
function viewProps.selectedItems(elm,data) elm.values = data.newValue end
function viewProps.selectedItem(elm,data) elm.value = data.newValue end

function Emulator:updateView(id,data,noUpdate)
  -- print("🔍 DEBUG: updateView called with:")
  -- print("  id:", id)
  -- print("  data:", json.encodeFast(data))
  -- print("  noUpdate:", noUpdate)
  
  local info = self.DIR[id]
  local elm = info.UImap[data.componentName or ""]
  if elm then
    if viewProps[data.propertyName] then
      viewProps[data.propertyName](elm,data)
      if not noUpdate then 
        if _PY.broadcast_view_update then
          local success = _PY.broadcast_view_update(id, data.componentName, data.propertyName, data.newValue)
        else
        end
      else
      end
    else
      self:DEBUG("Unknown view property: " .. data.propertyName)
    end
  else
    print("  ❌ UI element not found:", data.componentName)
    print("  Available elements:")
    for name, _ in pairs(info.UImap or {}) do
      print("    -", name)
    end
  end
end

function Emulator:HC3_CALL(method, path, data)
  if not self.config.hc3_creds then
    self:ERROR("HC3 credentials are not set")
    self:INFO("Setup an .env or ~/.env file with HC3 credentials")
    self:INFO("Please see https://github.com/jangabrielsson/plua/blob/main/README.md for instructions")
    os.exit()
  end
  
  local function makeRequest()
    local url = self.config.hc3_url.."/api"..path
    if type(data) == 'table' then data = json.encode(data) end
    return _PY.http_request_sync({
      method = method, 
      url = url,
      data = data,
      headers = {
        ['X-Fibaro-Version'] = '2',
        ['Accept-language'] = 'en',
        ["User-Agent"] = "plua/0.1.0",
        ["Content-Type"] = "application/json",
        ["Authorization"] = "Basic " .. (self.config.hc3_creds or ""),
      }
    })
  end
  
  -- First attempt
  local res = makeRequest()
  
  -- If request failed with connection error, try to wake the device
  if res.error and (res.error:find("Connection") or res.error:find("timeout") or res.error:find("refused")) then
    self:DEBUG("Connection failed, attempting to wake HC3 device...")
    
    -- Extract hostname/IP from HC3 URL
    local host = self.config.hc3_url:match("https?://([^:/]+)")
    if host and _PY.wake_network_device then
      local wakeResult = _PY.wake_network_device(host, 3.0)
      if wakeResult then
        self:DEBUG("Wake attempt successful, retrying HC3 call...")
        -- Wait a moment for the device to fully wake up
        _PY.py_sleep(1000) -- 1 second
        -- Retry the request
        res = makeRequest()
      else
        self:DEBUG("Wake attempt failed or device didn't respond")
      end
    end
  end
  
  if res.ok then
    if tonumber(res.status) and res.status >= 200 and res.status < 300 then
      return res.json, res.status
    end
  end
  if res.status == 401 or res.status == 403  then
    self:ERROR("HC3 Authentication failed: " .. res.status.." ".. (res.status_text or ""))
    self:INFO("Please check your HC3 credentials in the .env or ~/.env file") 
    self.INFO("Terminating emulator due to authentication failure, and to avoid lock out of HC3")
    os.exit()
  end
  if res.error and not (res.status and res.json) then
    self:ERROR("HC3 call failed: " .. res.error)
    self:INFO("Please check your HC3 connection")
    os.exit()
  end
  return nil, res.status, res.status_text
end

function Emulator:API_CALL(method, path, data)
  self:DEBUG(method, path, data and json.encodeFast(data) // 100)
  
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

function Emulator:refreshEvent(typ,data) 
  setTimeout(function() _PY.addEventFromLua(json.encode({type=typ,data=data})) end, 0)
end

local headerKeys = {}
function headerKeys.name(str,info) info.name = str end
function headerKeys.type(str,info) info.type = str end
function headerKeys.state(str,info) info.state = str end
function headerKeys.proxy(str,info,k) info.proxy = validate(str,"boolean",k) end
function headerKeys.proxy_port(str,info,k) info.proxy_port = validate(str,"number",k) end
function headerKeys.offline(str,info,k) info.offline = validate(str,"boolean",k) end
function headerKeys.time(str,info,k) info.time = str end
function headerKeys.uid(str,info,k) info.uid = str end
function headerKeys.manufacturer(str,info) info.manufacturer = str end
function headerKeys.model(str,info) info.model = str end
function headerKeys.role(str,info) info.role = str end
function headerKeys.description(str,info) 
  if str:sub(1,1) == '"' and str:sub(-1) == '"' then
    str = str:sub(2,-2) -- Remove quotes
  end
  info.description = str
end
function headerKeys.latitude(str,info,k) info.latitude = validate(str,"number",k) end
function headerKeys.qacolor(str,info,k) info.qacolor = str end
function headerKeys.longitude(str,info,k) info.longitude = validate(str,"number",k) end
function headerKeys.debug(str,info,k) info.debug = validate(str,"boolean",k) end
function headerKeys.save(str,info) info.save = str end
function headerKeys.desktop(str,info) info.desktop = validate(str,"boolean") end
function headerKeys.proxyupdate(str,info) info.proxyupdate = str end
function headerKeys.project(str,info,k) info.project = validate(str,"number",k) end
function headerKeys.nop(str,info,k) validate(str,"boolean",k) end
function headerKeys.norun(str,info,k) end
function headerKeys.noproxy(str,info,k) info.noproxy = validate(str,"boolean",k) end
function headerKeys.interfaces(str,info,k) info.interfaces = validate(str,"table",k) end
function headerKeys.breakonload(str,info,k) info.breakOnLoad = validate(str,"boolean",k) end
function headerKeys.headers(str,info,k) info.include = str end
function headerKeys.var(str,info,k) 
  local name,value = str:match("^([%w_]+)%s*=%s*(.+)$")
  assert(name,"Invalid var header: "..str)
  info.vars[#info.vars+1] = {name=name,value=validate(value,nil,k)}
end
function headerKeys.u(str,info) info._UI[#info._UI+1] = str end
local fileOrder = 1
function headerKeys.file(str,info)
  local path,name = str:match("^([^,]+),(.+)$")
  if path == nil then path,name = str:match("^([^:]+):(.+)$") end
  assert(path,"Invalid file header: "..str)
  if path:sub(1,1) == '$' then
    local lpath = package.searchpath(path:sub(2),package.path)
    if _PY.file_exists(lpath) then path = lpath
    else error(fmt("Library not found: '%s'",path)) end
  elseif path:sub(1,1) == '%' then
    path = info.path..path:sub(2) -- Relative to the QA path
  end
  if _PY.file_exists(path) then
    local seen = info.files[name] ~= nil
    assert( not seen, fmt("File '%s' already exists in QA",name) )
    info.files[name] = {path = path, content = nil, order = fileOrder } 
    fileOrder = fileOrder + 1
  else
    error(fmt("--%%file: File not found: '%s'",path))
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

function Emulator:processHeaders(filename,content,extraHeaders)
  local shortname = filename:match("([^/\\]+%.lua)") or filename
  local path = filename:sub(1,-(#shortname+1))
  local name = shortname:match("(.+)%.lua")
  local headers = {
    name=name or "MyQA",
    type='com.fibaro.binarySwitch',
    files={},
    vars={},
    _UI={},
    path = path or ""
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
  extraHeaders = extraHeaders or {}
  if headers.include then
    assert(_PY.file_exists(headers.include),"file doesn't exist")
    local f = io.open(headers.include)
    assert(f,"Failed to open include file: "..headers.include)
    for line in f:lines() do
      line = line and line:match("%-%-%%%%(.*)") or line
      extraHeaders[#extraHeaders+1] = line
    end
    f:close()
  end
  for _,h in ipairs(extraHeaders) do
    local key,str = h:match("^%s*([%w_]+):%s*(.*)$")
    if headerKeys[key] then
      headerKeys[key](str,headers,key)
    else print(fmt("Unknown header key: '%s' - ignoring",key)) end 
  end
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

local function getFQA(self,fname,extraHeaders)
  local info = self:createInfoFromFile(fname,extraHeaders)
  self:registerDevice(info)
  return self.lib.getFQA(info.device.id)
end

local tools = {
  uploadQA = {
    sort = 1,
    doc = "Upload QuickApp to HC3",
    usage = ">plua -t uploadQA <filename>",
    fun = function(self,file)
      file = tostring(file)
      assert(_PY.file_exists(file),"File don't exist:"..tostring(file))
      self:INFO("Uploading QA",file)
      local fqa = getFQA(self,file,{"noproxy:true"})
      local dev,code = self.lib.uploadFQA(fqa)
      if dev then
      else
        self:ERROR("Upload failed",code)
      end
    end
  },
  updateFile = {
    sort = 3,
    doc = "Update QuickApp file on QA on HC3, need to have .project file",
    usage = ">plua -t updateFile <filename>",
    fun = function(self,file)
      file = tostring(file)
      assert(_PY.file_exists(file),"File don't exist:"..tostring(file))
      self.lib.updateFile(file) 
      self:INFO("Updated file",file)
    end
  },
  updateQA = {
    sort = 4,
    doc = "Update QuickApp on HC3, need to have .project file",
    usage = ">plua -t updateQA <filename>",
    fun = function(self,file)
      file = tostring(file)
      assert(_PY.file_exists(file),"File don't exist:"..tostring(file))
      self.lib.updateQA(file)
      self:INFO("Updated QA",file)
    end
  },
  downloadQA = {
    sort = 2,
    doc = "Download QuickApp from HC3 and unpack it to lua files",
    usage = ">plua -t downloadQA <id> [<dest dir>]",
    fun = function(self,id,path)
      id = tonumber(id)
      path = path or "./"
      path = path:sub(#path) == "/" and path or path.."/"
      assert(_PY.file_exists(path),"path must exist")
      assert(id,"id must be number")
      self:INFO("Downloading QA",id,"to",path)
      local name = self.lib.downloadFQA(id,path)
      self:INFO("Downloaded QA",name)
    end
  },
  pack = {
    sort = 5,
    doc = "Pack lua QuickApp file into a .fqa file",
    usage = ">plua -t pack <qa filename> [<fqa filename>]",
    fun = function(self,file,name)
      assert(_PY.file_exists(file),"file doesn't exist")
      if not name then name = file:gsub("%.lua$","")..".fqa" end
      local code = self.lib.readFile(file)
      local fqa = self.lib.luaToFQA(code)
      self.lib.writeFile(name,json.encodeFast(fqa))
      self:INFO("Packed QA",file,"to",name)
    end
  },
  unpack = {
    sort = 6,
    doc = "Unpack fqa file to lua files",
    usage = ">plua -t unpack <fqa filename> [<dest dir>]",
    fun = function(self,file,path)
      path = path or "./"
      path = path:sub(#path) == "/" and path or path.."/"
      assert(_PY.file_exists(path),"path must exist")
      assert(_PY.file_exists(file),"file doesn't exist")
      local fqa = self.lib.readFile(file)
      fqa = json.decode(fqa)
      local r = self.lib.unpackFQAAux(nil,fqa,path)
      self:INFO("Unpacked QA",file,"to",r)
    end
  }
}

local function loadExtraTools()
  local n = 0; for _,_ in pairs(tools) do n=n+1 end
  local lfs = require("lfs")
  local toolsPath = libpath.."tools/"
  for file in lfs.dir(toolsPath) do
    if file ~= "." and file ~= ".." then
      if file:match("%.lua$") then
        local toolName = file:sub(1,-5) -- Remove .lua
        if not tools[toolName] then
          local f = io.open(toolsPath..file,"r")
          if f then
            local code = f:read("*a")
            f:close()
            local t = load(code,toolsPath..file)(Emulator)
            if t and t.fun then
              n = n+1
              tools[toolName] = { sort=n, doc=t.doc, usage=t.usage, fun=t.fun }
            end
          end
        end
      end
    end
  end
end

function Emulator:runTool(tool,...)
  if tool == 'help' then
    loadExtraTools()
    local r = {} for k,v in pairs(tools) do r[#r+1] = {sort=v.sort,name=k,doc=v.doc,usage=v.usage} end
    table.sort(r,function(a,b) return a.sort < b.sort end)
    _print("=========== Available tools: ===================")
    for _,t in pairs(r) do
      _print(t.name,":",t.doc)
      _print("  ",t.usage)
      _print()
    end 
  elseif tools[tool] then 
    local stat,err = pcall(tools[tool].fun,self,...)
    if not stat then 
      self:ERROR("Tool error",tool,err)
    end
  else
    local fname = libpath.."tools/"..tool..".lua"
    local f = io.open(fname,"r")
    if f then
      local code = f:read("*a")
      f:close()
      local t = load(code,fname)()
      t.fun(self,...)
    else
      self:ERROR("Unknown tool: "..tool)
    end
  end
  --os.exit()
end

return Emulator