-- Test just the Fibaro API hook directly
print("Testing direct Fibaro API hook...")

if _PY.fibaro_api_hook then
    print("fibaro_api_hook is available")
    
    local result = _PY.fibaro_api_hook("GET", "/api/devices", nil)
    print("Direct hook result type:", type(result))
    
    if type(result) == "table" then
        print("Hook returned a table (success)")
        -- Try to examine the table content
        for k, v in pairs(result) do
            print("  result[" .. tostring(k) .. "] = " .. tostring(v))
        end
    else
        print("Hook returned:", result)
    end
else
    print("fibaro_api_hook is not available")
end

print("Script completed successfully")
