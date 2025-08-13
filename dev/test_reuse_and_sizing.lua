-- Test window reuse and sizing fixes
print("=== Testing Window Reuse and Sizing ===")

-- Test 1: Create first window with specific size
print("1. Creating first window (500x400 at 100,100)...")
local success1 = _PY.create_browser_window(
    "reuse_test_1", 
    "http://localhost:8080/static/quickapp_ui.html?qa_id=4001&desktop=true",
    500, 
    400, 
    100, 
    100
)
print("Window 1 creation:", success1)

_PY.sleep(3)

-- Test 2: Create second window with different size
print("2. Creating second window (600x500 at 300,200)...")
local success2 = _PY.create_browser_window(
    "reuse_test_2", 
    "http://localhost:8080/static/quickapp_ui.html?qa_id=4002&desktop=true",
    600, 
    500, 
    300, 
    200
)
print("Window 2 creation:", success2)

_PY.sleep(3)

-- Test 3: Try to reuse first window (should reuse, not create new)
print("3. Trying to reuse first window (should reuse existing)...")
local success3 = _PY.create_browser_window(
    "reuse_test_1",  -- Same window ID as test 1
    "http://localhost:8080/static/quickapp_ui.html?qa_id=4001&desktop=true",
    700,  -- Different size
    600, 
    400,  -- Different position
    300
)
print("Window 1 reuse:", success3)

_PY.sleep(2)

-- Test 4: Try to reuse second window  
print("4. Trying to reuse second window (should reuse existing)...")
local success4 = _PY.create_browser_window(
    "reuse_test_2",  -- Same window ID as test 2
    "http://localhost:8080/static/quickapp_ui.html?qa_id=4002&desktop=true",
    800,  -- Different size
    700,
    500,  -- Different position  
    400
)
print("Window 2 reuse:", success4)

_PY.sleep(2)

-- List windows
print("5. Final window list:")
local windows = _PY.list_browser_windows()
if windows then
    for window_id, info in pairs(windows) do
        print(string.format("  %s: %dx%d at %d,%d", window_id, info.width, info.height, info.x, info.y))
    end
end

print("\n=== Expected Results ===")
print("✅ Only 2 Safari windows should exist (not 4)")
print("✅ Windows should be sized as specified")
print("✅ Window reuse should work for same window_id")
print("✅ Different window_ids should create separate windows")
