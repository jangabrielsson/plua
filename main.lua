--%%name:My QuickApp
--%%type:com.fibaro.quickApp
--%%description:A starter QuickApp template

function QuickApp:onInit()
    self:debug("QuickApp started:", self.name, self.id)
    
    -- Initialize UI callback
    self:updateProperty("log", "QuickApp initialized at " .. os.date("%c"))
    
    -- Example: Set up a timer for periodic updates
    fibaro.setTimeout(5000, function()
        self:updateProperty("log", "Timer update at " .. os.date("%c"))
    end)
end

function QuickApp:button(event)
    self:debug("Button pressed!")
    self:updateProperty("log", "Button pressed at " .. os.date("%c"))
    
    -- Example: Toggle a property or call an API
    local currentValue = self:getVariable("counter") or "0"
    local newValue = tostring(tonumber(currentValue) + 1)
    self:setVariable("counter", newValue)
    self:updateProperty("log", "Button count: " .. newValue)
end

-- Add more QuickApp methods here as needed
-- function QuickApp:turnOn()
-- function QuickApp:turnOff()
-- function QuickApp:setValue(value)
