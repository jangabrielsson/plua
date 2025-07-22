-- Initialize Lua environment for plua2
-- This file contains the core runtime initialization code
-- 
-- This script is loaded by the Python LuaInterpreter class during initialization.
-- It sets up the timer system, coroutine handling, and core Lua functions.
-- The Python functions pythonTimer() and pythonCancelTimer() are injected
-- by the Python runtime before this script is executed.

-- Add src/lua to the front of package.path for require() statements
local current_path = package.path
package.path = "src/lua/?.lua;" .. current_path
local mobdebug = require('mobdebug')
mobdebug.coro()

-- Callback system for async operations (global for runtime state access)
_callback_registry = {}
_persistent_callbacks = {}  -- Track which callbacks should not be deleted
local _callback_counter = 0

-- Timer-specific tracking (now uses callback IDs, global for runtime state access)
_pending_timers = {}

function _PY.registerCallback(callback_func, persistent)
    _callback_counter = _callback_counter + 1
    _callback_registry[_callback_counter] = callback_func
    if persistent then
        _persistent_callbacks[_callback_counter] = true
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
    local callback = _callback_registry[callback_id]
    if callback then
        if not _persistent_callbacks[callback_id] then
            _callback_registry[callback_id] = nil  -- Clean up non-persistent callbacks
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
    local timer = _pending_timers[callback_id]
    if timer and not timer.cancelled then
      _pending_timers[callback_id] = nil  -- Cleanup
      debugCall("timer callback",callback)  -- Execute original callback
    elseif timer and timer.cancelled then
      print("Timer", callback_id, "was cancelled")
      _pending_timers[callback_id] = nil  -- Clean up cancelled timer
    end
  end
  
  -- Register as a regular callback (non-persistent, will be cleaned up after execution)
  callback_id = _PY.registerCallback(wrapper, false)
  
  -- Store timer metadata for cancellation support
  _pending_timers[callback_id] = {
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
  local timer = _pending_timers[callback_id]
  if timer then
    timer.cancelled = true
    _PY.pythonCancelTimer(callback_id)  -- Notify Python to cancel the task
    print("Timer", callback_id, "cancelled")
    return true
  else
    print("Timer", callback_id, "not found for cancellation")
    return false
  end
end

-- Direct timer execution without coroutine (for setTimeout)
local function _timer_direct(fun, ms)
  return _addTimer(fun, ms)
end

function sleep(ms)
  local co = coroutine.running()
  return _addTimer(function()
     coroutine.resume(co)
  end, ms)
end

function setTimeout(fun,ms)
  return _timer_direct(fun, ms)  -- Return timer ID, execute directly without coroutine
end

-- Track active intervals for proper cancellation
_active_intervals = {}

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
  local res = {"<font color='white'>",os.date("[%H:%M:%S]")}
  for _,v in ipairs({...}) do
    res[#res+1] = tostring(v)
  end
  res[#res+1] = "</font>"
  _print(table.concat(res, " "))
end

json = {}
json.encode = _PY.json_encode
json.decode = _PY.json_decode

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
-- _PY.broadcast_ui_update is set up by Python runtime, no default needed