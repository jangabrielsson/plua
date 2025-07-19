-- Test REPL functionality with automated input
-- This script will be used to test basic REPL features

print("Testing REPL features...")

-- Test basic Lua
local x = 42
print("x =", x)

-- Test JSON
local data = {name = "test", value = 123}
local json_str = json.encode(data)
print("JSON:", json_str)

-- Test timers
setTimeout(function()
    print("Timer executed!")
end, 1000)

print("REPL test completed")
