-- Test script for new window management features
-- This script tests window reuse, position persistence, and granular window control

print("=== Testing Window Management Features ===")

-- Test 1: Open a window for QA 100
print("\n1. Opening window for QA 100...")
local result1 = _PY.open_quickapp_window(100, "Test QA 100", 600, 400)
print("Result:", json.encode(result1))

-- Test 2: Try to open the same window again (should reuse)
print("\n2. Opening same QA 100 again (should reuse)...")
local result2 = _PY.open_quickapp_window(100, "Test QA 100", 600, 400) 
print("Result:", json.encode(result2))

-- Test 3: Force new window for same QA
print("\n3. Forcing new window for QA 100...")
local result3 = _PY.open_quickapp_window(100, "Test QA 100 New", 600, 400, nil, nil, true)
print("Result:", json.encode(result3))

-- Test 4: Open window with specific position
print("\n4. Opening QA 200 with specific position...")
local result4 = _PY.open_quickapp_window(200, "Test QA 200", 500, 300, 200, 150)
print("Result:", json.encode(result4))

-- Test 5: List all windows
print("\n5. Listing all windows...")
local windows = _PY.list_quickapp_windows()
print("Windows:", json.encode(windows))

-- Test 6: Close specific QA window
print("\n6. Closing window for QA 200...")
local close_result = _PY.close_quickapp_window(200)
print("Close result:", json.encode(close_result))

-- Test 7: List windows again
print("\n7. Listing windows after closing QA 200...")
local windows2 = _PY.list_quickapp_windows()
print("Windows:", json.encode(windows2))

-- Wait a bit for user to see the windows
print("\n8. Waiting 5 seconds for you to see the windows...")
_PY.sleep(5)

-- Test 8: Close all windows
print("\n9. Closing all windows...")
local close_all = _PY.close_all_quickapp_windows()
print("Close all result:", json.encode(close_all))

print("\n=== Test completed ===")
