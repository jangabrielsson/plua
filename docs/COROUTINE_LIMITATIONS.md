# Coroutine Limitations in PLua

## Overview

PLua uses the Lupa library to provide Lua 5.4 functionality within Python. While Lupa provides excellent Lua integration, it has specific limitations regarding coroutine resumption that affect how timers and asynchronous operations work.

## The Core Limitation

**You cannot call `coroutine.resume()` directly from a Python callback (like a timer callback).**

This is a fundamental limitation of the Lupa library due to how it handles the Python→Lua C boundary. Attempting to resume a coroutine directly from a Python callback will cause a segmentation fault.

### Example of What Doesn't Work

```lua
-- This will crash with a segmentation fault
local function test()
  print("A")
  local co = coroutine.running()
  setTimeout(function() 
    print("D") 
    coroutine.resume(co)  -- ❌ CRASH: Cannot resume from Python callback
    print("E") 
  end, 1000)
  print("B")
  coroutine.yield()
  print("C")
end

local co = coroutine.create(test)
coroutine.resume(co)
```

## The PLua Solution: Queue-Based Callback System

PLua implements a workaround using a queue-based system that schedules coroutine resumes from the main event loop context, avoiding the unsafe C boundary crossing.

### How It Works

1. **Timer Callbacks Queue Lua Functions**: When a timer fires, the Python callback doesn't directly call the Lua function. Instead, it queues the Lua function for later execution.

2. **Continuous Event Loop Processing**: A dedicated asyncio task continuously processes the callback queue, executing Lua functions from the main event loop context.

3. **Safe Coroutine Resumption**: Coroutine resumes happen from the main event loop, not from Python callbacks, avoiding the C boundary issue.

### Example of What Works

```lua
-- This works correctly in PLua with the queue-based system
local function test()
  print("A")
  local co = coroutine.running()
  setTimeout(function() 
    print("D") 
    coroutine.resume(co)  -- ✅ SAFE: Resumes from main event loop context
    print("E") 
  end, 1000)
  print("B")
  coroutine.yield()
  print("C")
end

local co = coroutine.create(test)
coroutine.resume(co)

-- Output: A, B, D, C, E
```

## User Experience Impact

### What Users Expect (Standard Lua)

In standard Lua environments, users expect to be able to:

```lua
-- This pattern works in standard Lua
local co = coroutine.create(function()
  print("Starting...")
  coroutine.yield()
  print("Resumed!")
end)

coroutine.resume(co)  -- Prints "Starting..."

-- Later, from any context (timer, callback, etc.)
setTimeout(function()
  coroutine.resume(co)  -- Prints "Resumed!" - works in standard Lua
end, 1000)
```

### What Works in PLua

**Good news: The same pattern now works in PLua!** The queue-based system makes PLua behave like standard Lua:

```lua
-- PLua-compatible pattern (same as standard Lua)
local co = coroutine.create(function()
  print("Starting...")
  coroutine.yield()
  print("Resumed!")
end)

coroutine.resume(co)  -- Prints "Starting..."

-- This now works in PLua!
setTimeout(function()
  coroutine.resume(co)  -- Prints "Resumed!" - works in PLua
end, 1000)
```

## Best Practices for PLua

### 1. Use Standard Lua Patterns

The queue-based system makes PLua compatible with standard Lua patterns:

```lua
-- Good: Standard Lua pattern that works in PLua
local co = coroutine.create(function()
  print("Starting...")
  coroutine.yield()
  print("Resumed!")
end)

coroutine.resume(co)
setTimeout(function() coroutine.resume(co) end, 1000)

-- Also good: Use flags when appropriate
local done = false
setTimeout(function() done = true end, 1000)
while not done do coroutine.yield() end
```

### 2. Use `_PY.sleep()` for Simple Delays

```lua
-- Good: Use _PY.sleep for simple delays
_PY.sleep(1.0)  -- Non-blocking sleep that works with the event loop

-- Avoid: Blocking sleep
os.execute("sleep 1")  -- Blocks the entire interpreter
```

### 3. Keep Coroutines Alive

```lua
-- Good: Keep the main coroutine alive
while true do
  _PY.sleep(1)  -- This keeps the event loop running
end

-- Bad: Let the coroutine exit immediately
print("Done")  -- Coroutine exits, timers may not fire
```

### 4. Understand the Infrastructure

The queue-based system automatically handles:
- Timer callbacks
- Interval callbacks  
- Coroutine resumption
- Event loop integration
- Proper termination tracking

## Technical Details

### Why This Limitation Exists

Lupa uses the Lua C API to interface between Python and Lua. When a Python callback tries to resume a Lua coroutine, it crosses the C boundary in an unsafe way:

1. Python callback executes in Python context
2. `coroutine.resume()` call crosses into Lua C API
3. Lua C API tries to modify Lua state from Python context
4. This creates a race condition or invalid state, causing a segmentation fault

### The PLua Workaround

PLua's solution works by:

1. **Deferring Execution**: Python callbacks queue Lua functions instead of executing them directly
2. **Continuous Processing**: A dedicated asyncio task continuously processes the callback queue
3. **Safe Context**: All Lua interactions happen from the main event loop, avoiding the unsafe C boundary crossing
4. **Infrastructure Integration**: The callback processing task is excluded from termination decisions

### Architecture Overview

```
Timer Fires → Python Callback → Queue Lua Function → Event Loop Processes → Execute Lua Function → Resume Coroutine (if needed)
```

### Performance Considerations

The queue-based approach adds minimal overhead:
- Small memory usage for the callback queue
- Minimal latency (one event loop iteration, ~10ms)
- No impact on timer accuracy
- Thread-safe implementation
- Continuous processing ensures responsiveness

### Termination Strategy

The system properly handles termination:
- Infrastructure tasks (callback loop, main execution) are excluded from termination decisions
- Only user operations (timers, intervals) are counted
- Scripts terminate when all user operations complete
- The callback loop continues running until the entire process exits

## Testing and Verification

### Working Example: coro1.lua

```lua
--%%name:Coro
local function test()
  print("A")
  local co = coroutine.running()
  setTimeout(function() 
    print("D") 
    coroutine.resume(co) 
    print("E") 
  end, 1000)
  print("B")
  coroutine.yield()
  print("C")
end

local co = coroutine.create(test)
coroutine.resume(co)

-- Output: A, B, D, C, E (no segmentation fault)
```

### Working Example: Fibaro Interval

```lua
--%%name:Fibaro Basic
local n = 0
local ref = setInterval(function()
  n = n + 1
  print("B")
  if n > 5 then
    print("Stop")
    clearInterval(ref)  -- Works correctly, stops the interval
  end
end, 1000)

-- Output: B (6 times), Stop, then terminates
```

## Future Considerations

This limitation is inherent to Lupa's architecture and is unlikely to change. However, PLua could potentially:

1. **Better Error Messages**: Provide clearer error messages when users attempt unsafe patterns
2. **Pattern Detection**: Warn users about potentially problematic code patterns
3. **Performance Optimization**: Further optimize the queue processing for high-frequency timers
4. **Debugging Tools**: Add tools to inspect the callback queue and coroutine state

## Related Files

- `src/plua/coroutine_manager.py` - Implements the queue-based callback system
- `src/plua/interpreter.py` - Integrates coroutine management with the interpreter
- `examples/basic/` - Contains working examples of timer usage
- `dev/coro*.lua` - Test files demonstrating the limitations and solutions 