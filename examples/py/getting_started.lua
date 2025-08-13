-- Getting Started with EPLua
-- This example demonstrates the basic features of EPLua

print("Welcome to EPLua!")
print("Current time:", _PY.get_time())

-- Basic timers
print("\nSetting up timers...")
_PY.setTimeout(function()
    print("  Timer 1: Hello from 1 second timer!")
end, 1000)

_PY.setTimeout(function()
    print("  Timer 2: Hello from 2 second timer!")
end, 2000)

-- Interval example
local count = 0
local intervalId
intervalId = _PY.setInterval(function()
    count = count + 1
    print("  Interval: Count is", count)
    
    if count >= 3 then
        _PY.clearInterval(intervalId)
        print("  Interval stopped after 3 iterations")
    end
end, 500)

-- Platform information
local platform = _PY.get_platform()
print("\nPlatform Info:")
print("  System:", platform.system)
print("  Machine:", platform.machine)

-- Simple math
print("\nMath examples:")
print("  5 + 10 =", _PY.math_add(5, 10))
print("  Random number:", _PY.random_number(1, 100))

-- File operations
local content = "Hello from EPLua! Time: " .. os.date("%Y-%m-%d %H:%M:%S")
local write_success = _PY.write_file("getting_started_output.txt", content)
print("\nFile operations:")
print("  Write success:", write_success)

if write_success then
    local read_content = _PY.read_file("getting_started_output.txt")
    print("  File content:", read_content)
end

print("\nAll examples complete! Waiting for timers to finish...")
