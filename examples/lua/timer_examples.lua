-- EPLua Timer Examples
-- Demonstrates setTimeout, setInterval, clearTimeout, clearInterval

print("=== EPLua Timer Examples ===")

-- 1. Basic setTimeout
print("\n1. Basic setTimeout:")
setTimeout(function()
    print("  ✓ This message appears after 1 second")
end, 1000)

-- 2. Multiple timeouts
print("\n2. Multiple timeouts:")
setTimeout(function() print("  ✓ First (500ms)") end, 500)
setTimeout(function() print("  ✓ Second (1000ms)") end, 1000)
setTimeout(function() print("  ✓ Third (1500ms)") end, 1500)

-- 3. Clearing timeouts
print("\n3. Clearing timeouts:")
local timeoutId = setTimeout(function()
    print("  ❌ This should NOT appear (cancelled)")
end, 2000)

setTimeout(function()
    print("  ✓ Cancelling the 2-second timeout")
    clearTimeout(timeoutId)
end, 1800)

-- 4. Basic setInterval
print("\n4. Basic setInterval:")
local count = 0
local intervalId = setInterval(function()
    count = count + 1
    print("  ✓ Interval tick:", count)
end, 600)

-- 5. Auto-clearing interval
setTimeout(function()
    print("  ✓ Clearing interval after 5 ticks")
    clearInterval(intervalId)
end, 3500)

-- 6. Self-clearing interval
print("\n5. Self-clearing interval:")
local selfCount = 0
local selfIntervalId
selfIntervalId = setInterval(function()
    selfCount = selfCount + 1
    print("  ✓ Self-clearing interval:", selfCount)
    
    if selfCount >= 3 then
        print("  ✓ Self-clearing now")
        clearInterval(selfIntervalId)
    end
end, 800)

-- 7. Timer chains
print("\n6. Timer chains:")
setTimeout(function()
    print("  ✓ Step 1: Starting chain")
    
    setTimeout(function()
        print("  ✓ Step 2: Chain continues")
        
        setTimeout(function()
            print("  ✓ Step 3: Chain completes")
        end, 500)
    end, 500)
end, 4000)

-- 8. Timer with error handling
print("\n7. Timer with error handling:")
setTimeout(function()
    print("  ✓ Timer with safe error handling")
    
    -- This would normally cause an error, but timers are wrapped with pcall
    local result = 10 / 0  -- Division by zero in Lua results in inf, not error
    print("  ✓ Result:", result)
end, 5000)

-- 9. Performance test
print("\n8. Performance test:")
local startTime = os.clock()
local performanceCount = 0
local perfInterval
perfInterval = setInterval(function()
    performanceCount = performanceCount + 1
    
    if performanceCount >= 10 then
        local endTime = os.clock()
        local elapsed = (endTime - startTime) * 1000
        print("  ✓ 10 intervals completed in", math.floor(elapsed), "ms")
        clearInterval(perfInterval)
    end
end, 50) -- Every 50ms

-- Completion
setTimeout(function()
    print("\n🎉 Timer Examples Complete!")
    print("All timer functions work as expected.")
end, 7000)
