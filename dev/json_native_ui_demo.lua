-- Enhanced Native UI Demo - JSON Format Example
-- Shows how to use JSON format and better ID management

local nativeUI = require('native_ui')
local json = require('json')

print("🎛️ JSON Native UI Demo")

if not nativeUI.isAvailable() then
    print("❌ Native UI not available")
    return
end

print("✅ Native UI available!")

-- Example 1: JSON format (what you requested)
print("\n📝 Creating QuickApp from JSON...")

local quickAppJSON = json.encode({
    elements = {
        {
            type = "header",
            text = "QuickApp 5555",
            level = 1,
            id = "title"
        },
        {
            type = "label",
            text = "Connected ✅",
            id = "status"
        },
        {
            type = "separator",
            id = "sep1"
        },
        {
            type = "label",
            text = "Current Value: 0",
            id = "value_display"
        },
        {
            type = "button",
            text = "Turn On",
            action = "turn_on",
            style = { primary = true },
            id = "turn_on_btn"
        },
        {
            type = "button",
            text = "Turn Off", 
            action = "turn_off",
            id = "turn_off_btn"
        },
        {
            type = "slider",
            text = "Level",
            min = 0,
            max = 100,
            value = 25,
            id = "level_slider"
        },
        {
            type = "separator",
            id = "sep2"
        },
        {
            type = "label",
            text = "Status: Ready",
            id = "device_status"
        },
        {
            type = "button",
            text = "Btn 1",
            action = "btn1",
            id = "btn1"
        },
        {
            type = "button",
            text = "Btn 2", 
            action = "btn2",
            id = "btn2"
        },
        {
            type = "button",
            text = "Btn 3",
            action = "btn3", 
            id = "btn3"
        },
        {
            type = "button",
            text = "Btn 5",
            action = "btn5",
            id = "btn5"
        },
        {
            type = "separator",
            id = "sep3"
        },
        {
            type = "slider",
            text = "Secondary",
            min = 0,
            max = 100,
            value = 50,
            id = "secondary_slider"
        },
        {
            type = "dropdown",
            text = "Mode",
            options = {"Auto", "Manual", "Off"},
            value = "Auto",
            id = "mode_select"
        },
        {
            type = "multiselect",
            text = "Options",
            options = {"Feature A", "Feature B", "Feature C", "Debug Mode"},
            values = {"Feature A"},
            height = 3,
            id = "options_multi"
        }
    }
})

-- Create window from JSON
local jsonWindow = nativeUI.createWindow("QuickApp JSON", 400, 600)
local ui = nativeUI.fromJSON(quickAppJSON)
jsonWindow:setUI(ui)

-- Set up interactivity with known IDs
local currentValue = 0
local isOn = false

-- Turn On button - notice we use the exact ID from JSON
jsonWindow:setCallback("turn_on_btn", function(data)
    print("🟢 Turn On clicked (ID: " .. (data.element_id or "turn_on_btn") .. ")")
    isOn = true
    currentValue = jsonWindow:getValue("level_slider") or 50
    
    -- Update the display using the ID
    jsonWindow:setText("value_display", "Current Value: " .. currentValue)
    jsonWindow:setText("device_status", "Status: Device ON")
    print("  Value set to:", currentValue)
end)

-- Turn Off button
jsonWindow:setCallback("turn_off_btn", function(data)
    print("🔴 Turn Off clicked (ID: " .. (data.element_id or "turn_off_btn") .. ")")
    isOn = false
    currentValue = 0
    
    -- Update multiple elements by ID
    jsonWindow:setText("value_display", "Current Value: " .. currentValue)
    jsonWindow:setText("device_status", "Status: Device OFF")
    jsonWindow:setValue("level_slider", 0)
    print("  Value set to:", currentValue)
end)

-- Level slider - get callbacks with element ID
jsonWindow:setCallback("level_slider", function(data)
    local value = data.value or jsonWindow:getValue("level_slider") or 0
    print("🎚️ Level slider changed (ID: " .. (data.element_id or "level_slider") .. ") to:", value)
    if isOn then
        currentValue = value
        jsonWindow:setText("value_display", "Current Value: " .. currentValue)
    end
end)

-- Mode dropdown
jsonWindow:setCallback("mode_select", function(data)
    local mode = data.value or jsonWindow:getValue("mode_select") or "Auto"
    print("⚙️ Mode changed (ID: " .. (data.element_id or "mode_select") .. ") to:", mode)
    jsonWindow:setText("device_status", "Status: Mode = " .. mode)
end)

-- Multi-select
jsonWindow:setCallback("options_multi", function(data)
    local selected = data.values or {}
    print("☑️ Options selected (ID: " .. (data.element_id or "options_multi") .. "):", json.encode(selected))
end)

-- Action buttons with dynamic updates
local buttonActions = {"btn1", "btn2", "btn3", "btn5"}
for _, btnId in ipairs(buttonActions) do
    jsonWindow:setCallback(btnId, function(data)
        local action = data.action or btnId
        print("🔘 Button clicked (ID: " .. (data.element_id or btnId) .. ") action:", action)
        
        -- Update button text to show it was clicked
        jsonWindow:setText(btnId, btnId:upper() .. " ✓")
        
        -- Reset button text after 2 seconds
        setTimeout(function()
            jsonWindow:setText(btnId, btnId:gsub("btn", "Btn "))
        end, 2000)
        
        -- Update status
        jsonWindow:setText("device_status", "Status: " .. action .. " executed")
    end)
end

jsonWindow:show()
print("✅ JSON QuickApp created!")

-- Example 2: Demonstrating real-time updates by ID
print("\n🔄 Setting up real-time updates...")

local updateCount = 0
setInterval(function()
    updateCount = updateCount + 1
    local timestamp = os.date("%H:%M:%S")
    
    -- Update specific elements by their IDs
    jsonWindow:setText("status", "Connected ✅ (Updates: " .. updateCount .. ")")
    
    -- Simulate some changing values
    if updateCount % 3 == 0 then
        local randomValue = math.random(0, 100)
        jsonWindow:setValue("secondary_slider", randomValue)
        jsonWindow:setText("device_status", "Status: Auto-updated " .. timestamp)
    end
    
    print("🔄 Update #" .. updateCount .. " at " .. timestamp)
end, 3000)

print("\n📋 Window created with ID:", jsonWindow:getId())
print("🎉 JSON Native UI Demo complete!")
print("\n✨ Key Features Demonstrated:")
print("   📄 JSON format UI specification")
print("   🏷️ Explicit element IDs for reliable access")
print("   📝 setText() for updating labels/buttons")
print("   🎛️ setValue() for updating sliders/inputs")
print("   📞 Callbacks receive element ID information")
print("   🔄 Real-time updates by element ID")
print("\n💡 All element updates use the exact IDs from the JSON!")
