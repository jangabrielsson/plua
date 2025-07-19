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

function _PY.executeCallback(callback_id, ...)
    local callback = _callback_registry[callback_id]
    if callback then
        if not _persistent_callbacks[callback_id] then
            _callback_registry[callback_id] = nil  -- Clean up non-persistent callbacks
        end
        callback(...)
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
      callback()  -- Execute original callback
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

-- Keep coroutine handling in Lua for specific functions that need it
local function _timer_with_coroutine(fun,ms,...)
  local co = coroutine.create(fun)
  local args = {...}
  return _addTimer(function()
    coroutine.resume(co,table.unpack(args))
  end, ms)
end

-- Direct timer execution without coroutine (for setTimeout)
local function _timer_direct(fun, ms)
  return _addTimer(fun, ms)
end

-- Simulate a Python timer function in Lua
function netWorkIO(callback)
  return _timer_with_coroutine(callback,1000,"xyz")
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

net = require("net")

-- Default main_file_hook implementation
-- This provides the standard behavior for loading and executing Lua files
-- Libraries can override this hook to provide custom preprocessing
function _PY.main_file_hook(filename)
    print("Loading file: " .. filename)
    
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
        coroutine.wrap(func)()
    else
        error("Failed to load script: " .. tostring(err))
    end
end

print("Lua runtime initialized with default main_file_hook")