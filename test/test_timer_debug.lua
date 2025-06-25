-- Timer debug test
print("Timer debug test starting...")

-- Test 1: Check if timer is created
print("Test 1: Creating timer...")
local timer_id = _PY.setTimeout(function()
    print("✓ Timer callback executed!")
end, 1000)

print("Timer ID:", timer_id)
print("Active timers:", _PY.has_active_timers())

-- Test 2: Check if interval is created
print("Test 2: Creating interval...")
local interval_id = _PY.setInterval(function()
    print("✓ Interval callback executed!")
end, 2000)

print("Interval ID:", interval_id)
print("Active intervals:", _PY.has_active_intervals())

-- Test 3: Check active operations
print("Test 3: Checking active operations...")
print("Active network operations:", _PY.has_active_network_operations())

-- Test 4: Check event loop status
print("Test 4: Checking event loop...")
local loop = _PY._get_event_loop_info()
if loop then
    print("Event loop info:", loop)
else
    print("No event loop info available")
end

print("Waiting for timers to execute...") 