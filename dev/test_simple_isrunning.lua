-- Simple timer-based test for _PY.isRunning hook
-- Shows how to terminate when all work is done

print("=== Simple Timer Test with isRunning Hook ===")

local tasks_completed = 0
local total_tasks = 3

-- Define isRunning hook - stop when all tasks are done and no timers are pending
function _PY.isRunning(state)
    print(string.format("📊 Runtime state - Timers: %d, Callbacks: %d, Completed: %d/%d", 
        state.active_timers, state.pending_callbacks, tasks_completed, total_tasks))
    
    -- Stop when all tasks are completed and no timers/callbacks are pending
    if tasks_completed >= total_tasks and state.total_tasks == 0 then
        print("✅ All tasks completed - script terminating automatically")
        return false
    end
    
    return true
end

-- Schedule some tasks
setTimeout(function()
    print("🔸 Task 1 completed")
    tasks_completed = tasks_completed + 1
end, 1000)

setTimeout(function()
    print("🔸 Task 2 completed")
    tasks_completed = tasks_completed + 1
end, 3000)

setTimeout(function()
    print("🔸 Task 3 completed")
    tasks_completed = tasks_completed + 1
    print("🎯 All scheduled tasks finished - waiting for auto-termination...")
end, 5000)

print(string.format("Scheduled %d tasks - script will auto-terminate when complete", total_tasks))
