_PY = _PY
local fmt = string.format
local bundled = require("plua.bundled_files")
local json = require("plua.json")
local class = require("plua.class")
local net = require("plua.net")
__TAG = "<font color='light_blue'>PLUA</font>"

local DEVICEID = 5555-1
local _print = print
local print,printErr = print,print -- redefile iater

---@class Emulator
Emulator = {}
class 'Emulator'
function Emulator:__init(plua)
  self.DIR = {}  -- deviceId -> { device = {}, path="..", qa=...}
  self.lib = plua
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
  
  self.tempDir = _PY.create_temp_directory("plua")
  self.lib.loadLib("utils",self)
  function print(...) plua.__fibaro_add_debug_message(__TAG, self.lib.logStr(...), "DEBUG") end
  function printErr(...) 
    plua.__fibaro_add_debug_message(__TAG, self.lib.logStr(...), "ERROR") 
  end
  self.lib.loadLib("fibaro_api",self)
  self.lib.loadLib("tools",self)
  self.lib.ui = self.lib.loadLib("ui",self)
end

function Emulator:registerDevice(info)
  if info.device.id == nil then DEVICEID = DEVICEID + 1; info.device.id = DEVICEID end
  self.DIR[info.device.id] = { 
    device = info.device, files = info.files, env = info.env, headers = info.headers,
    UI = info.UI, UImap = info.UImap, watches = info.watches,
  }
end

function Emulator:saveState() end
function Emulator:loadState() end

local function validate(str,typ,key)
  local stat,val = pcall(function() return load("return "..str)() end)
  if not stat then error(fmt("Invalid header %s: %s",key,str)) end
  if typ and type(val) ~= typ then 
    error(fmt("Invalid header %s: expected %s, got %s",key,typ,type(val)))
  end
  return val
end

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
    if _PY.file_exists(lpath) then path = lpath
    else error(fmt("Library not found: '%s'",path)) end
  end
  if _PY.file_exists(path) then
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

local function loadFile(env,path,name,content)
  if not content then
    local file = io.open(path, "r")
    assert(file, "Failed to open file: " .. path)
    content = file:read("*all")
    file:close()
  end
  local func, err = load(content, path, "t", env)
  if func then func() return true
  else error(err) end
end

function Emulator:loadResource(fname,parseJson)
  local file = io.open(fname, "r")
  assert(file, "Failed to open file: " .. fname)
  local content = file:read("*all")
  file:close()
  if parseJson then return json.decode(content) end
  return content
end

local embedUIs = require("plua.embedui")

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
    self.lib.loadLib("helper",self)
    self.lib.startHelper()
  end
  if headers.proxy then
    local proxylib = self.lib.loadLib("proxy",self)
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
    if deviceTypes == nil then deviceTypes = self:loadResource(bundled.get_lua_path().."/rsrsc/devices.json",true) end
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

function Emulator:saveQA(fname,id)
  local info = self.DIR[id]
  local fqa = self.lib.getFQA(id)
  self.lib.writeFile(fname,json.encode(fqa))
  self:INFO("Saved QA to",fname)
end

function Emulator:startQA(id)
  local info = self.DIR[id]
  if info.headers.save then self:saveQA(info.headers.save ,id) end
  if info.headers.project then self.lib.saveProject(id,info,nil) end
  local env = info.env
  env.setTimeout(function()
    local ok, err = pcall(function()
      if env.QuickApp and env.QuickApp.onInit then
        env.quickApp = env.QuickApp(info.device)
      else
        -- No quickApp object, no onInit function
      end
    end)
    if not ok then
      print("ERROR in setTimeout callback:", err)
    end
  end, 200)
end

function Emulator:restartQA(id)
  local info = self.DIR[id]
  self:INFO("Restarting QA",id, "in 4s")
  info.env.setTimeout(function()
    self:loadQA(info)
    self:startQA(id)
  end,4000)
end

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

function Emulator:createChild(data)
  local info = { UI = {}, headers = {} }
  if deviceTypes == nil then deviceTypes = self:loadResource(bundled.get_lua_path().."/rsrsc/devices.json",true) end
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
    __fibaro_add_debug_message = self.lib.__fibaro_add_debug_message, _PY = _PY,
  }
  for _,name in ipairs(stdLua) do env[name] = _G[name] end
  
  info.env = env
  local luapath = bundled.get_lua_path()
  loadfile(luapath.."/plua/fibaro.lua","t",env)()
  loadfile(luapath.."/plua/quickapp.lua","t",env)()
  env._G = env
  env.plugin.mainDeviceId = info.device.id
  for name,f in pairs(info.files) do
    if name ~= 'main' then loadFile(env,f.path,name,f.content) end
  end
  loadFile(env,info.files.main.path,'main',info.files.main.content)
end

