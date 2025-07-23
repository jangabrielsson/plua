# Timers & Async Operations

The timer system in plua2 provides JavaScript-like asynchronous operations, enabling time-based delays, intervals, and precise scheduling of Lua functions.

## ⏰ Basic Timer Functions

### setTimeout

Execute a function after a specified delay.

```lua
-- Basic timeout
setTimeout(function()
    print("This runs after 2 seconds")
end, 2000)

-- Timeout with parameters
local function greet(name, message)
    print("Hello " .. name .. "! " .. message)
end

setTimeout(function()
    greet("Alice", "Welcome to plua2!")
end, 1000)
```

### clearTimeout

Cancel a scheduled timeout before it executes.

```lua
-- Schedule a timeout
local timer_id = setTimeout(function()
    print("This will not execute")
end, 5000)

-- Cancel it after 2 seconds
setTimeout(function()
    clearTimeout(timer_id)
    print("Timer cancelled")
end, 2000)
```

### setInterval

Execute a function repeatedly at specified intervals.

```lua
local counter = 0

local interval_id = setInterval(function()
    counter = counter + 1
    print("Counter:", counter)
    
    -- Stop after 5 iterations
    if counter >= 5 then
        clearInterval(interval_id)
        print("Interval stopped")
    end
end, 1000)  -- Every 1 second
```

### clearInterval

Stop a repeating interval.

```lua
local start_time = os.time()

local interval_id = setInterval(function()
    local elapsed = os.time() - start_time
    print("Elapsed time:", elapsed, "seconds")
end, 500)

-- Stop after 10 seconds
setTimeout(function()
    clearInterval(interval_id)
    print("Interval cleared after 10 seconds")
end, 10000)
```

## 🔄 Advanced Timer Patterns

### Debouncing

Delay execution until after a series of rapid calls has stopped.

```lua
local function create_debounce(func, delay)
    local timer_id = nil
    
    return function(...)
        local args = {...}
        
        if timer_id then
            clearTimeout(timer_id)
        end
        
        timer_id = setTimeout(function()
            func(table.unpack(args))
            timer_id = nil
        end, delay)
    end
end

-- Usage example
local debounced_save = create_debounce(function(data)
    print("Saving data:", data)
end, 1000)

-- These calls will be debounced
debounced_save("data1")
debounced_save("data2")
debounced_save("data3")  -- Only this one will execute after 1 second
```

### Throttling

Limit function execution to once per time period.

```lua
local function create_throttle(func, delay)
    local last_call = 0
    
    return function(...)
        local now = os.time() * 1000  -- Convert to milliseconds
        
        if now - last_call >= delay then
            last_call = now
            func(...)
        end
    end
end

-- Usage example
local throttled_log = create_throttle(function(message)
    print(os.date() .. ": " .. message)
end, 2000)  -- At most once per 2 seconds

-- These calls will be throttled
for i = 1, 10 do
    setTimeout(function()
        throttled_log("Message " .. i)
    end, i * 100)
end
```

### Retry Logic

Retry operations with exponential backoff.

```lua
local function retry_with_backoff(func, max_attempts, base_delay)
    local attempt = 0
    
    local function try_execute()
        attempt = attempt + 1
        
        local success, result = pcall(func)
        
        if success then
            print("✓ Operation succeeded on attempt", attempt)
            return result
        else
            print("✗ Attempt", attempt, "failed:", result)
            
            if attempt < max_attempts then
                local delay = base_delay * (2 ^ (attempt - 1))  -- Exponential backoff
                print("Retrying in", delay, "ms...")
                
                setTimeout(try_execute, delay)
            else
                print("✗ All", max_attempts, "attempts failed")
            end
        end
    end
    
    try_execute()
end

-- Usage example
local function unreliable_operation()
    if math.random() < 0.7 then  -- 70% chance of failure
        error("Random failure")
    end
    return "Success!"
end

retry_with_backoff(unreliable_operation, 5, 1000)  -- 5 attempts, starting with 1s delay
```

## ⏱️ Timing and Measurement

### Execution Timer

Measure how long operations take.

```lua
local function time_operation(name, operation)
    local start_time = os.time() * 1000  -- Milliseconds
    
    print("Starting operation:", name)
    
    local function finish()
        local elapsed = (os.time() * 1000) - start_time
        print(string.format("✓ %s completed in %d ms", name, elapsed))
    end
    
    -- Execute operation
    operation(finish)
end

-- Usage example
time_operation("Data Processing", function(done)
    -- Simulate some work
    local result = 0
    for i = 1, 1000000 do
        result = result + i
    end
    
    setTimeout(function()
        print("Result:", result)
        done()
    end, 100)
end)
```

