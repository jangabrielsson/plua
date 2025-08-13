-- HTTP Module Demo
-- Shows how to use the dynamically-loaded HTTP module

local http = require("examples.lua.http")

print("=== HTTP Module Dynamic Loading Demo ===")

-- List available functions
print("\nAvailable HTTP functions:")
local functions = http.list_functions()
for _, name in ipairs(functions) do
    print("  - " .. name)
end

-- Test with a simple HTTP request (we'll use httpbin.org as it's reliable for testing)
print("\nTesting HTTP GET request...")

local success, result = pcall(function()
    return http.get("https://httpbin.org/json")
end)

if success and result then
    print("✓ HTTP request successful!")
    
    -- Parse and display some of the response
    if type(result) == "table" then
        print("Response type: table")
        if result.status then
            print("Status: " .. tostring(result.status))
        end
        if result.body then
            local body_preview = string.sub(tostring(result.body), 1, 100)
            print("Body preview: " .. body_preview .. "...")
        end
    else
        print("Response: " .. tostring(result))
    end
else
    print("✗ HTTP request failed: " .. tostring(result))
    print("(This might be expected if there's no internet connection)")
end

print("\n" .. string.rep("=", 50))
print("HTTP Module Summary:")
print("✓ HTTP client module loaded dynamically")
print("✓ Clean Lua API wrapping Python HTTP functionality")
print("✓ Error handling for network issues")
print("✓ Modular design - can be extended with more HTTP features")
print("\nThis demonstrates how:")
print("• Complex Python networking can be wrapped in simple Lua APIs")
print("• Modules can be composed from dynamically loaded components")
print("• Each module handles its own loading and error management")
print("• The same pattern works for any Python backend functionality")
