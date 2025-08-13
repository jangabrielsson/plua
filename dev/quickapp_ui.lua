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

-- Define UI structure
local ui = {
    type = "frame",
    padding = 20,
    children = {        
        {id = "label1", type = "label", text = "Label: 1"},
        {id = "btn1", type = "button", text = "Button: 1", style = {color = 'blue'}},

        {
          type = "button_row",
          id = "action_buttons", 
          buttons = {
            { text = "Button: 21", action = "primary_action", id = "btn21" },
            { text = "Button: 22", action = "secondary_action", id = "btn22" },
            { text = "Button: 23", action = "cancel_action", id = "btn23" },
            { text = "Button: 24", action = "cancel_action", id = "btn24" },
            { text = "Button: 25", action = "cancel_action", id = "btn25" }
          }
        },
        {
          type = "slider", text = "",
          min = 0, max = 100,value = 25,id = "slider1"
        },
        {
          type = "combobox",
          id = "mode_dropdown",
          text = "Mode",
          options = {"Auto", "Manual", "Off"},
          value = "Auto"
        },
        {
          type = "dropdown_multiselect",
          id = "categories",
          text = "Categories",
          options = {"Technology", "Science", "Arts", "Sports"},
          values = {"Technology", "Science"}
        },
        {
          type = "toggle_button",
          id = "power_switch",
          text = "Power",
          value = false
        },
    }
}

-- Set the UI and show the window
mainWindow:setUI(ui):show()

setInterval(function() end,1000)