### Performance Monitor

Track performance metrics over time.

```lua
local performance_monitor = {
    operations = {},
    start_time = os.time()
}

function performance_monitor:record(operation_name, duration)
    if not self.operations[operation_name] then
        self.operations[operation_name] = {
            count = 0,
            total_time = 0,
            min_time = math.huge,
            max_time = 0
        }
    end
    
    local op = self.operations[operation_name]
    op.count = op.count + 1
    op.total_time = op.total_time + duration
    op.min_time = math.min(op.min_time, duration)
    op.max_time = math.max(op.max_time, duration)
end

function performance_monitor:report()
    print("\n--- Performance Report ---")
    print(string.format("Uptime: %d seconds", os.time() - self.start_time))
    
    for name, stats in pairs(self.operations) do
        local avg_time = stats.total_time / stats.count
        print(string.format("%s: %d calls, avg %.1fms, min %.1fms, max %.1fms",
              name, stats.count, avg_time, stats.min_time, stats.max_time))
    end
    print("------------------------\n")
end

-- Auto-report every 10 seconds
setInterval(function()
    performance_monitor:report()
end, 10000)

-- Example usage
local function timed_operation(name, work_function)
    local start = os.time() * 1000
    
    work_function(function()
        local duration = (os.time() * 1000) - start
        performance_monitor:record(name, duration)
    end)
end
```

## 🚀 Async Patterns

### Sequential Execution

Execute async operations in sequence.

```lua
local function async_sequence(operations, callback)
    local index = 1
    
    local function execute_next()
        if index <= #operations then
            local operation = operations[index]
            index = index + 1
            
            operation(execute_next)  -- Pass continuation
        else
            if callback then callback() end
        end
    end
    
    execute_next()
end

-- Usage example
async_sequence({
    function(next)
        print("Step 1: Initializing...")
        setTimeout(next, 1000)
    end,
    
    function(next)
        print("Step 2: Loading data...")
        setTimeout(next, 1500)
    end,
    
    function(next)
        print("Step 3: Processing...")
        setTimeout(next, 800)
    end
}, function()
    print("✓ All steps completed!")
end)
```

### Parallel Execution

Execute multiple async operations in parallel.

```lua
local function async_parallel(operations, callback)
    local completed = 0
    local results = {}
    
    for i, operation in ipairs(operations) do
        operation(function(result)
            completed = completed + 1
            results[i] = result
            
            if completed == #operations then
                if callback then callback(results) end
            end
        end)
    end
end

-- Usage example
async_parallel({
    function(done)
        setTimeout(function()
            done("Result A")
        end, 1000)
    end,
    
    function(done)
        setTimeout(function()
            done("Result B")
        end, 1500)
    end,
    
    function(done)
        setTimeout(function()
            done("Result C")
        end, 800)
    end
}, function(results)
    print("✓ All parallel operations completed:")
    for i, result in ipairs(results) do
        print("  Operation", i, ":", result)
    end
end)
```

### Rate Limiting

Control the rate of operations.

```lua
local function create_rate_limiter(max_per_second)
    local queue = {}
    local processing = false
    local interval = 1000 / max_per_second  -- milliseconds between operations
    
    local function process_queue()
        if #queue > 0 and not processing then
            processing = true
            local operation = table.remove(queue, 1)
            
            operation()
            
            setTimeout(function()
                processing = false
                if #queue > 0 then
                    process_queue()
                end
            end, interval)
        end
    end
    
    return function(operation)
        table.insert(queue, operation)
        process_queue()
    end
end

-- Usage example: Limit to 2 operations per second
local rate_limiter = create_rate_limiter(2)

for i = 1, 10 do
    rate_limiter(function()
        print(os.date() .. ": Processing item", i)
    end)
end
```

## 🔄 Scheduled Tasks

### Daily Tasks

Execute tasks at specific times.

