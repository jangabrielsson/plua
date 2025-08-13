-- Network Module Dynamic Loading Demo
-- Shows how to dynamically load different Python modules for network functionality

print("=== Network Module Dynamic Loading Demo ===")

-- Function to safely load and test a module
local function test_module_loading(module_name, test_function)
    print(string.format("\nLoading %s module:", module_name))
    local module_funcs = _PY.loadPythonModule(module_name)
    
    if module_funcs.error then
        print("  ✗ Error: " .. module_funcs.error)
        return nil
    end
    
    print("  ✓ Module loaded successfully!")
    print("  Available functions:")
    local func_names = {}
    for name, func in pairs(module_funcs) do
        table.insert(func_names, name)
    end
    table.sort(func_names)
    
    for _, name in ipairs(func_names) do
        print("    - " .. name)
    end
    
    -- Run optional test function
    if test_function then
        print("  Testing functionality:")
        local success, result = pcall(test_function, module_funcs)
        if success then
            print("    ✓ Test passed: " .. (result or "OK"))
        else
            print("    ✗ Test failed: " .. result)
        end
    end
    
    return module_funcs
end

-- Test different network modules
test_module_loading("http_client", function(funcs)
    -- Test if the HTTP client functions are available
    if funcs.create_http_client then
        return "HTTP client functions available"
    else
        error("HTTP client functions not found")
    end
end)

test_module_loading("tcp", function(funcs)
    -- Test if TCP functions are available
    if funcs.tcp_create_server then
        return "TCP server functions available"
    else
        error("TCP functions not found")
    end
end)

test_module_loading("websocket", function(funcs)
    -- Test if WebSocket functions are available
    if funcs.websocket_create_client then
        return "WebSocket client functions available"
    else
        error("WebSocket functions not found")
    end
end)

test_module_loading("mqtt", function(funcs)
    -- Test if MQTT functions are available
    if funcs.mqtt_create_client then
        return "MQTT client functions available"
    else
        error("MQTT functions not found")
    end
end)

-- Test the filesystem module that we know works
test_module_loading("filesystem", function(funcs)
    local current_dir = funcs.fs_currentdir()
    return "Current directory: " .. current_dir
end)

print("\n" .. string.rep("=", 60))
print("Dynamic Loading Summary:")
print("✓ Modules can be loaded on demand, similar to FFI")
print("✓ Each module provides its own set of functions")
print("✓ Functions are immediately available after loading")
print("✓ Error handling for missing or failed modules")
print("✓ Clean separation between Python implementation and Lua API")
print("\nThis approach allows:")
print("• Lua scripts to only load what they need")
print("• Python modules to be developed independently")
print("• Easy testing and debugging of individual modules")
print("• Memory efficiency - unused modules aren't loaded")
print("• Hot-reloading during development")
