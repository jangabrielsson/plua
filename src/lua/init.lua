-- _PY is a bridge table with functions used to communicate between Lua and Python.
-- It is initialized in the PLua engine and provides access to timer functions.
local _PY = _PY or {}
local _print = print
local EMU

-- Use config for cross-platform paths
local config = _PY.config or {}
local luaLibPath = config.luaLibPath or "src/lua"
config.tempdir = os.tmpname():gsub("\\", "/")
if not config.tempdir:match("/$") then
  config.tempdir = config.tempdir .. "/"
end

-- Build platform-appropriate path
local initpath = luaLibPath .. "/" .. "?.lua;"
local current_path = package.path
package.path = initpath .. current_path

_PY.mobdebug = {     -- Setup void debug functions if we can't or wont load debugger
on = function() end, 
coro = function() end, 
logging = function(_) end, 
start = function() end, 
setbreakpoint = function(_,_) end, 
done = function() end 
}

local debugIDE = config.environment == "vscode" or config.environment == "zerobrane"
-- ToDo, make this more robust, by only guessing if we have no debugger flag.
-- Only try to start mobdebug if debugger is enabled in config
if config.debugger and debugIDE then 
  local success, mobdebug = pcall(require, 'mobdebug')
  if success then
    if config.debugger_logging then mobdebug.logging(true) end
    
    -- Set timeouts to prevent hanging
    mobdebug.yieldtimeout = 0.5  -- 500ms timeout for yield operations
    
    -- Try to start with timeout protection
    local start_success,err = pcall(function()
      mobdebug.start(config.debugger_host or "localhost", config.debugger_port or 8172)
      mobdebug.on()
      mobdebug.coro()
    end)
    if start_success then 
      _PY.mobdebug = mobdebug 
    else print("Mobdebug error:",err) end
  end
end

json = require('json')
local callbacks = {}
local callbackID = 0
local userFuns = {}

local environment = _PY.get_system_info().environment
_PY.config.cwd = environment.cwd
_PY.config.homedir = environment.home
_PY.config.user = environment.user

local f = io.open(_PY.config.homedir .. "/.plua/user_funs.lua", "r")
if f then
  local code = f:read("*all")
  f:close()
  local l,err = load(code)
  if not l then _print("Error loading user_funs.lua:", err)
  else
    local ok, res = pcall(l)
    if not ok then _print("Error executing user_funs.lua:", res)
    else userFuns = res end
  end
end

-- Register a callback and return its ID
function _PY.registerCallback(callback, persistent, system)
  callbackID = callbackID + 1
  persistent = persistent or false
  system = system or false
  --print("REG CB", tostring(callbackID), tostring(callback), persistent, system)
  callbacks[callbackID] = { 
    type = "callback", 
    callback = callback,
    system = system,
    persistent = persistent -- Default to non-persistent
  }
  return callbackID
end

function _PY.setTimeout(callback, ms, options)
  options = options or {}
  callbackID = callbackID + 1
  callbacks[callbackID] = { 
    type = "timeout", 
    callback = callback, 
    system = options.system or false,
    ref = _PY.set_timeout(callbackID, ms) 
  }
  return callbackID
end

function _PY.clearTimeout(id)
  if callbacks[id] then
    _PY.clear_timeout(callbacks[id].ref)
    callbacks[id] = nil
  end
end

-- Clear a registered callback manually (for persistent callbacks)
function _PY.clearRegisteredCallback(id)
  if callbacks[id] then
    callbacks[id] = nil
  end
end

local intervals = {}
local intervalID = 0

function _PY.setInterval(callback, ms)
  intervalID = intervalID + 1
  local id = intervalID
  
  -- Initialize the interval entry
  intervals[id] = true
  
  local function loop()
    if not intervals[id] then return end  -- Check if interval was cleared
    xpcall(callback,function(err)
      print("Error in interval callback: " .. tostring(err))
      print(debug.traceback())
      intervals[id] = nil
    end)
    if intervals[id] then
      -- If the interval is still active, schedule the next execution
      -- Store the new timeout reference in the intervals table
      intervals[id] = _PY.setTimeout(loop, ms)
    end
  end
  
  -- Start the first execution
  intervals[id] = _PY.setTimeout(loop, ms) 
  return id
end

function _PY.clearInterval(id)
  local ref = intervals[id]
  if ref then 
    _PY.clearTimeout(ref) 
    intervals[id] = nil
  end
end

function _PY.timerExpired(id,...)
  if callbacks[id] then 
    local is_persistent = callbacks[id].persistent
    
    -- Execute the callback with error handling
    xpcall(callbacks[id].callback,function(err)
      print("Error in timer callback: " .. tostring(err))
      print(debug.traceback())
    end,...)
    
    -- Clean up non-persistent callbacks AFTER execution
    if not is_persistent then
      callbacks[id] = nil
    end
  end
