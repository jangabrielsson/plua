-- Complete timer system test
print("=== COMPLETE TIMER SYSTEM TEST ===")

-- Test 1: setTimeout and clearTimeout
print("\n--- Test 1: setTimeout and clearTimeout ---")
local timer1 = setTimeout(function()
    print("Timer 1 fired (should NOT see this)")
end, 2000)

local timer2 = setTimeout(function()
    print("Timer 2 fired (should see this)")
end, 1000)

print("Timer 1 ID:", timer1)
print("Timer 2 ID:", timer2)

-- Cancel timer1 immediately
print("Cancelling timer 1...")
local cancelled = clearTimeout(timer1)
print("Timer 1 cancelled:", cancelled)

-- Test 2: setInterval and clearInterval
print("\n--- Test 2: setInterval and clearInterval ---")
local interval_count = 0
local interval_id = setInterval(function()
    interval_count = interval_count + 1
    print("Interval fired, count:", interval_count)
    if interval_count >= 3 then
        print("Cancelling interval after 3 executions...")
        local cancelled = clearInterval(interval_id)
        print("Interval cancelled:", cancelled)
    end
end, 500)

print("Interval ID:", interval_id)

-- Test 3: Multiple timers
print("\n--- Test 3: Multiple timers ---")
setTimeout(function()
    print("Quick timer (500ms)")
end, 500)

setTimeout(function()
    print("Medium timer (1000ms)")
end, 1000)

setTimeout(function()
    print("Slow timer (1500ms)")
end, 1500)

-- Keep the coroutine alive
print("\nWaiting for all timers to complete...")
local wait_count = 0
while wait_count < 10 do
    _PY.sleep(1)
    wait_count = wait_count + 1
    print("Waited", wait_count, "seconds...")
end

print("=== TEST COMPLETED ===") 