```lua
local function schedule_daily(hour, minute, task)
    local function calculate_delay()
        local now = os.date("*t")
        local target = os.time({
            year = now.year,
            month = now.month,
            day = now.day,
            hour = hour,
            min = minute,
            sec = 0
        })
        
        -- If target time has passed today, schedule for tomorrow
        if target <= os.time() then
            target = target + 24 * 60 * 60  -- Add 24 hours
        end
        
        return (target - os.time()) * 1000  -- Convert to milliseconds
    end
    
    local function schedule_next()
        local delay = calculate_delay()
        print(string.format("Next task scheduled in %.1f hours", delay / 1000 / 60 / 60))
        
        setTimeout(function()
            print(string.format("Executing daily task at %02d:%02d", hour, minute))
            task()
            schedule_next()  -- Schedule next occurrence
        end, delay)
    end
    
    schedule_next()
end

-- Usage example: Daily backup at 2:30 AM
schedule_daily(2, 30, function()
    print("Running daily backup...")
    -- Backup logic here
    print("✓ Daily backup completed")
end)
```

### Cron-like Scheduling

```lua
local function create_scheduler()
    local jobs = {}
    
    local function check_jobs()
        local now = os.date("*t")
        
        for _, job in ipairs(jobs) do
            if job.hour == now.hour and job.min == now.min and job.sec == now.sec then
                if not job.last_run or job.last_run < os.time() - 60 then  -- Prevent double execution
                    job.last_run = os.time()
                    job.task()
                end
            end
        end
    end
    
    -- Check every second
    setInterval(check_jobs, 1000)
    
    return {
        add_job = function(hour, minute, second, task)
            table.insert(jobs, {
                hour = hour,
                min = minute,
                sec = second,
                task = task,
                last_run = 0
            })
        end
    }
end

-- Usage example
local scheduler = create_scheduler()

scheduler.add_job(14, 30, 0, function()  -- 2:30:00 PM
    print("Afternoon reminder: Time for a break!")
end)

scheduler.add_job(9, 0, 0, function()   -- 9:00:00 AM
    print("Good morning! Starting daily routines...")
end)
```

## 🧪 Testing Examples

### Timer Accuracy Test

```lua
local function test_timer_accuracy()
    local delays = {100, 500, 1000, 2000, 5000}
    
    for _, delay in ipairs(delays) do
        local start_time = os.time() * 1000
        
        setTimeout(function()
            local actual_delay = (os.time() * 1000) - start_time
            local accuracy = math.abs(actual_delay - delay)
            
            print(string.format("Expected: %dms, Actual: %dms, Accuracy: ±%dms", 
                  delay, actual_delay, accuracy))
        end, delay)
    end
end

test_timer_accuracy()
```

### Memory Leak Test

```lua
local function test_timer_cleanup()
    local timer_count = 0
    
    -- Create and cancel many timers
    for i = 1, 1000 do
        local timer_id = setTimeout(function()
            print("This should not execute")
        end, 60000)  -- 1 minute
        
        -- Cancel immediately
        clearTimeout(timer_id)
        timer_count = timer_count + 1
        
        if timer_count % 100 == 0 then
            print("Created and cancelled", timer_count, "timers")
        end
    end
    
    print("✓ Timer cleanup test completed")
end

test_timer_cleanup()
```

## 💡 Best Practices

### Timer Management
```lua
-- Keep track of active timers for cleanup
local active_timers = {}

local function managed_setTimeout(callback, delay)
    local timer_id = setTimeout(function()
        active_timers[timer_id] = nil  -- Remove from tracking
        callback()
    end, delay)
    
    active_timers[timer_id] = true
    return timer_id
end

local function cleanup_all_timers()
    for timer_id, _ in pairs(active_timers) do
        clearTimeout(timer_id)
    end
    active_timers = {}
    print("✓ All timers cleaned up")
end

-- Cleanup on program exit
-- cleanup_all_timers()
```

### Error Handling
```lua
-- Wrap timer callbacks with error handling
local function safe_setTimeout(callback, delay)
    return setTimeout(function()
        local success, error_msg = pcall(callback)
        if not success then
            print("Timer callback error:", error_msg)
        end
    end, delay)
end

-- Usage
safe_setTimeout(function()
    error("This error won't crash the program")
end, 1000)
```

### Resource Management
```lua
-- Limit concurrent timers to prevent resource exhaustion
local max_concurrent_timers = 100
local active_timer_count = 0

local function throttled_setTimeout(callback, delay)
    if active_timer_count >= max_concurrent_timers then
        print("Warning: Maximum timer limit reached")
        return nil
    end
    
    active_timer_count = active_timer_count + 1
    
    return setTimeout(function()
        active_timer_count = active_timer_count - 1
        callback()
    end, delay)
end
```

## 🚀 Advanced Examples

See the [examples directory](../../examples/) for more comprehensive timer examples including:
- Game loops and animation timers
- Data polling and synchronization
- Distributed task scheduling
- Real-time monitoring systems
