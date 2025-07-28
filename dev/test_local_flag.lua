-- Test script to verify --local flag propagation
print("=== Testing --local Flag Propagation ===")

-- Check if runtime_config exists
if _PY and _PY.config and _PY.config.runtime_config then
    print("✅ runtime_config found")
    
    -- Check the local flag (using ['local'] since 'local' is a Lua keyword)
    local localFlag = _PY.config.runtime_config['local']
    print("runtime_config.local =", localFlag)
    
    if localFlag == true then
        print("✅ --local flag is enabled (true)")
    elseif localFlag == false then
        print("⚠️  --local flag is disabled (false)")
    else
        print("❌ --local flag is not set or has unexpected value:", localFlag)
    end
    
    -- Print all runtime_config for debugging
    print("\nAll runtime_config values:")
    for key, value in pairs(_PY.config.runtime_config) do
        print("  " .. tostring(key) .. " = " .. tostring(value))
    end
else
    print("❌ runtime_config not found")
end

print("=== Test Complete ===")