end

-- Get the count of pending callbacks (for CLI keep-alive logic)
function _PY.getPendingCallbackCount()
  local count = 0
  for _,v in pairs(callbacks) do
    count = count + (v.system and 0 or 1)
  end
  return count
end

-- Get the count of running callbacks (for CLI keep-alive logic)
function _PY.getRunningIntervalsCount()
  local count = 0
  for _ in pairs(intervals) do
    count = count + 1
  end
  return count
end

function _PY.get_callbacks_count() return _PY.getPendingCallbackCount(),_PY.getRunningIntervalsCount() end

local function Error(str)
  return setmetatable({}, {
    __tostring = function() return "Error: " .. tostring(str) end,
  })
end

local function doError(str,n) error(Error(str),n or nil) end

function _PY.mainfileResolver(filename)
  if not (filename:match("%.lua$") or filename:match("%.fqa")) then
    local f = io.open(filename, "r")
    if not f then return filename end
    local content = f:read("*a")
    f:close()
    local file = content:match("%[%[(.-)%]%]") or filename
    return file
  end
  return filename
end

local function loadAndRun(filename)
  local f = io.open(filename, "r")
  if not f then
    error("Could not open file: " .. filename)
  end
  local content = f:read("*a")
  f:close()
  local function loadAndRun()
    local func, err = load(content, filename)
    if not func then
      local msg = err:match("(:%d+: .*)") or err
      print("Error: Reading Lua file:", filename..msg)
      os.exit()
    else
      xpcall(func,function(err)
        local file,msg = err:match('"(.-)"%](.*)')
        local msg = file and (file..msg) or err
        print("Error: Running Lua file:", msg)
        _print(debug.traceback("..while running "..filename,1))
        os.exit()
      end)
    end
  end
  local co = coroutine.create(loadAndRun) -- Always run in a coroutine
  local ok, err = coroutine.resume(co)
  if not ok then
    _print(err)
    _print(debug.traceback(co, "..while running "..filename))
  end
end

function _PY.mainLuaFile(filenames)
  if _PY.config.tool then 
    EMU = require("fibaro")
    _PY.mainLuaFile(filenames)
    return
  end
  for _,filename in ipairs(filenames or {}) do
    -- ToDo, we could be smart here and check if it looks like a QuickApp file?
    loadAndRun(filename)
  end
end

local statements = {"do","if","while","for","repeat","function","local","return","break"}
local function returnCode(code)
  local isStatement = false
  for _,stat in ipairs(statements) do if code:match("^%s*" .. stat) then isStatement = true break end end
  if not isStatement then code = "return "..code end
  return code
end

