-- Simple timer test
print("Simple timer test starting...")

-- Test basic setTimeout
print("Setting up a 1-second timer...")
_PY.setTimeout(function()
    print("✓ Timer callback executed!")
end, 1000)

print("Timer set up. Yielding to allow timer to fire...")

-- Yield to the event loop periodically to allow timers to fire
for i = 1, 20 do  -- Yield 20 times (2 seconds total)
    _PY.yield_to_loop()
    -- Small delay to avoid overwhelming the event loop
    for j = 1, 1000000 do end  -- Busy wait
end

print("Test completed!") 