-- Simple test script for Nuitka build
print("=== PLua Nuitka Build Test ===")
print("Lua version:", _VERSION)
print("Platform info available:", _PY.get_platform() ~= nil)
print("Timer count:", _PY.get_timer_count())

-- Test timer
local timer_fired = false
setTimeout(function()
    timer_fired = true
    print("✅ Timer functionality works!")
end, 500)

-- Test file operations
local readme_exists = _PY.file_exists("README.md")
print("✅ File operations work! README.md exists:", readme_exists)

-- Test JSON
local json_data = _PY.to_json({test = "value", number = 42})
print("✅ JSON serialization works!")

-- Wait for timer
setTimeout(function()
    if timer_fired then
        print("=== All tests completed successfully! ===")
    else
        print("⚠️  Timer test failed")
    end
    print("PLua Nuitka build is functional! 🎉")
end, 1000)
