-- Test script to verify that loadPythonModule works in compiled Nuitka app
print("Testing Python module loading...")

-- Test loading each pylib module
local modules_to_test = {
    "http_client",
    "websocket_client", 
    "udp_client",
    "mqtt_client",
    "filesystem",
    "tcp_client"
}

local success_count = 0
local total_count = #modules_to_test

for _, module_name in ipairs(modules_to_test) do
    print(string.format("Loading module: %s", module_name))
    
    local success, result = pcall(function()
        return loadPythonModule(module_name)
    end)
    
    if success then
        print(string.format("  ✓ Successfully loaded %s", module_name))
        success_count = success_count + 1
        
        -- Try to inspect the module a bit
        if type(result) == "table" then
            local func_count = 0
            for k, v in pairs(result) do
                if type(v) == "function" then
                    func_count = func_count + 1
                end
            end
            print(string.format("    Module has %d functions", func_count))
        end
    else
        print(string.format("  ✗ Failed to load %s: %s", module_name, tostring(result)))
    end
end

print(string.format("\nResults: %d/%d modules loaded successfully", success_count, total_count))

if success_count == total_count then
    print("🎉 All Python modules loaded successfully!")
    return 0
else
    print("❌ Some modules failed to load")
    return 1
end
