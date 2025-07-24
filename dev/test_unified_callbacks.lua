-- test_unified_callbacks.lua
-- Test the unified timer/callback system

print("Testing unified callback system...")

-- Test 1: Basic timer functionality
print("Test 1: Basic timer")
setTimeout(function()
    print("Timer 1 executed!")
end, 1000)

-- Test 2: Timer with cancellation
print("Test 2: Timer cancellation")
local timer_id = setTimeout(function()
    print("This timer should be cancelled!")
end, 2000)

-- Cancel the timer after 500ms
setTimeout(function()
    print("Cancelling timer", timer_id)
    clearTimeout(timer_id)
end, 500)

-- Test 3: Multiple timers
print("Test 3: Multiple timers")
setTimeout(function()
    print("Timer A executed!")
end, 1500)

setTimeout(function()
    print("Timer B executed!")
end, 2500)

-- Test 4: Timer with coroutine (sleep)
print("Test 4: Coroutine timer")
coroutine.wrap(function()
    print("Before sleep...")
    _PY.sleep(3000)
    print("After sleep - coroutine timer works!")
end)()

print("All tests started - waiting for results...")
