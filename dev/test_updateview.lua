-- Test script to trigger updateView explicitly
print("Testing updateView functionality...")

-- Create a simple QuickApp with UI elements
function QuickApp:onInit()
    self:debug("Test QA initialized with ID:", self.id)
    
    -- Set initial state
    self:updateView("label1", "text", "Initial text")
    
    -- Schedule an update in 3 seconds
    setTimeout(function()
        self:debug("Updating label1 text...")
        self:updateView("label1", "text", "Updated at " .. os.date("%H:%M:%S"))
        self:debug("Update sent via updateView")
    end, 3000)
    
    -- Schedule another update in 6 seconds
    setTimeout(function()
        self:debug("Second update...")
        self:updateView("label1", "text", "Second update at " .. os.date("%H:%M:%S"))
    end, 6000)
end

function QuickApp:turnOn()
    self:debug("Turn On pressed - updating UI")
    self:updateView("label1", "text", "Turn On pressed at " .. os.date("%H:%M:%S"))
    self:updateProperty("value", true)
end

function QuickApp:turnOff()
    self:debug("Turn Off pressed - updating UI")
    self:updateView("label1", "text", "Turn Off pressed at " .. os.date("%H:%M:%S"))
    self:updateProperty("value", false)
end
