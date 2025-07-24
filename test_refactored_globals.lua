-- Test script to verify the refactored globals work correctly
print("Testing refactored timer and callback system")

-- Test that timers still work
local timer_count = 0
local timer_id = setTimeout(function()
    timer_count = timer_count + 1
    print("Timer executed, count:", timer_count)
    
    -- Test accessing the internal structures
    local timer_count = 0
    for _ in pairs(_PY._pending_timers) do timer_count = timer_count + 1 end
    print("Active timers in _PY._pending_timers:", timer_count)
    
    local callback_count = 0  
    for _ in pairs(_PY._callback_registry) do callback_count = callback_count + 1 end
    print("Callbacks in _PY._callback_registry:", callback_count)
end, 1000)

print("Timer created with ID:", timer_id)

-- Test interval
local interval_count = 0
local interval_id  -- Declare here so it's accessible in the closure
interval_id = setInterval(function()
    interval_count = interval_count + 1
    print("Interval executed, count:", interval_count)
    if interval_count >= 3 then
        clearInterval(interval_id)
        print("Interval cleared")
    end
end, 500)

print("Interval created with ID:", interval_id)
print("Test script loaded - timers should execute in the background")
