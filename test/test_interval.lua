-- Test setInterval functionality
print("=== setInterval Test ===")

print("Creating interval that fires every 500ms...")
local count = 0
local interval_id = nil  -- Declare first

-- Create the interval and assign the ID
interval_id = _PY.setInterval(function()
    count = count + 1
    print("✓ Interval callback", count)
    
    if count >= 5 then
        print("✓ Stopping interval after 5 executions")
        print("✓ clearInterval called with ID:", interval_id)
        _PY.clearInterval(interval_id)
    end
end, 500)

print("Interval created with ID:", interval_id)
print("Active intervals:", _PY.has_active_intervals())

-- Yield to allow intervals to fire
for i = 1, 300 do  -- Wait for 3 seconds
    _PY.yield_to_loop()
    -- Small delay
    for j = 1, 100000 do end
end

print("Test completed!") 