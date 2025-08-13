-- Final comprehensive test of all functionality
print("=== EPLua Comprehensive Test ===")

-- Test timers
print("\n1. Testing Timers:")
_PY.setTimeout(function()
    print("  ✓ Simple timeout works")
end, 500)

-- Test intervals
local count = 0
local intervalId
intervalId = _PY.setInterval(function()
    count = count + 1
    print("  ✓ Interval tick", count)
    if count >= 2 then
        _PY.clearInterval(intervalId)
        print("  ✓ Interval cleared")
    end
end, 300)

-- Test Lua tables
print("\n2. Testing Lua Tables:")
local platform = _PY.get_platform()
print("  Platform system:", platform.system)
print("  Platform machine:", platform.machine)

local parsed = _PY.parse_json('{"test": true, "numbers": [1,2,3]}')
print("  JSON parsed test:", parsed.test)
print("  JSON first number:", parsed.numbers[1])

-- Test file operations
print("\n3. Testing File Operations:")
local write_ok = _PY.write_file("comprehensive_test.txt", "EPLua works great!")
print("  File write:", write_ok and "✓ SUCCESS" or "✗ FAILED")

if write_ok then
    local content = _PY.read_file("comprehensive_test.txt")
    print("  File read:", content)
end

-- Test utility functions
print("\n4. Testing Utilities:")
print("  Math 10+15:", _PY.math_add(10, 15))
print("  Random 50-100:", _PY.random_number(50, 100))
print("  Current time:", _PY.get_time())

-- Test system info
print("\n5. Testing System Info:")
local sysinfo = _PY.get_system_info()
print("  Python version:", sysinfo.platform.python_version)
print("  Current user:", sysinfo.environment.user)
print("  Process PID:", sysinfo.runtime.pid)

-- Test directory listing
print("\n6. Testing Directory:")
local dir = _PY.list_directory(".")
print("  Directory entries:", dir.count)

print("\n=== All Tests Complete ===")
print("Waiting for timers to finish...")
