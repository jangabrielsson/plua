-- test_callback_combination.lua
-- Test combining timers with other callback types

print("Testing callback combination...")

-- Test 1: Timer callback
print("Setting up timer...")
setTimeout(function()
    print("Timer callback executed successfully!")
end, 1000)

-- Test 2: Manual callback registration
print("Setting up manual callback...")
local callback_id = _PY.registerCallback(function(data)
    print("Manual callback executed with data:", data or "nil")
end, false)

-- Test 3: Trigger the manual callback after a delay
setTimeout(function()
    print("Triggering manual callback...")
    _PY.executeCallback(callback_id, "test data")
end, 2000)

-- Test 4: Persistent callback
print("Setting up persistent callback...")
local persistent_id = _PY.registerCallback(function(data)
    print("Persistent callback called with:", data or "nil")
end, true)

-- Call it multiple times
setTimeout(function()
    print("Calling persistent callback first time...")
    _PY.executeCallback(persistent_id, "first call")
end, 3000)

setTimeout(function()
    print("Calling persistent callback second time...")
    _PY.executeCallback(persistent_id, "second call")
end, 4000)

print("All tests set up, waiting for execution...")
