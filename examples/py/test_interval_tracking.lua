-- Test interval tracking to ensure no premature exit
print("Testing interval tracking...")

local count = 0
local interval_id = _PY.setInterval(function()
    count = count + 1
    print("Interval tick", count)
    
    -- Stop after 3 ticks
    if count >= 3 then
        print("Clearing interval...")
        _PY.clearInterval(interval_id)
        print("Interval cleared, script should exit now")
    end
end, 500)

print("Interval started, waiting for 3 ticks...")
