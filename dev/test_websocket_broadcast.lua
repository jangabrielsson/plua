-- Test WebSocket broadcasting
print("Testing WebSocket broadcast system...")

-- Test broadcast_view_update function
if _PY.broadcast_view_update then
    print("✅ broadcast_view_update is available")
    
    -- Try to broadcast a test update
    local success = _PY.broadcast_view_update(5555, "test_label", "text", "Hello from Lua!")
    print("Broadcast result:", success)
    
    -- Try another broadcast
    success = _PY.broadcast_view_update(5555, "button1", "color", "red")
    print("Second broadcast result:", success)
    
else
    print("❌ broadcast_view_update is NOT available")
end

print("WebSocket broadcast test completed")
