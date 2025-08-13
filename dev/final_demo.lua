-- Native UI Demo - QuickApp Style Interface (With Working Callbacks!)
-- Demonstrates button row functionality with full callback support

local nativeUI = require('native_ui')
local json = require('json')

print("🎛️ EPLua Native UI Demo (Button Row Demo)")

-- Check if native UI is available
if not nativeUI.isAvailable() then
    print("❌ Native UI not available on this system")
    return
end

print("✅ Native UI available!")

-- Create the main window
print("\n📝 Creating QuickApp-style window...")

local mainWindow = nativeUI.createWindow("QuickApp 5555 - Button Row Demo", 400, 600)

-- Build UI using the quick builder with button row
local ui = nativeUI.quickUI()
    :label("=== QuickApp 5555 ===", "main_title")
    :label("Connected ✅", "connection_status")
    :separator("sep1")
    :label("Current Value: 25", "value_display")
    :button("Turn On", "turn_on", true, "turn_on_btn")
    :button("Turn Off", "turn_off", false, "turn_off_btn")
    :slider("Level", 0, 100, 25, "level_slider")
    :separator("sep2")
    :label("Status: Ready", "device_status")
    
    -- NEW: Button Row with 4 action buttons
    :buttonRow({
        {text = "Btn 1", action = "btn1", id = "action_btn1"},
        {text = "Btn 2", action = "btn2", id = "action_btn2"},
        {text = "Btn 3", action = "btn3", id = "action_btn3"},
        {text = "Btn 5", action = "btn5", id = "action_btn5"}
    }, "action_buttons_row")
    
    :separator("sep3")
    :slider("Secondary", 0, 100, 50, "secondary_slider")
    :dropdown("Mode", {"Auto", "Manual", "Off"}, "Auto", "mode_dropdown")
    
    -- Examples of different button row configurations
    :separator("sep4")
    :label("Button Row Examples:", "examples_label")
    
    -- 2 button row
    :label("Two Buttons:", "two_label")
    :buttonRow({"Save", "Cancel"}, "save_cancel_row")
    
    -- 3 button row with mixed styles
    :label("Three Mixed Buttons:", "three_label")
    :buttonRow({
        {text = "Primary", isPrimary = true, id = "primary_ex"},
        {text = "Normal", id = "normal_ex"},
        {text = "Action", id = "action_ex"}
    }, "mixed_row")
    
    -- 5 button row
    :label("Five Buttons:", "five_label")
    :buttonRow({"A", "B", "C", "D", "E"}, "five_row")
    
    :build()

-- Set the UI
mainWindow:setUI(ui)

-- Setup callbacks for all interactive elements
print("🔧 Setting up callbacks...")

-- Main control callbacks
mainWindow:setCallback("turn_on_btn", function(data)
    print("🟢 Turn On pressed!")
    mainWindow:setValue("connection_status", "Device ON ✅")
    mainWindow:setValue("device_status", "Status: Device is ON")
end)

mainWindow:setCallback("turn_off_btn", function(data)
    print("🔴 Turn Off pressed!")
    mainWindow:setValue("connection_status", "Device OFF ❌")
    mainWindow:setValue("device_status", "Status: Device is OFF")
end)

-- Slider callbacks
mainWindow:setCallback("level_slider", function(data)
    local value = data and data.data and data.data.value or "unknown"
    print("🎚️ Level slider changed to:", value)
    mainWindow:setValue("value_display", "Current Value: " .. value)
end)

mainWindow:setCallback("secondary_slider", function(data)
    local value = data and data.data and data.data.value or "unknown"
    print("🎚️ Secondary slider changed to:", value)
end)

-- Dropdown callback
mainWindow:setCallback("mode_dropdown", function(data)
    local value = data and data.data and data.data.value or "unknown"
    print("📋 Mode changed to:", value)
    mainWindow:setValue("device_status", "Status: Mode set to " .. value)
end)

-- Action button row callbacks
mainWindow:setCallback("action_btn1", function(data)
    print("🎯 Action Button 1 clicked!")
    mainWindow:setValue("device_status", "Status: Action 1 executed")
end)

mainWindow:setCallback("action_btn2", function(data)
    print("🎯 Action Button 2 clicked!")
    mainWindow:setValue("device_status", "Status: Action 2 executed")
end)

mainWindow:setCallback("action_btn3", function(data)
    print("🎯 Action Button 3 clicked!")
    mainWindow:setValue("device_status", "Status: Action 3 executed")
end)

mainWindow:setCallback("action_btn5", function(data)
    print("🎯 Action Button 5 clicked!")
    mainWindow:setValue("device_status", "Status: Action 5 executed")
end)

-- Example button rows callbacks
mainWindow:setCallback("save_cancel_row", function(data)
    local button = data and data.button or "unknown"
    print("💾 Save/Cancel row - Button clicked:", button)
    if button == "Save" then
        mainWindow:setValue("device_status", "Status: Settings saved!")
    elseif button == "Cancel" then
        mainWindow:setValue("device_status", "Status: Changes cancelled")
    end
end)

mainWindow:setCallback("mixed_row", function(data)
    local button = data and data.button or "unknown"
    print("🔘 Mixed row - Button clicked:", button)
    mainWindow:setValue("device_status", "Status: " .. button .. " action")
end)

mainWindow:setCallback("five_row", function(data)
    local button = data and data.button or "unknown"
    print("🔤 Five row - Button clicked:", button)
    mainWindow:setValue("device_status", "Status: Button " .. button .. " pressed")
end)

-- Show the window
mainWindow:show()

print("✅ QuickApp window created and displayed!")
print("📝 Window ID:", mainWindow:getId())

print("\n🎉 Button Row Demo complete!")
print("💡 Window shows various button row configurations:")
print("   🔸 4-button action row (Btn 1, Btn 2, Btn 3, Btn 5)")
print("   🔸 2-button row (Save, Cancel)")
print("   🔸 3-button mixed styles row (Primary highlighted)")
print("   🔸 5-button row (A, B, C, D, E)")
print("🎛️ This demonstrates horizontal button layout with working callbacks!")
print("\n💡 Try interacting with the controls:")
print("   🔘 Click buttons to see callback responses")
print("   🎚️ Move sliders to update values")
print("   📋 Change dropdown to see status updates")

-- Keep the script running
setInterval(function()
    -- Could update UI elements here when callbacks are working
end, 5000)
