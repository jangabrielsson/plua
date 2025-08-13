-- Test to see what _PY functions are available
print("Available _PY functions:")
for name, func in pairs(_PY) do
    print("  " .. name .. " : " .. type(func))
end

-- Test if broadcast_view_update exists
if _PY.broadcast_view_update then
    print("\n✅ broadcast_view_update is available")
    
    -- Try to call it
    local success = _PY.broadcast_view_update(5555, "test_element", "text", "test_value")
    print("Broadcast result:", success)
else
    print("\n❌ broadcast_view_update is NOT available")
end
