-- Test the AppleScript-based window creation
print("=== Testing AppleScript Window Creation ===")

-- Close any existing browser windows first
print("1. Closing all existing browser windows...")
local close_result = _PY.close_all_browser_windows()
print("Close all result:", close_result)

_PY.sleep(2)

-- Test 1: Create first window
print("2. Creating first browser window...")
local success1 = _PY.create_browser_window(
    "applescript_test_1", 
    "http://localhost:8080/static/quickapp_ui.html?qa_id=2001&desktop=true",
    600, 
    400, 
    100, 
    100
)
print("Window 1 creation:", success1)

_PY.sleep(4)

-- Test 2: Create second window
print("3. Creating second browser window...")
local success2 = _PY.create_browser_window(
    "applescript_test_2", 
    "http://localhost:8080/static/quickapp_ui.html?qa_id=2002&desktop=true",
    600, 
    400, 
    300, 
    200
)
print("Window 2 creation:", success2)

_PY.sleep(4)

-- Test 3: Create third window
print("4. Creating third browser window...")
local success3 = _PY.create_browser_window(
    "applescript_test_3", 
    "http://localhost:8080/static/quickapp_ui.html?qa_id=2003&desktop=true",
    600, 
    400, 
    500, 
    300
)
print("Window 3 creation:", success3)

_PY.sleep(2)

print("=== Check Safari ===")
print("You should see exactly 3 Safari windows:")
print("- Window 1: QA 2001")
print("- Window 2: QA 2002") 
print("- Window 3: QA 2003")
print("NO duplicate tabs should exist!")

-- List windows to verify
local windows = _PY.list_browser_windows()
if windows then
    print("\nManaged windows:")
    for window_id, info in pairs(windows) do
        print(string.format("  %s: %s", window_id, info.url))
    end
end
