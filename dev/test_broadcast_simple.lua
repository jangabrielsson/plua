-- Test if broadcast_view_update is available and callable
print("🔍 Testing _PY.broadcast_view_update availability...")

if _PY then
    print("✅ _PY namespace is available")
    
    if _PY.broadcast_view_update then
        print("✅ _PY.broadcast_view_update function exists")
        
        -- Test calling it
        print("🔄 Calling broadcast_view_update...")
        local success = _PY.broadcast_view_update(5555, "test_element", "text", "test_value")
        print("📡 Result:", success)
    else
        print("❌ _PY.broadcast_view_update is NOT available")
        print("Available _PY functions:")
        for k, v in pairs(_PY) do
            print("  - " .. k .. " (" .. type(v) .. ")")
        end
    end
else
    print("❌ _PY namespace is NOT available")
end
