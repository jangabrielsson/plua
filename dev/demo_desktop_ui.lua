-- Desktop UI Demo for plua QuickApp
-- This script demonstrates the desktop UI functionality

print("Starting Desktop UI Demo...")

-- Demo QuickApp definition
local demoQA = {
    id = 123,
    name = "Desktop Demo QuickApp",
    ui = {
        { type = "label", text = "Welcome to Desktop UI!" },
        { type = "button", text = "Test Button", callback = "onButtonClick" },
        { type = "slider", min = 0, max = 100, value = 50, callback = "onSliderChange" }
    },
    
    -- Callback functions
    onButtonClick = function(self)
        print("Button clicked!")
        self:updateView("status", "text", "Button was clicked at " .. os.date("%X"))
    end,
    
    onSliderChange = function(self, data)
        local value = data.value or 50
        print("Slider changed to: " .. value)
        self:updateView("status", "text", "Slider value: " .. value)
    end,
    
    updateView = function(self, elementId, property, value)
        -- This would normally update the UI element
        print(string.format("UI Update: %s.%s = %s", elementId, property, value))
    end
}

-- Store the QuickApp globally for API access
_QA = _QA or {}
_QA[123] = demoQA

-- Function to create a desktop window
function createDesktopWindow(qaId)
    local http = require('net').http
    
    local requestData = {
        qa_id = qaId,
        title = "Demo QuickApp " .. qaId,
        width = 800,
        height = 600
    }
    
    print("Creating desktop window for QuickApp " .. qaId .. "...")
    
    -- Send request to create window
    local response = http.request({
        url = "http://localhost:8888/api/desktop/create_window",
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json"
        },
        data = json.encode(requestData)
    })
    
    if response and response.status == 200 then
        local result = json.decode(response.data)
        if result.success then
            print("Desktop window created: " .. result.window_id)
            return result.window_id
        else
            print("Failed to create window: " .. (result.error or "unknown error"))
        end
    else
        print("HTTP request failed: " .. (response and response.status or "no response"))
    end
    
    return nil
end

-- Function to list desktop windows  
function listDesktopWindows()
    local http = require('net').http
    
    local response = http.request({
        url = "http://localhost:8888/api/desktop/windows",
        method = "GET"
    })
    
    if response and response.status == 200 then
        local result = json.decode(response.data)
        if result.windows then
            print("Open desktop windows:")
            for windowId, info in pairs(result.windows) do
                print("  " .. windowId .. ": " .. info.title)
            end
        else
            print("No desktop windows open")
        end
    else
        print("Failed to list windows")
    end
end

-- Wait a moment for the API server to be ready
_PY.setTimeout(function()
    print("\n=== Desktop UI Demo ===")
    print("Creating desktop window...")
    
    local windowId = createDesktopWindow(123)
    
    if windowId then
        print("Window created successfully!")
        print("\nTry interacting with the QuickApp UI in the desktop window.")
        print("The callbacks will be printed here in the terminal.")
        
        -- List windows after a short delay
        _PY.setTimeout(function()
            print("\n")
            listDesktopWindows()
        end, 2000)
        
        -- Send a test update after 5 seconds
        _PY.setTimeout(function()
            print("\nSending test update to window...")
            local http = require('net').http
            
            local updateData = {
                window_id = windowId,
                event_type = "ui_update",
                data = {
                    element_id = "status-label",
                    value = "Updated from Lua at " .. os.date("%X")
                }
            }
            
            local response = http.request({
                url = "http://localhost:8888/api/desktop/send",
                method = "POST",
                headers = {
                    ["Content-Type"] = "application/json"
                },
                data = json.encode(updateData)
            })
            
            if response and response.status == 200 then
                print("Update sent successfully!")
            else
                print("Failed to send update")
            end
        end, 5000)
    else
        print("Failed to create window. Make sure:")
        print("1. You started plua with --desktop flag")
        print("2. pywebview is installed (pip install pywebview)")
        print("3. The API server is running")
    end
end, 1000)

print("Demo script loaded. Desktop window will be created in 1 second...")
print("Press Ctrl+C to exit.")
