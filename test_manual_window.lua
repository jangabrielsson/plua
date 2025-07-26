-- Manual window creation test

print("=== Manual Window Creation Test ===")

-- Try to open a window manually
print("Opening window for QA 4123...")
local result = _PY.open_quickapp_window(4123, "Basic QuickApp", 600, 400)
print("Result:", json.encode(result))

print("Test completed")
