-- Simple timer test
print("=== SIMPLE TIMER TEST ===")

-- Test setTimeout
print("Setting up timer...")
local timer_id = setTimeout(function()
    print("Timer fired!")
end, 1000)

print("Timer ID:", timer_id)

-- Test clearTimeout
print("Cancelling timer...")
local cancelled = clearTimeout(timer_id)
print("Timer cancelled:", cancelled)

-- Test another timer that should fire
print("Setting up another timer...")
setTimeout(function()
    print("Second timer fired!")
end, 500)

print("Waiting...")
_PY.sleep(2)

print("=== TEST COMPLETED ===") 