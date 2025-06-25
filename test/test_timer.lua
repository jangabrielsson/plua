-- Timer test script
print("Starting timer tests...")

-- Test 1: Simple setTimeout
print("Test 1: setTimeout (2 seconds)")
_PY.setTimeout(function()
    print("✓ setTimeout callback executed after 2 seconds")
end, 2000)

-- Test 2: setTimeout with closure (capturing variables)
print("Test 2: setTimeout with closure (1 second)")
local message = "Hello from timer"
local number = 42
_PY.setTimeout(function()
    print("✓ setTimeout with closure:", message, number)
end, 1000)

-- Test 3: setInterval
print("Test 3: setInterval (every 1 second, 3 times)")
local interval_count,interval_id = 0,nil
interval_id = _PY.setInterval(function()
    interval_count = interval_count + 1
    print("✓ setInterval callback", interval_count, "of 3")
    
    if interval_count >= 3 then
        _PY.clearInterval(interval_id)
        print("✓ setInterval cleared after 3 executions")
    end
end, 1000)

-- Test 4: Multiple timers
print("Test 4: Multiple timers")
_PY.setTimeout(function()
    print("✓ Fast timer (500ms)")
end, 500)

_PY.setTimeout(function()
    print("✓ Medium timer (1500ms)")
end, 1500)

_PY.setTimeout(function()
    print("✓ Slow timer (3000ms)")
end, 3000)

-- Test 5: Timer cleanup
print("Test 5: Timer cleanup test")
local cleanup_timer = _PY.setTimeout(function()
    print("✓ This should NOT execute (timer was cleared)")
end, 5000)

_PY.setTimeout(function()
    print("✓ Clearing timer before it executes")
    _PY.clearTimeout(cleanup_timer)
end, 1000)

print("All timer tests started. Yielding to allow timers to fire...")
print("Expected execution order:")
print("  500ms: Fast timer")
print("  1000ms: setTimeout with closure + Timer cleanup")
print("  1500ms: Medium timer")
print("  2000ms: Simple setTimeout")
print("  3000ms: Slow timer")
print("  1s intervals: setInterval (3 times)")
print("  5000ms: Should NOT execute (cleared)")

-- Yield to the event loop to allow timers to fire
for i = 1, 400 do  -- Wait for 4 seconds
    _PY.yield_to_loop()
    -- Small delay to avoid overwhelming the event loop
    for j = 1, 100000 do end
end

print("Test completed!") 