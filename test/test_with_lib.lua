-- Test script that demonstrates direct Lua operations
print("=== Testing Direct Lua Operations ===")

-- Note: utils library has been removed
-- This test now demonstrates direct Lua operations and _PY functions

print("Direct Lua operations:")
print("Capitalized:", string.upper("hello world"))
print("Formatted:", "Info: Direct operations working")

-- Create a table directly in Lua
local test_table = {name = "Test", value = 42}
print("Created table:")
for key, value in pairs(test_table) do
  print("  " .. key .. ":", value)
end

-- Test some _PY functions
print("\n--- Testing _PY functions ---")
local hostname = _PY.get_hostname()
print("Hostname:", hostname)

local timestamp = _PY.get_time()
print("Current timestamp:", timestamp)

print("=== Test completed ===")