function _PY.luaFragment(str) 
  if str:match("mobdebug") then return nil end -- ignore loading of mobdebug
  local func, err = load(returnCode(str))
  if not func then
    error("Error loading Lua fragment: " .. err)
  else
    local p = print -- kind of a hack to avoid clientPrint for upstart fragments...
    print = _print
    local res = {pcall(func)}
    print = p
    if not res[1] then
      error("Error executing Lua fragment: " .. res[2])
    end
    if #res > 1 then
      local r = {}
      for _,v in ipairs(res) do r[#r+1] = type(v)=='table' and json.encodeLua(v) or tostring(v) end
      _print(table.unpack(r,2))
    end
  end
end

local FUNCTION = "fun".."ction"
-- Handle thread-safe script execution requests
function _PY.threadRequest(id, script, isJson)
  -- This function can handle both Lua scripts and JSON function calls
  -- JSON format: {"function": "<function_name>", "module": "<module_name>", "args": [...]}
  local start_time = _PY.get_time()
  
  if isJson then
    -- Parse JSON and call the specified function
    local json_data, json_err = _PY.parse_json(script)
    if not json_data then
      _PY.threadRequestResult(id, {
        success = false,
        error = "JSON parse error: " .. tostring(json_err),
        result = nil,
        execution_time = _PY.get_time() - start_time
      })
      return
    end
    
    -- Validate JSON structure
    if type(json_data) ~= "table" or not json_data[FUNCTION] then
      _PY.threadRequestResult(id, {
        success = false,
        error = "Invalid JSON format: missing 'fun".."ction' field",
        result = nil,
        execution_time = _PY.get_time() - start_time
      })
      return
    end
    
    local func_name = json_data[FUNCTION]
    local module_name = json_data.module
    local args = json_data.args or {}
    
    -- Resolve the function to call
    local func_to_call
    if module_name then
      -- Call function from a specific module
      local module = _G[module_name]
      if not module then
        _PY.threadRequestResult(id, {
          success = false,
          error = "Module not found: " .. tostring(module_name),
          result = nil,
          execution_time = _PY.get_time() - start_time
        })
        return
      end
      func_to_call = module[func_name]
    else
      -- Call global function - check both _G and _PY tables
      func_to_call = _G[func_name] or _PY[func_name]
    end
    
    if not func_to_call or (type(func_to_call) ~= "function" and type(func_to_call) ~= "userdata") then
      local full_name = module_name and (module_name .. "." .. func_name) or func_name
      _PY.threadRequestResult(id, {
        success = false,
        error = "Function not found: " .. full_name,
        result = nil,
        execution_time = _PY.get_time() - start_time
      })
      return
    end
    
    -- Call the function with arguments
    local success, result = pcall(func_to_call, table.unpack(args))
    local execution_time = _PY.get_time() - start_time
    
    if success then
      -- Handle nil results explicitly
      if result == nil then
        result = "nil"  -- Convert nil to a string representation
      end
      
      _PY.threadRequestResult(id, {
        success = true,
        error = nil,
        result = result,
        execution_time = execution_time
      })
    else
      _PY.threadRequestResult(id, {
        success = false,
        error = "Function execution error: " .. tostring(result),
        result = nil,
        execution_time = execution_time
      })
    end
    
  else
    -- Handle regular Lua script execution (existing behavior)
    local func, err = load(script, "threadRequest:" .. id)
    if not func then
      _PY.threadRequestResult(id, {
        success = false,
        error = "Load error: " .. tostring(err),
        result = nil,
        execution_time = _PY.get_time() - start_time
      })
      return
    end
    
    -- Execute the script and capture result
    local success, result = pcall(func)
    local execution_time = _PY.get_time() - start_time
    
    if success then
      -- Handle nil results explicitly
      if result == nil then
        result = "nil"  -- Convert nil to a string representation
      end
      
      _PY.threadRequestResult(id, {
        success = true,
        error = nil,
        result = result,
        execution_time = execution_time
      })
    else
      _PY.threadRequestResult(id, {
        success = false,
        error = "Execution error: " .. tostring(result),
        result = nil,
        execution_time = execution_time
      })
    end
  end
end

function coroutine.wrapdebug(func,error_handler)
  local co = coroutine.create(func)
  return function(...)
    local res = {coroutine.resume(co, ...)}
    if res[1] then
      return table.unpack(res, 2)  -- Return all results except the first (true)
    else
      -- Handle error in coroutine
      local err,traceback = res[2], debug.traceback(co)
      if error_handler then
        error_handler(err, traceback)
      else
        print(err, traceback)
      end
    end
  end
end

-- redefine print to send to socket listeners
function print(...)
  local args = {...}
  local result = {}
  for i=1,#args do 
    local a = args[i]
    result[#result+1] = type(a) == 'table' and json.encodeLua(a) or tostring(a)
  end
  local resStr = table.concat(result," ")
  --resStr = os.date("[%m-%d %H:%M:%S]: ") .. resStr
  _PY.clientPrint(-1,resStr) -- send to all socket listeners
  --_PY.clientPrint(0,resStr)  -- send to stdout ?
end

function _PY.clientExecute(clientId,code)
  --_print("CE", clientId, code)
  local func, err = load(returnCode(code))
  if not func then _PY.clientPrint(clientId,err) return end
  if EMU then EMU.formatOutput = function(v) return type(v)=='table' and json.encodeLua(v) or tostring(v) end end
  local res = {pcall(func)}
  if not res[1] then _PY.clientPrint(clientId,res[2]) return end
  if #res > 1 then print(table.unpack(res,2)) end
end

function _PY.fibaroApiHook(method, path, data)
  -- Return service unavailable - Fibaro API not loaded
  print("❌ init.lua fibaroApiHook called (should not happen!) with:", method, path, data)
  return nil, 503
end

local runFor = tonumber(_PY.config.runFor)
if runFor then
  if runFor > 0 then
    _PY.setTimeout(function() os.exit() end, runFor * 1000, {system = true}) -- Kill after runFor seconds, if still running
  elseif runFor == 0 then
    _PY.setTimeout(function() end, math.huge) -- Keep running indefinitely...
  elseif runFor < 0 then
    _PY.setTimeout(function() os.exit() end, (-runFor) * 1000) -- Kill exactly runFor seconds
  end
end

_PY.getQuickapps = function()
  return nil, 503
end

_PY.getQuickapp = function(id)
  return nil, 503
end

----------------- Import standard libraries ----------------
net = require("net")
require("timers")
os.getenv = _PY.dotgetenv

if _PY.config.diagnostic then require("diagnostic") os.exit() end

if config.fibaro or config.environment=='zerobrane' then
  EMU = require("fibaro")
end