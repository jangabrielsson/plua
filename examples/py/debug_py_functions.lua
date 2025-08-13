-- Test what functions are available in _PY
print("Checking available functions in _PY:")

if _PY then
    for key, value in pairs(_PY) do
        print("  " .. key .. ": " .. type(value))
    end
else
    print("_PY table not found!")
end

-- Test if registerCallback is available
if _PY and _PY.registerCallback then
    print("registerCallback is available")
    
    -- Test registering a callback
    local callback_id = _PY.registerCallback(function(err, data)
        print("Test callback called with:", err, data)
    end)
    print("Registered callback with ID:", callback_id)
else
    print("registerCallback not available")
end
