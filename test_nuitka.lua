-- Test script for Nuitka build
print("Testing Nuitka PLua build...")
print("Lua version:", _VERSION)
print("Platform:", _PY and _PY.platform or "unknown")

-- Test basic timer
setTimeout(function()
    print("✓ Timer functionality works")
end, 50)

-- Test HTTP functionality if available
if _PY and _PY.http then
    print("✓ HTTP module available")
end

-- Test JSON functionality
local json = require('json')
local test_table = {name = "test", value = 42}
local json_str = json.encode(test_table)
local decoded = json.decode(json_str)
print("✓ JSON encode/decode works:", decoded.name, decoded.value)

print("Nuitka build test completed!")
