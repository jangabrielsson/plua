-- Test cross-session window reuse
print("=== Testing Cross-Session Window Reuse ===")

-- Test creating a QuickApp window that should be reused across restarts
print("1. Creating QuickApp window for QA 7001...")
local success1 = _PY.create_browser_window(
    "quickapp_7001", 
    "http://localhost:8080/static/quickapp_ui.html?qa_id=7001&desktop=true",
    500, 
    400, 
    100, 
    100
)
print("Window creation:", success1)

_PY.sleep(2)

-- Check window list
print("2. Current windows:")
local windows = _PY.list_browser_windows()
if windows then
    for window_id, info in pairs(windows) do
        print(string.format("  %s: %s (%dx%d)", window_id, info.url, info.width, info.height))
    end
end

print("\n=== Restart Test ===")
print("This simulates what happens when you restart EPLua:")
print("1. Keep the Safari window open")
print("2. Restart this script")
print("3. Try to create the same QuickApp window again")
print("4. It should reuse the existing Safari window, not create a new one")

print("\nWindow created. You can now:")
print("1. Keep the Safari window open")
print("2. Stop this script (Ctrl+C)")  
print("3. Run it again to test reuse")
print("4. The same Safari window should be reused")
