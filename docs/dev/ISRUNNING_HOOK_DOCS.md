# _PY.isRunning Hook Documentation

The `_PY.isRunning` hook is a powerful feature that allows Lua scripts to define custom termination logic based on runtime state. This is especially useful for scripts with asynchronous operations like timers, HTTP servers, and network callbacks.

## Overview

When using `--run-forever` or `--duration`, the runtime periodically calls the user-defined `_PY.isRunning` function (if it exists) to determine whether the script should continue running. This eliminates the need to manually place `os.exit()` calls throughout your code.

## Function Signature

```lua
function _PY.isRunning(state)
    -- state is a table with:
    -- state.active_timers: number of pending timers
    -- state.pending_callbacks: number of registered callbacks  
    -- state.total_tasks: active_timers + pending_callbacks
    
    -- Return true to continue running, false to terminate
    return boolean
end
```

## State Table Fields

- **`active_timers`**: Number of timers that haven't executed yet (created by `setTimeout`, etc.)
- **`pending_callbacks`**: Number of registered callbacks (HTTP server handlers, network callbacks, etc.)
- **`total_tasks`**: Sum of active_timers and pending_callbacks

## Usage Examples

### Example 1: Timer-based Completion

```lua
local tasks_completed = 0
local total_tasks = 3

function _PY.isRunning(state)
    -- Stop when all tasks are done and no pending work
    if tasks_completed >= total_tasks and state.total_tasks == 0 then
        print("All tasks completed - terminating")
        return false
    end
    return true
end

-- Schedule some work
setTimeout(function() tasks_completed = tasks_completed + 1 end, 1000)
setTimeout(function() tasks_completed = tasks_completed + 1 end, 2000)  
setTimeout(function() tasks_completed = tasks_completed + 1 end, 3000)
```

### Example 2: HTTP Server with Request Limit

```lua
local request_count = 0
local max_requests = 10

function _PY.isRunning(state)
    -- Stop after processing enough requests
    if request_count >= max_requests and state.total_tasks == 0 then
        print(string.format("Processed %d requests - shutting down", request_count))
        return false
    end
    return true
end

-- HTTP server handler
local function handle_request(method, path, payload)
    request_count = request_count + 1
    return json.encode({message = "OK", count = request_count}), 200
end

net.HTTPServer():start("0.0.0.0", 8080, handle_request)
```

### Example 3: Conditional Logic

```lua
function _PY.isRunning(state)
    print(string.format("Runtime check - Timers: %d, Callbacks: %d", 
        state.active_timers, state.pending_callbacks))
    
    -- Multiple termination conditions
    if state.total_tasks == 0 then
        print("No pending work - terminating")
        return false
    end
    
    -- Could add time-based limits, error conditions, etc.
    if os.time() > start_time + 300 then  -- 5 minute timeout
        print("Timeout reached - terminating")
        return false
    end
    
    return true
end
```

## When the Hook is Called

- **`--run-forever`**: Every 10 seconds
- **`--duration N`**: Every 1 second during the duration

## Default Behavior

If no `_PY.isRunning` hook is defined, the script runs for the full duration or forever (until manually stopped with Ctrl+C).

## Error Handling

If the `_PY.isRunning` hook throws an error, the runtime logs the error and defaults to continuing execution. This prevents hook bugs from crashing the main script.

## Best Practices

1. **Keep it simple**: The hook should be fast and lightweight
2. **Use state.total_tasks**: Most termination logic should check if `state.total_tasks == 0`
3. **Add your own counters**: Track application-specific completion states
4. **Debug output**: Print state information to understand what's happening
5. **Graceful defaults**: Return `true` if uncertain

## Testing

Use the provided test scripts:

```bash
# Simple timer-based test
python -m src.plua dev/test_simple_isrunning.lua --debug

# HTTP server test  
python -m src.plua dev/test_isrunning_hook.lua --debug
# Then make requests: curl http://localhost:8099/test
```

## Advanced Usage

### Custom Shutdown Logic

```lua
local shutdown_requested = false

function request_shutdown()
    shutdown_requested = true
    print("Shutdown requested by user")
end

function _PY.isRunning(state)
    if shutdown_requested then
        print("Processing shutdown request...")
        return false
    end
    return state.total_tasks > 0  -- Continue while work pending
end

-- Expose shutdown via HTTP endpoint
local function handle_request(method, path, payload)
    if path == "/shutdown" then
        request_shutdown()
        return json.encode({message = "Shutdown initiated"}), 200
    end
    -- ... other endpoints
end
```

This feature makes it much easier to write self-terminating scripts that clean up properly after completing their work!
