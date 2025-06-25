-- Comprehensive timer test
print("=== Comprehensive Timer Test ===")

-- Test 1: Check if timer is created
print("Test 1: Creating timer...")
local timer_id = _PY.setTimeout(function()
    print("✓ Timer callback executed!")
end, 1000)

print("Timer ID:", timer_id)
print("Active timers:", _PY.has_active_timers())

-- Test 2: Check event loop info
print("Test 2: Event loop info...")
local loop_info = _PY._get_event_loop_info()
print("Loop info:", loop_info)

-- Test 3: Create multiple timers
print("Test 3: Creating multiple timers...")
_PY.setTimeout(function()
    print("✓ Fast timer (500ms)")
end, 500)

_PY.setTimeout(function()
    print("✓ Medium timer (1500ms)")
end, 1500)

_PY.setTimeout(function()
    print("✓ Slow timer (3000ms)")
end, 3000)

print("Active timers after creating multiple:", _PY.has_active_timers())

-- Test 4: Try to yield and wait
print("Test 4: Yielding and waiting...")
for i = 1, 10 do
    print("Yield", i, "- Active timers:", _PY.has_active_timers())
    _PY.yield_to_loop()
    -- Busy wait a bit
    for j = 1, 100000 do end
end

print("Test completed!") 