-- Browser Window Manager Demo
-- This demo shows how to create and manage external browser windows

local json = require("json")

print("🌐 Browser Window Manager Demo")
print("================================")

-- Test basic window creation
print("\n📝 Testing basic window creation...")
local result = _PY.create_browser_window("test_window", "https://httpbin.org/html", 600, 400, 50, 50)
print("Create window result:", result)

-- Wait a moment
_PY.sleep(2)

-- Test window URL setting
print("\n🔗 Testing URL setting...")
local url_result = _PY.set_browser_window_url("test_window", "https://httpbin.org/json")
print("Set URL result:", url_result)

-- Wait a moment
_PY.sleep(2)

-- Test advanced window creation with positioning
print("\n🎯 Testing advanced window creation...")
local success = _PY.create_browser_window("demo_window", "https://httpbin.org/html", 800, 600, 200, 150)
print("Advanced window created:", success)

-- Wait a moment
_PY.sleep(2)

-- Test window info
print("\n📊 Testing window info...")
local info = _PY.get_browser_window_info("demo_window")
if info then
    print("Window info:", json.encode(info))
else
    print("No window info available")
end

-- Test listing windows
print("\n📋 Listing all windows...")
local windows = _PY.list_browser_windows()
if windows then
    print("All windows:", json.encode(windows))
else
    print("No windows found")
end

-- Test URL change
print("\n🔄 Testing URL change...")
local change_result = _PY.set_browser_window_url("demo_window", "https://httpbin.org/user-agent")
print("URL change result:", change_result)

-- Keep the demo alive for a bit to see the windows
print("\n⏱️  Keeping demo alive for 10 seconds...")
print("You should see browser windows open. Press Ctrl+C to exit early.")

-- Use a timer to keep the script alive and then clean up
local cleanup_timer
cleanup_timer = setTimeout(function()
    print("\n🧹 Cleaning up...")
    
    -- Close specific windows
    local close1 = _PY.close_browser_window("test_window")
    local close2 = _PY.close_browser_window("demo_window")
    print("Closed test_window:", close1)
    print("Closed demo_window:", close2)
    
    -- Alternative: close all windows at once
    -- local close_all = _PY.close_all_browser_windows()
    -- print("Closed all windows:", close_all)
    
    print("✅ Demo completed!")
    clearTimeout(cleanup_timer)
end, 10000)

print("Demo running... browser windows should appear!")
