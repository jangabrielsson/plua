-- Native UI Demo - Working Visual Interface
-- Shows a fully functional native tkinter UI built from JSON

local nativeUI = require('native_ui')

print("🎛️ EPLua Native UI - Visual Demo")

-- Check if native UI is available
if not nativeUI.isAvailable() then
    print("❌ Native UI not available on this system")
    return
end

print("✅ Native UI available!")

-- Create the main window
print("\n📝 Creating QuickApp-style interface...")

local mainWindow = nativeUI.createWindow("QuickApp Device 5555", 450, 650)

-- Build a comprehensive UI
local ui = nativeUI.quickUI()
    :header("Device Control Panel", 1)
    :label("Status: Connected ✅")
    :separator()
    :label("Current Level: 25%")
    :button("Turn On", "turn_on", true)  -- Primary button
    :button("Turn Off", "turn_off", false)
    :separator()
    :slider("Brightness", 0, 100, 75)
    :separator()
    :label("Mode Settings")
    :dropdown("Operation Mode", {"Auto", "Manual", "Schedule", "Off"}, "Auto")
    :multiselect("Features", {"Timer", "Sensor", "Remote", "Logging"}, {"Timer", "Sensor"}, 2)
    :separator()
    :slider("Volume", 0, 100, 50)
    :switch("Night Mode", false)
    :separator()
    :button("Apply Settings", "apply")
    :button("Reset", "reset")
    :button("Info", "info")
    :build()

-- Set the UI and show
mainWindow:setUI(ui):show()

print("✅ QuickApp interface created and displayed!")
print("📝 Window ID:", mainWindow:getId())

-- Create a second demo window
print("\n🎯 Creating settings window...")

local settingsWindow = nativeUI.createWindow("Device Settings", 400, 500)

local settingsUI = nativeUI.quickUI()
    :header("Advanced Settings", 2)
    :separator()
    :label("Network Configuration")
    :dropdown("WiFi Network", {"Home_Network", "Office_WiFi", "Guest"}, "Home_Network")
    :switch("Auto Connect", true)
    :separator()
    :label("Device Preferences")
    :slider("Update Frequency", 1, 60, 15)
    :multiselect("Log Types", {"Error", "Warning", "Info", "Debug"}, {"Error", "Warning"}, 4)
    :separator()
    :label("Security")
    :switch("Enable Encryption", true)
    :switch("Require Authentication", false)
    :separator()
    :button("Save Configuration", "save", true)
    :button("Cancel", "cancel")
    :build()

settingsWindow:setUI(settingsUI):show()

print("✅ Settings window created!")

-- Show all windows
print("\n📋 Current native windows:")
print(nativeUI.listWindows())

print("\n🎉 Native UI Demo complete!")
print("💡 Both windows should now be visible with native tkinter controls.")
print("🎛️ All UI elements are functional - sliders, dropdowns, switches work!")
print("🔧 This demonstrates a complete native UI solution without HTML.")
print("\n📚 Features demonstrated:")
print("  ✅ Headers and labels")
print("  ✅ Primary and secondary buttons") 
print("  ✅ Sliders with ranges")
print("  ✅ Dropdown menus")
print("  ✅ Multi-select lists")
print("  ✅ Toggle switches")
print("  ✅ Visual separators")
print("  ✅ Method chaining")
print("  ✅ JSON-based UI descriptions")

-- Keep the demo running
setInterval(function() end, 5000)
