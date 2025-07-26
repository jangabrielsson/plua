-- Simple test for basic window management functionality using browser fallback

print("=== Testing Window Management (Browser Fallback) ===")

-- Test opening a window (will fall back to browser)
print("\n1. Opening window for QA 100...")
local result1 = _PY.open_quickapp_window(100, "Test QA 100", 600, 400)
print("Result:", json.encode(result1))

-- Test listing windows
print("\n2. Listing all windows...")
local windows = _PY.list_quickapp_windows()
print("Windows:", json.encode(windows))

-- Test closing specific window
print("\n3. Closing window for QA 100...")
local close_result = _PY.close_quickapp_window(100)
print("Close result:", json.encode(close_result))

print("\n=== Test completed ===")
