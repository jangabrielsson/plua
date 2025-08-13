-- Test interval scoping to ensure proper cleanup
print("Testing interval scoping...")

do
    local count = 0
    -- The interval id should be accessible for clearing
    interval_id = _PY.setInterval(function()
        count = count + 1
        print("Scoped interval tick", count)
        
        -- Clear from global scope
        if count >= 3 then
            print("Clearing scoped interval...")
            _PY.clearInterval(interval_id)
            print("Scoped interval cleared")
        end
    end, 300)
end

print("Interval started from scoped block, waiting for clear...")
