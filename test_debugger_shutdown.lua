-- Test script to verify debugger shutdown fixes
print("Starting debugger shutdown test...")

-- Create some timers to test cleanup
local timer1 = setTimeout(function()
    print("Timer 1 executed")
end, 2000)

local timer2 = setInterval(function()
    print("Interval timer")
end, 1000)

-- Test desktop UI if available
pcall(function()
    if _PY.open_quickapp_window then
        _PY.open_quickapp_window(1234, "Test Window", 400, 300)
        print("Created test QuickApp window")
    end
end)

-- Add a way to test signal handling
function testSignalHandling()
    print("Testing signal handling...")
    print("Try stopping the debugger with Shift+F5 or Ctrl+C")
    print("The process should shut down cleanly without hanging")
end

-- Create some async activity
local function busyWork()
    for i = 1, 10 do
        print("Working... " .. i)
        setTimeout(function()
            print("Async work " .. i)
        end, i * 500)
    end
end

busyWork()
testSignalHandling()

print("Test setup complete. Try stopping the debugger now.")
print("Expected behavior: Clean shutdown without hanging")
