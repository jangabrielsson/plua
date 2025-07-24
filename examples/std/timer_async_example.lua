-- Timer and Async Example
-- This example shows how to use timers and asynchronous operations in plua

print("=== Timer and Async Example ===")

-- Example 1: Basic timers
print("\n1. Basic timer operations")

print("Starting timer examples at", os.date("%H:%M:%S"))

-- Single timeout
setTimeout(function()
    print("✅ Single timeout executed at", os.date("%H:%M:%S"))
end, 1000)

-- Multiple timeouts with different delays
setTimeout(function()
    print("⏰ Timer 1: 500ms delay")
end, 500)

setTimeout(function()
    print("⏰ Timer 2: 1500ms delay")
end, 1500)

setTimeout(function()
    print("⏰ Timer 3: 2000ms delay")
end, 2000)

-- Example 2: Repeating timer (setInterval)
setTimeout(function()
    print("\n2. Repeating timer example")
    
    local counter = 0
    local max_count = 5
    local interval_id  -- Declare before use
    
    interval_id = setInterval(function()
        counter = counter + 1
        print("📅 Interval tick " .. counter .. " at " .. os.date("%H:%M:%S"))
        
        if counter >= max_count then
            clearInterval(interval_id)
            print("✅ Interval stopped after " .. max_count .. " ticks")
        end
    end, 800)
    
end, 3000)

-- Example 3: Chained async operations
setTimeout(function()
    print("\n3. Chained async operations")
    
    -- Declare functions first
    local step1, step2, step3
    
    step1 = function()
        print("🔄 Step 1: Starting process...")
        setTimeout(step2, 500)
    end
    
    step2 = function()
        print("🔄 Step 2: Processing data...")
        setTimeout(step3, 700)
    end
    
    step3 = function()
        print("🔄 Step 3: Finalizing...")
        setTimeout(function()
            print("✅ All steps completed!")
        end, 300)
    end
    
    step1()
    
end, 8000)

-- Example 4: Simulating async work with timers
setTimeout(function()
    print("\n4. Simulating async work")
    
    local function simulate_api_call(endpoint, callback)
        print("🌐 Making API call to: " .. endpoint)
        
        -- Simulate network delay
        local delay = math.random(500, 2000)
        setTimeout(function()
            -- Simulate success/failure
            local success = math.random() > 0.2 -- 80% success rate
            
            if success then
                local fake_data = {
                    endpoint = endpoint,
                    timestamp = os.time(),
                    data = "Sample response data",
                    status = 200
                }
                callback(nil, fake_data)
            else
                callback("Network error", nil)
            end
        end, delay)
    end
    
    -- Make multiple API calls
    local endpoints = {"/users", "/posts", "/comments"}
    local completed = 0
    
    for i, endpoint in ipairs(endpoints) do
        simulate_api_call(endpoint, function(error, data)
            completed = completed + 1
            
            if error then
                print("❌ " .. endpoint .. " failed: " .. error)
            else
                print("✅ " .. endpoint .. " success: " .. data.data)
            end
            
            if completed == #endpoints then
                print("🎉 All API calls completed!")
            end
        end)
    end
    
end, 12000)

-- Example 5: Timer cancellation
setTimeout(function()
    print("\n5. Timer cancellation example")
    
    local timer_id = setTimeout(function()
        print("❌ This should not execute (timer was cancelled)")
    end, 1000)
    
    -- Cancel the timer before it executes
    setTimeout(function()
        clearTimeout(timer_id)
        print("✅ Timer cancelled successfully")
    end, 500)
    
end, 16000)

-- Example 6: Performance timing
setTimeout(function()
    print("\n6. Performance timing")
    
    local start_time = os.clock()
    
    local function heavy_computation()
        -- Simulate some CPU work
        local sum = 0
        for i = 1, 100000 do
            sum = sum + math.sin(i)
        end
        return sum
    end
    
    print("🔢 Starting computation...")
    local result = heavy_computation()
    local end_time = os.clock()
    
    print("✅ Computation complete!")
    print("   Result: " .. string.format("%.6f", result))
    print("   Time: " .. string.format("%.3f", (end_time - start_time) * 1000) .. "ms")
    
end, 19000)

print("Timer examples scheduled. Watch for outputs over the next 20+ seconds...")
print("This demonstrates plua's event loop and async capabilities.")
