-- Test script for HC3 wake-up functionality
-- This script tests the automatic wake-up feature when HC3 is sleeping

print("Testing HC3 Wake-up Functionality")
print("==================================")

-- Test the wake_network_device function directly
print("\n1. Testing wake_network_device function:")
if _PY.wake_network_device then
    print("Function is available")
    
    -- Test with a known IP/hostname (replace with your HC3's IP)
    local test_host = "192.168.1.76"  -- Replace with your HC3's IP
    print("Testing wake for host: " .. test_host)
    
    local result = _PY.wake_network_device(test_host, 3.0)
    print("Wake result: " .. tostring(result))
else
    print("ERROR: wake_network_device function not available")
end

-- Test if py_sleep function is available
print("\n2. Testing py_sleep function:")
if _PY.py_sleep then
    print("py_sleep function is available")
    print("Testing 500ms sleep...")
    local start_time = _PY.get_time()
    _PY.py_sleep(500)
    local end_time = _PY.get_time()
    print("Slept for: " .. (end_time - start_time) .. "ms")
else
    print("ERROR: py_sleep function not available")
end

-- Test HC3 connectivity if we're in an appropriate environment
print("\n3. Testing HC3 environment:")
print("Checking available globals...")

-- Check if fibaro global is available (indicates HC3 mode)
if fibaro then
    print("Fibaro API is available")
    -- Try a simple API call
    print("Attempting fibaro.getGlobalVariable test...")
    local success, result = pcall(function()
        return fibaro.getGlobalVariable("TEST_VAR")
    end)
    if success then
        print("Fibaro API call successful")
    else
        print("Fibaro API call failed: " .. tostring(result))
    end
else
    print("Fibaro API not available (not in HC3 mode)")
end

print("\nTest completed.")
