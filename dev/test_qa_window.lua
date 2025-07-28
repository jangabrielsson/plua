-- Test script that opens a QuickApp window manually
print("=== QuickApp Window Test ===")

-- Define a simple QuickApp that opens a window
function QuickApp:onInit()
    self:debug("QuickApp started")
    
    -- Open a window to test cleanup
    local window = {
        type = "myQuickApp",
        title = "Test QuickApp Window",
        id = 999
    }
    
    -- This should open a desktop UI window
    self:trace("Opening QuickApp window for testing...")
    
    -- Schedule some work to keep the app running
    fibaro.setTimeout(30000, function()
        self:debug("Timer fired - app still running")
    end)
end

function QuickApp:button(event)
    self:debug("Button pressed!")
end

-- Initialize QuickApp
local qa = QuickApp:new()
qa.id = 999
qa.name = "Test QuickApp"
qa:onInit()

print("QuickApp initialized - window should be opening...")
print("Press Ctrl+C to test cleanup...")
