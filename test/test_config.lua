-- Test script for configuration file loading

print("Testing PLua configuration file loading...")

-- Check if pluaconfig is available
if _PY.pluaconfig then
    print("✓ pluaconfig is available")
    
    -- Print the configuration
    print("\nConfiguration contents:")
    _PY.print_table(_PY.pluaconfig)
    
    -- Test accessing specific values
    print("\nTesting specific configuration values:")
    
    if _PY.pluaconfig.app_name then
        print("app_name:", _PY.pluaconfig.app_name)
    else
        print("app_name: not found")
    end
    
    if _PY.pluaconfig.port then
        print("port:", _PY.pluaconfig.port)
    else
        print("port: not found")
    end
    
    if _PY.pluaconfig.local_setting then
        print("local_setting:", _PY.pluaconfig.local_setting)
    else
        print("local_setting: not found")
    end
    
    if _PY.pluaconfig.database then
        print("database.host:", _PY.pluaconfig.database.host)
        print("database.port:", _PY.pluaconfig.database.port)
        print("database.ssl:", _PY.pluaconfig.database.ssl)
    else
        print("database: not found")
    end
    
    if _PY.pluaconfig.api then
        print("api.base_url:", _PY.pluaconfig.api.base_url)
        print("api.version:", _PY.pluaconfig.api.version)
    else
        print("api: not found")
    end
    
    -- Test calling the startup function if it exists
    if _PY.pluaconfig.on_startup and type(_PY.pluaconfig.on_startup) == "function" then
        print("\nCalling on_startup function:")
        _PY.pluaconfig.on_startup()
    else
        print("\non_startup function: not found or not a function")
    end
    
else
    print("✗ pluaconfig is not available")
end

print("\nConfiguration test completed!") 