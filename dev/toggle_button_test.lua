-- Test toggle button functionality
local windows = require('windows')

-- Create window
local window = windows.createNativeWindow("Toggle Button Test", 400, 300)

-- Define UI with toggle buttons using hierarchical format
local ui = {
    type = "frame",
    padding = 20,
    children = {
        {
            type = "label",
            id = "title",
            text = "Toggle Button Test"
        },
        {
            type = "toggle_button",
            id = "power_switch",
            text = "Power",
            value = false
        },
        {
            type = "toggle_button",
            id = "auto_mode",
            text = "Auto Mode",
            value = true
        },
        {
            type = "label",
            id = "status",
            text = "Status: Ready"
        }
    }
}

-- Set the UI
window:setUI(ui)

-- Set callbacks
window:setCallback("power_switch", function(data)
    local is_on = data.data.value
    print("Power switch:", is_on and "ON" or "OFF")
end)

window:setCallback("auto_mode", function(data)
    local is_on = data.data.value
    print("Auto mode:", is_on and "ON" or "OFF")
end)

-- Show the window
window:show()

-- Keep the script running
setInterval(1000, function()
    -- Keep alive
end) 