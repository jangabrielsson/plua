-- Test _PY.config to show available fields
print("=== _PY.config Structure ===")

local config = _PY.config
if config then
    print("Available config fields:")
    
    -- Collect and sort keys
    local keys = {}
    for key, _ in pairs(config) do
        table.insert(keys, key)
    end
    table.sort(keys)
    
    -- Display all fields with their types and values
    for _, key in ipairs(keys) do
        local value = config[key]
        local value_type = type(value)
        local value_str = tostring(value)
        
        -- Truncate long values
        if string.len(value_str) > 50 then
            value_str = string.sub(value_str, 1, 47) .. "..."
        end
        
        print(string.format("  %-20s: %-15s (%s)", key, value_str, value_type))
    end
else
    print("No config data available")
end
