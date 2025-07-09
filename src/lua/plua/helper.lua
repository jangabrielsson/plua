local Emu = ...
local helperStarted = false
local HELPER_UUID = "plua-00-01"
local HELPER_VERSION = "1.0.0"
local fmt = string.format
local net = require("plua.net")

local startServer

local PORT = Emu.lib.webport+2
local function installHelper()
  local bundled = require("plua.bundled_files")
  local fqa =  Emu:loadResource(bundled.get_lua_path().."/rsrsc/pluaHelper.fqa",true)
  if not fqa then
    Emu:ERRORF("Failed to load helper")
    return nil
  end
  fqa.visible = false
  fqa.initialProperties.quickAppUuid = HELPER_UUID
  fqa.initialProperties.model = HELPER_VERSION
  local helper,err = Emu.lib.uploadFQA(fqa)
  if not helper then
    Emu:ERROR(fmt("Failed to install helper: %s",err or "Unknown error"))
    return nil
  end
  Emu.api.hc3.put("/devices/"..helper.id,{visible=false}) -- Hide helper
  Emu:INFO("Helper installed")
  return helper
end

local connection = nil
local function startHelper()
  if helperStarted then return connection end
  local helpers = (Emu.api.hc3.get("/devices?property=[quickAppUuid,"..HELPER_UUID.."]") or {})
  local helper
  if #helpers > 1 then
    Emu:ERROR("Multiple helper instances found, will remove all but latest")
    table.sort(helpers,function(a,b) return a.id < b.id end)
    for i=1,#helpers-1 do
      Emu.api.hc3.delete("/devices/"..helpers[i].id)
    end
  end
  helper = helpers[#helpers]
  if not helper or helper.properties.model ~= HELPER_VERSION then
    if helper then Emu.api.hc3.delete("/devices/"..helper.id) end -- Old, remove and install new helper
    helper = installHelper()
  end
  if not helper then
    return Emu:ERROR("Failed to install helper")
  end
  local helperId = helper.id
  local wsurl = fmt("ws://%s:%d",Emu.lib.IPAddress,PORT)
  if helperId then startServer(helperId,wsurl) end
  helperStarted = true
end

local client = nil
local server = nil
local cb = nil
function startServer(helperId,wsurl)
  server = net.WebSocketServer(false)
  local host,port = Emu.lib.IPAddress,PORT
  --Emu:INFO("Starting helper server on",host,port)
  server:start(host, port, {
    receive = function(client_id, msg) if cb then cb(msg) end end,
    connected = function(client_id)
      if Emu.debugFlag then Emu:INFO("Helper connected") end
      client = client_id
    end,
    disconnected = function(client_id) client = nil end
  })
  setTimeout(function()
    Emu.api.hc3.post("/devices/"..helperId.."/action/connect",{args={wsurl}}) 
  end,10)
end

local function send(msg)
  if Emu.offline then
    Emu:WARNING("api.hc3.restricted: Offline mode")
    return '{false,"Offline mode"}'
  end
  if not (client and server) then return nil end
  local co = coroutine.running()
  if not co then return nil end
  cb = function(msg) coroutine.resume(co,msg) end
  server:send(client,msg)
  return coroutine.yield()
end

Emu.lib.startHelper = startHelper
Emu.lib.sendSyncHc3 = send
