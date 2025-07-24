# Timer and Callback System Unification

## Overview

Successfully unified the timer and callback systems in plua, eliminating code duplication and creating a more maintainable architecture.

## Changes Made

### 1. Lua Side (src/lua/init.lua)

**Before:**
- Separate timer system with `_addTimer()`, `_executeTimer()`, `_pending_timers`
- Separate callback system with `registerCallback()`, `executeCallback()`, `_callback_registry`
- Two different ID counters and execution paths

**After:**
- Unified system where timers are implemented as special callback wrappers
- Single callback registration system handles both timers and general callbacks
- Timer-specific logic (cancellation, cleanup) handled in the wrapper function

#### Key Changes:
```lua
-- Unified timer implementation using callbacks
local function _addTimer(callback, delay_ms)
  local callback_id
  
  -- Timer wrapper handles cancellation and cleanup
  local wrapper = function()
    local timer = _pending_timers[callback_id]
    if timer and not timer.cancelled then
      _pending_timers[callback_id] = nil  -- Cleanup
      callback()  -- Execute original callback
    elseif timer and timer.cancelled then
      print("Timer", callback_id, "was cancelled")
      _pending_timers[callback_id] = nil
    end
  end
  
  -- Register as regular callback
  callback_id = _PY.registerCallback(wrapper, false)
  
  -- Store timer metadata for cancellation
  _pending_timers[callback_id] = { ... }
  
  _PY.pythonTimer(callback_id, delay_ms)
  return callback_id
end
```

### 2. Python Side

**Removed:**
- `interpreter.execute_timer()` method
- Separate timer execution logic in `runtime.py`

**Updated:**
- `runtime.py` now uses `execute_lua_callback()` for both timer and callback execution
- `execute_lua_callback()` handles `None` data (for timers) and actual data (for callbacks)
- Single execution path in `run_timer_callbacks_loop()`

#### Key Changes:
```python
# runtime.py - Unified execution
if callback_data.type == "timer":
    # Execute timer callback using unified callback system
    self.interpreter.execute_lua_callback(callback_data.callback_id, None)
elif callback_data.type == "lua_callback":
    # Execute general Lua callback
    self.interpreter.execute_lua_callback(callback_data.callback_id, callback_data.data)

# interpreter.py - Handle None data for timers
def execute_lua_callback(self, callback_id: int, data: Any) -> None:
    if data is not None:
        # Normal callback with data
        lua_data = lua_exporter._convert_to_lua(data, self.lua)
        self.lua.globals().temp_callback_data = lua_data
        execute_script = f"_PY.executeCallback({callback_id}, temp_callback_data)"
    else:
        # Timer callback without data
        execute_script = f"_PY.executeCallback({callback_id})"
```

## Benefits Achieved

### 1. **Code Reduction**
- Eliminated duplicate registration/execution systems
- Removed ~30 lines of duplicate code
- Single execution path in runtime loop

### 2. **Improved Maintainability**
- One callback mechanism for all async operations
- Easier to debug and trace execution
- Consistent error handling and logging

### 3. **Better Flexibility**
- Easy to add new async operation types
- Timer logic encapsulated in wrapper functions
- Consistent callback ID space across all operations

### 4. **No Breaking Changes**
- All existing timer functions (`setTimeout`, `clearTimeout`, `sleep`) work unchanged
- All existing callback functions work unchanged
- Tests pass with minimal updates

## Testing Results

### ✅ **Timer Functionality**
- Basic timers work correctly
- Timer cancellation functions properly
- Multiple timers execute in correct order
- Coroutine-based `sleep()` function works

### ✅ **Callback Functionality**
- Manual callback registration works
- Persistent vs. non-persistent callbacks handled correctly
- Data passing to callbacks functions properly

### ✅ **Integration**
- All existing tests pass (with one test updated for the unified method)
- No performance regression
- Error handling preserved

## Architecture Improvement

**Before:**
```
Python Timer Request → runtime.py → interpreter.execute_timer() → _PY._executeTimer()
Python Callback Request → runtime.py → interpreter.execute_lua_callback() → _PY.executeCallback()
```

**After:**
```
Python Timer Request → runtime.py → interpreter.execute_lua_callback(id, None) → _PY.executeCallback()
Python Callback Request → runtime.py → interpreter.execute_lua_callback(id, data) → _PY.executeCallback()
```

## Future Extensibility

The unified system makes it trivial to add new async operation types:

1. Create a wrapper function in Lua that handles the operation-specific logic
2. Register the wrapper as a callback
3. Use the existing Python→Lua callback mechanism
4. No changes needed to runtime loop or execution paths

This unification creates a cleaner, more maintainable foundation for future async features in plua.
