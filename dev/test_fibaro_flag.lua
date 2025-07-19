-- test_fibaro_flag.lua
-- Test script to verify that Fibaro support is loaded

print("Testing Fibaro functionality...")

-- Check if fibaro global is available
if fibaro then
    print("✓ fibaro global table is available")
else
    print("✗ fibaro global table is NOT available")
end

-- Check if api global is available
if api then
    print("✓ api global table is available")
    print("  api.get: " .. type(api.get))
    print("  api.post: " .. type(api.post))
    print("  api.put: " .. type(api.put))
    print("  api.delete: " .. type(api.delete))
else
    print("✗ api global table is NOT available")
end

-- Check if fibaro API hook is available
if _PY and _PY.fibaro_api_hook then
    print("✓ _PY.fibaro_api_hook is available")
    print("  Type: " .. type(_PY.fibaro_api_hook))
else
    print("✗ _PY.fibaro_api_hook is NOT available")
end

-- Test the main_file_hook override
if _PY and _PY.main_file_hook then
    print("✓ _PY.main_file_hook is available (should be overridden by fibaro.lua)")
    print("  Type: " .. type(_PY.main_file_hook))
else
    print("✗ _PY.main_file_hook is NOT available")
end

print("Fibaro test completed!")
