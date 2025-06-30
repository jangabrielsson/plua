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

__TAG = "<font color='light_blue'>PLUA</font>"
plua.version = _PLUA_VERSION or "unknown"
plua.traceback = false

local function prettyCall(fun,errPrint)
  xpcall(fun,function(err)
    local info = debug.getinfo(2)
    local msg = err:match("^.-](:%d+:.*)$") or err
    local source = info.source:match("^.+/(.+)$") or info.short_src
    if plua.traceback then
      msg = msg .. "\n" .. debug.traceback()
    end
    (errPrint or print)(source..":"..msg)
    return false
  end)
  return true
end

plua.prettyCall = prettyCall

local typeColor = {
  DEBUG = "light_green",
  TRACE = "plum2",
  WARNING = "darkorange",
  ERROR = "light_red",
  INFO = "light_blue",
}

os.getenv = _PY.get_env_var

-- Adds a debug message to the emulator's debug output.
-- @param tag - The tag for the debug message.
-- @param msg - The message string.
-- @param typ - The type of message (e.g., "DEBUG", "ERROR").
function __fibaro_add_debug_message(tag, msg, typ, nohtml)
  local time = ""
  if plua.shortTime then
    time = tostring(os.date("[%H:%M:%S]"))
  else
    time = tostring(os.date("[%d.%m.%Y][%H:%M:%S]"))
  end
  local typStr = fmt("<font color='%s'>%-7s</font>", typeColor[typ], typ)
  msg = fmt("<font color='grey89'>%s[%s][%s]: %s</font>", time, typStr, tag, msg)
  _print(msg)
end

plua.__fibaro_add_debug_message = __fibaro_add_debug_message

plua.logStr = function(...) 
  local b = {} 
  for _,e in ipairs({...}) do 
    b[#b+1]=tostring(e) 
  end 
  return table.concat(b," ")
end

function print(...) __fibaro_add_debug_message(__TAG, plua.logStr(...), "DEBUG", false) end
function printErr(...) __fibaro_add_debug_message(__TAG, plua.logStr(...), "ERROR", false) end


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

plua.api_url = "http://127.0.0.1:8000"
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
      err = err:match("^.-qa_mgr%.lua:%d+:(.*)") or err
      local msg = err:match("^.-](:%d+:.*)$")
      if msg then err = filename..msg end
      Emu:ERROR(err)
    end
  end
end

_PY.mainHook = printError(function(filename) Emu:loadMainFile(filename) end)

_print("<font color='blue'>Fibaro API loaded</font>")