function Emulator:loadMainFile(filename)
  if _PY.args.task then return self:runTask(_PY.args.task,filename) end
  if not filename then self:ERROR("No filename provided") return false end
  if filename:match("%.lua$") then 
    -- OK
  elseif filename:match("%.fqa$") then
    -- Unpack fqa file into temp directory, and run it.
    local fqaStr = self.lib.readFile(filename)
    assert(fqaStr,"Can' read file "..filename)
    local fqa = json.decode(fqaStr)
    filename = self.lib.unpackFQAAux(nil,fqa,self.tempDir)
  else
    self:ERROR("Invalid file type: "..filename)
    return false
  end
  
  local info = self:createInfoFromFile(filename)
  if info.headers.debug then self.debugFlag = true end
  if _PY.args.debug == true then self.debugFlag = true end

  if info.headers.offline then
    self.offline = true
    self:DEBUG("Offline mode")
  end
  
  if info.headers.offline then
    -- If main files has offline directive, setup offline routes
    self.lib.loadLib("offline",self)
    self.lib.setupOfflineRoutes()
  else
    -- self.lib.loadLib("helper",self)
    -- self.lib.startHelper()
  end
  
  self:loadQA(info)

  self:registerDevice(info)
  
  self:startQA(info.device.id)
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
      if not noUpdate then _PY.broadcast_ui_update(id) end
    else
      self:DEBUG("Unknown view property: " .. data.propertyName)
    end
  end
end

function Emulator:API_CALL(method, path, data)
  local api_url = self.lib.api_url
  -- Call _PY.fibaroapi directly to avoid HTTP request blocking
  self:DEBUG("API: " .. api_url .. "/api" .. path)
  local result, status_code = _PY.fibaroapi(method, "/api" .. path, data)
  
  -- fibaroapi now handles redirects internally and always returns {data, status_code}
  return result, status_code or 200, {}
end

function Emulator:HC3_CALL(method, path, data, redirect)
  
  if not self.lib.hc3_creds then
    self:ERROR("HC3 credentials not configured")
    return {error = "HC3 credentials not configured"}, 401
  end
  
  -- Construct the external URL with the full path (including query parameters)
  path = path:gsub("^/api/","/")
  local external_url = self.lib.hc3_url.."/api"..path
  if redirect then
    self:DEBUG("Redirect to: " .. external_url)
  else
    self:DEBUG("HC3 api: " .. external_url)
  end
  
  -- Prepare request data
  local request_data = {
    url = external_url,
    method = method,
    headers = {
      ["Authorization"] = self.lib.hc3_creds,
      ["Content-Type"] = "application/json"
    }
  }
  
  -- Add body for POST/PUT requests
  if data and (method == "POST" or method == "PUT") then
    if type(data) == "table" then
      request_data.body = json.encode(data)
    else
      request_data.body = tostring(data)
    end
  end
  
  -- Make the HTTP request
  local http_result = _PY.http_request_sync(request_data)
  
  -- Parse the response
  local response_body = http_result.body
  local response_data = nil
  
  if response_body and response_body ~= "" then
    local success, parsed = pcall(json.decode, response_body)
    if success then
      response_data = parsed
    else
      self:ERROR("JSON parse error: " .. tostring(parsed))
      response_data = response_body
    end
  else
    self:DEBUG("Empty response body")
    response_data = {}
  end
  
  -- Return consistent format: {data, status_code}
  return response_data, http_result.code or 200
end

local pollStarted = false
function Emulator:startRefreshStatesPolling()
  if not (self.offline or pollStarted) then
    pollStarted = true
    local result = _PY.pollRefreshStates(0, self.lib.hc3_url.."/api/refreshStates?last=", {
      headers = {Authorization = self.lib.hc3_creds}
    })
  end
end

function Emulator:getRefreshStates(last) return _PY.getEvents(last) end

function Emulator:refreshEvent(typ,data) _PY.addEvent(json.encode({type=typ,data=data})) end

function Emulator:DEBUG(...) if self.debugFlag then print(...) end end
function Emulator:INFO(...) self.lib.__fibaro_add_debug_message(__TAG, self.lib.logStr(...), "INFO", false) end 
function Emulator:WARNING(...) self.lib.__fibaro_add_debug_message(__TAG, self.lib.logStr(...), "WARNING", false) end 
function Emulator:ERROR(...) printErr(...) end

local function getFQA(self,fname)
  local info = self:createInfoFromFile(fname)
  self:registerDevice(info)
  return self.lib.getFQA(info.device.id)
end

function Emulator:runTask(task,arg1)

  if task == "uploadQA" then             -- uploadQA <filename>
    self:INFO("Uploading QA",arg1)
    local fqa = getFQA(self,arg1)
    self.lib.uploadFQA(fqa)

  elseif task == "updateFile" then        -- updateFile <filename>
    self.lib.updateFile(arg1)

  elseif task == "updateQA" then          -- updateQA <filename>
    self:INFO("Updating QA",arg1)
  elseif task == "downloadQA" then        -- downloadQA <id>:<path>
    local id,path = arg1:match("^([^:]+):(.*)$")
    self:INFO("Downloading QA",id,"to",path)

  elseif task == "packQA" then             -- packQA <filename>
    local fqa = getFQA(self,arg1)
    _print(json.encodeFast(fqa))

  else
    self:ERROR("Unknown task: "..task)
  end
  return false
end

return Emulator