-- Simple interval test
print("=== SIMPLE INTERVAL TEST ===")

-- Test setInterval
print("Setting up interval...")
local count = 0
local interval_id = setInterval(function()
    count = count + 1
    print("Interval fired, count:", count)
    if count >= 3 then
        print("Cancelling interval...")
        local cancelled = clearInterval(interval_id)
        print("Interval cancelled:", cancelled)
    end
end, 500)

print("Interval ID:", interval_id)

print("Waiting for intervals...")
_PY.sleep(3)

print("=== TEST COMPLETED ===") 