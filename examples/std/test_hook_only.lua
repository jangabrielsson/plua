print("=== Testing _PY.isRunning Hook ===")

local request_count = 0
local max_requests = 5

net.TCPServer():start("localhost", 9765, function() end)
-- Define a custom isRunning hook
function _PY.isRunning(state)
    print(string.format("isRunning hook called - Timers: %d, Callbacks: %d, Total: %d, Requests: %d", 
        state.active_timers, state.pending_callbacks, state.total_tasks, request_count))
    
    -- Stop when we've processed enough requests and have no pending work
    if request_count >= max_requests and state.total_tasks == 0 then
        print("✅ Script completed successfully - terminating")
        return false  -- Stop running
    end
    
    -- Continue running
    return true
end

setTimeout(function()
    print("⏰ Timer 1 executed after 2 seconds")
end, 20*1000)