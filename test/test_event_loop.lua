-- Test if event loop is processing tasks
print("=== Event Loop Test ===")

-- Test 1: Create a simple timer with a very short delay
print("Test 1: Creating a 100ms timer...")
_PY.setTimeout(function()
    print("✓ 100ms timer executed!")
end, 100)

print("Timer created. Active timers:", _PY.has_active_timers())

-- Test 2: Wait a bit and check
print("Test 2: Waiting and checking...")
for i = 1, 5 do
    print("Check", i, "- Active timers:", _PY.has_active_timers())
    _PY.yield_to_loop()
    -- Wait a bit
    for j = 1, 1000000 do end
end

print("Test completed!") 