-- Auto-Terminating Script Example
-- Demonstrates the _PY.isRunning hook for automatic script termination
-- 
-- This example shows how to create scripts that automatically terminate
-- when all asynchronous work is complete, eliminating the need to manually
-- place os.exit() calls throughout your code.

print("=== Auto-Terminating Script Example ===")
print("This script will automatically terminate when all tasks are complete.\n")

local tasks_completed = 0
local total_tasks = 3
local start_time = os.time()

-- Define the isRunning hook - this function is called periodically by the runtime
-- to determine if the script should continue running
function _PY.isRunning(state)
    local elapsed = os.time() - start_time
    
    print(string.format("⏱️  [%ds] Runtime check - Timers: %d, Callbacks: %d, Completed: %d/%d", 
        elapsed, state.active_timers, state.pending_callbacks, tasks_completed, total_tasks))
    
    -- Stop when all tasks are completed and no timers/callbacks are pending
    if tasks_completed >= total_tasks and state.total_tasks == 0 then
        print("✅ All tasks completed - script terminating automatically")
        return false  -- Return false to stop the script
    end
    
    -- Optional: Add a safety timeout (uncomment if needed)
    -- if elapsed > 30 then
    --     print("⚠️  Timeout reached - forcing termination")
    --     return false
    -- end
    
    return true  -- Return true to continue running
end

print("Scheduling " .. total_tasks .. " tasks...")

-- Schedule some asynchronous tasks
setTimeout(function()
    print("🔸 Task 1: Initial setup completed")
    tasks_completed = tasks_completed + 1
end, 1000)

setTimeout(function()
    print("🔸 Task 2: Data processing completed")
    tasks_completed = tasks_completed + 1
end, 3000)

setTimeout(function()
    print("🔸 Task 3: Cleanup completed")
    tasks_completed = tasks_completed + 1
    print("🎯 All scheduled tasks finished - waiting for auto-termination...")
end, 5000)

print("\n💡 Key Points:")
print("   • No need to call os.exit() manually")
print("   • Script monitors its own state automatically")
print("   • Terminates cleanly when all work is done")
print("   • Works with timers, HTTP servers, network operations, etc.")
print("\n🚀 Starting tasks...")
