-- Initialize Lua environment for plua
-- This file contains the core runtime initialization code
-- 
-- This script is loaded by the Python LuaInterpreter class during initialization.
-- It sets up the timer system, coroutine handling, and core Lua functions.
-- The Python functions pythonTimer() and pythonCancelTimer() are injected
-- by the Python runtime before this script is executed.

-- Add src/lua to the front of package.path for require() statements
_PY = _PY or {}
local initpath = _PY.config.init_script_path:sub(1,-9).."?.lua;"
initpath = initpath:gsub("[\\/][%w_%s]+[\\/]%.%.","")
local current_path = package.path
package.path = initpath .. current_path

local debugger_config = _PY.config.runtime_config.debugger_config
if debugger_config then 
  local mobdebug = require('mobdebug')
  if debugger_config.debug then mobdebug.logging(true) end
  mobdebug.start(debugger_config.host,debugger_config.port)
  mobdebug.on()
  mobdebug.coro()
  _PY.mobdebug = mobdebug
else 
  _PY.mobdebug = { on = function() end, coro = function() end, logging = function(_) end, start = function() end, setbreakpoint = function(_,_) end }
end

-- Callback system for async operations (organized under _PY namespace)
_PY._callback_registry = {}
_PY._persistent_callbacks = {}  -- Track which callbacks should not be deleted
local _callback_counter = 0

-- Timer-specific tracking (now uses callback IDs, organized under _PY namespace)
_PY._pending_timers = {}

function _PY.registerCallback(callback_func, persistent)
    _callback_counter = _callback_counter + 1
    _PY._callback_registry[_callback_counter] = callback_func
    if persistent then
        _PY._persistent_callbacks[_callback_counter] = true
    end
    return _callback_counter
end

local function debugCall(typ,fun,...)
  xpcall(fun,function(err)
          local info = nil
          err = tostring(err)
          for i=2,5 do 
            info = debug.getinfo(i)
            if not info or info.what == 'Lua' then break end
          end
          if info then
            local source = info.source
            local line, msg = err:match(":(%d+): (.*)")
            line = line or info.currentline or ""
            err = source .. ":"..line..": "..(msg or err)
          end
          print("Error in "..typ..":", err)
          print(debug.traceback())
      end,...) 
end

function _PY.executeCallback(callback_id, ...)
    local callback = _PY._callback_registry[callback_id]
    if callback then
        if not _PY._persistent_callbacks[callback_id] then
            _PY._callback_registry[callback_id] = nil  -- Clean up non-persistent callbacks
        end
        debugCall("callback",callback,...)
    end
end

-- Unified timer system using callbacks
local function _addTimer(callback, delay_ms)
  -- Pre-declare callback_id for the wrapper closure
  local callback_id
  
  -- Create a wrapper function that handles timer-specific logic
  local wrapper = function()
    local timer = _PY._pending_timers[callback_id]
    if timer and not timer.cancelled then
      _PY._pending_timers[callback_id] = nil  -- Cleanup
      debugCall("timer callback",callback)  -- Execute original callback
    elseif timer and timer.cancelled then
      print("Timer", callback_id, "was cancelled")
      _PY._pending_timers[callback_id] = nil  -- Clean up cancelled timer
    end
  end
  
  -- Register as a regular callback (non-persistent, will be cleaned up after execution)
  callback_id = _PY.registerCallback(wrapper, false)
  
  -- Store timer metadata for cancellation support
  _PY._pending_timers[callback_id] = {
    callback = callback,
    delay_ms = delay_ms,
    id = callback_id,
    cancelled = false
  }
  
  -- Schedule with Python using the callback ID
  _PY.pythonTimer(callback_id, delay_ms)
  return callback_id
end

function clearTimeout(callback_id)
  local timer = _PY._pending_timers[callback_id]
  if timer then
    timer.cancelled = true
    _PY.pythonCancelTimer(callback_id)  -- Notify Python to cancel the task
    --print("Timer", callback_id, "cancelled")
  else
    --print("Timer", callback_id, "not found for cancellation")
  end
end

-- Direct timer execution without coroutine (for setTimeout)
local function _timer_direct(fun, ms)
  return _addTimer(fun, ms)
end

function _PY.sleep(ms)
  local co = coroutine.running()
  return _addTimer(function()
     coroutine.resume(co)
  end, ms)
end

function setTimeout(fun,ms)
  return _timer_direct(fun, ms)  -- Return timer ID, execute directly without coroutine
end

-- Track active intervals for proper cancellation
local _active_intervals = {}

function setInterval(fun, ms)
  local interval_id = _callback_counter + 1  -- Pre-allocate the next ID
  
  local function loop()
    -- Check if interval was cancelled before executing
    if not _active_intervals[interval_id] then
      return  -- Stop the loop
    end
    fun()  -- Execute the interval function
    -- Reschedule only if not cancelled
    if _active_intervals[interval_id] then
      _active_intervals[interval_id] = setTimeout(loop, ms)
    end
  end
  
  -- Register the interval as active
  -- Start the first iteration
  _active_intervals[interval_id] = setTimeout(loop, ms)
  
  return interval_id
end

function clearInterval(interval_id)
  local interval = _active_intervals[interval_id]
  if interval then
    clearTimeout(interval)  -- Cancel the timer
    _active_intervals[interval_id] = nil
  end
end

local _print = print

function print(...)
  local res = {}
  for _,v in ipairs({...}) do
    res[#res+1] = tostring(v)
  end
  _print("<font color='white'>"..table.concat(res, " ").."</font>")
end

json = require("json")

os.getenv = _PY.getenv_with_dotenv
net = require("net")

-- Default main_file_hook implementation
-- This provides the standard behavior for loading and executing Lua files
-- Libraries can override this hook to provide custom preprocessing

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

function _PY.main_file_hook(filename)
    require('mobdebug').on()
    require('mobdebug').coro()
    --print("Loading file: " .. filename)
    
    -- Read the file content
    local file = io.open(filename, "r")
    if not file then
        error("Cannot open file: " .. filename)
    end
    
    local content = file:read("*all")
    file:close()
    
    -- Load and execute the content in a coroutine, explicitly passing the global environment
    local func, err = load(content, "@" .. filename, "t", _G)
    if func then
        coroutine.wrapdebug(func, function(err,tb)
            err = err:match(":(%d+: .*)")
            print("Error in script " .. filename .. ": " .. tostring(err))
            print(tb)
        end)()  -- Execute the function in a coroutine
    else
        error("Failed to load script: " .. tostring(err))
    end
end

-- Default fibaro_api_hook implementation
-- This provides a default "service unavailable" response for Fibaro API calls
-- Libraries like fibaro.lua can override this hook to provide actual implementations
function _PY.fibaro_api_hook(method, path, data)
    -- Return service unavailable - Fibaro API not loaded
    return nil, 503
end

_PY.get_quickapps = _PY.get_quickapps or function() return {} end
_PY.get_quickapp = _PY.get_quickapp or function(_id) return nil end
-- _PY.broadcast_view_update is set up by Python runtime, no default needed

------- Extra functions ------------

-- File functions (readFile, writeFile, fileExist) are now implemented in Python
-- They are available via the @lua_exporter.export decorator as user_facing functions 