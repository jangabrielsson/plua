--[[
  This file is the entry point for setting up a Fibaro Lua environment.
  Supports QuickApp and Fibaro API.
]]
---@table _PY
_PY = _PY or {}
local plua = {}

_print = print
local fmt = string.format
local bundled = require("plua.bundled_files")
local libPath = bundled.get_lua_path().."/plua/"
function plua.loadLib(name,...) return loadfile(libPath..name..".lua","t",_G)(...) end
json = require("plua.json")
plua.loadLib("emulator",plua)

os.getenv = _PY.get_env_var

__TAG = "<font color='light_blue'>PLUA</font>"
plua.version = _PLUA_VERSION or "unknown"
plua.traceback = false

local hc3_url = _PY.pluaconfig and _PY.pluaconfig.hc3_url or os.getenv("HC3_URL")
local hc3_user = _PY.pluaconfig and _PY.pluaconfig.hc3_user or  os.getenv("HC3_USER")
local hc3_pass = _PY.pluaconfig and _PY.pluaconfig.hc3_pass or os.getenv("HC3_PASSWORD")
local hc3_port = 80
if hc3_url then
  local protocol = hc3_url:match("^(https?)://")
  if not protocol then 
    hc3_url = "http://" .. hc3_url
  end
  hc3_url = hc3_url:sub(-1) == "/" and hc3_url:sub(1,-2) or hc3_url
  hc3_url = hc3_url:gsub(":[0-9]+$", "") or hc3_url
  hc3_port = protocol == "https" and 443 or 80
  hc3_url = hc3_url..":"..hc3_port
end

plua.webport = _PY.args.port or 8000
plua.IPAddress = _PY.get_local_ip()
plua.api_url = string.format("http://127.0.0.1:%s",plua.webport)
plua.hc3_url = hc3_url
plua.hc3_port = hc3_port
if hc3_user and hc3_pass then 
  plua.hc3_creds = "Basic " .. _PY.base64_encode(hc3_user .. ":" .. hc3_pass)
end

local Emu = Emulator(plua)

local function printError(func)
  return function(filename)
    local ok,err = pcall(func,filename)
    if not ok then
      print(err)
      err = type(err) == "string" and err or tostring(err)
      if type(err) == "string" then
        err = err:match("^.-qa_mgr%.lua:%d+:(.*)") or err
        local msg = err:match("^.-](:%d+:.*)$")
        if msg then err = filename..msg end
      end
      Emu:ERROR(err)
    end
  end
end

_PY.mainHook = printError(function(filename) 
  Emu:loadMainFile(filename) 
end)

function _PY.getQAInfo(id) 
  local qa_data = Emu.DIR[id]
  if qa_data then
    return json.encode({device=qa_data.device,UI=qa_data.UI})
  else
    return nil
  end
end

function _PY.getAllQAInfo() 
  local qa_data = {}
  for _,i in pairs(Emu.DIR) do
    qa_data[#qa_data+1] = {device=i.device,UI=i.UI}
  end
  return json.encode(qa_data)
end

if not _PY.args.task then
  _print(fmt("<font color='blue'>Fibaro API loaded%s</font>",_PY.args.task and (" with task ".._PY.args.task) or ""))
end