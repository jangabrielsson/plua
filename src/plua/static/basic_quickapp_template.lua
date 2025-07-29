--%%name:My QuickApp
--%%type:com.fibaro.binarySwitch
--%%description:A starter QuickApp template

--%%Var:counter=0
--%%u:{label='lbl1', text=""}

function QuickApp:onInit()
    self:debug("QuickApp started:", self.name, self.id)
    
    -- Initialize UI callback
    self:updateView("lbl1", "text", "QuickApp initialized at " .. os.date("%c"))
    
    -- Example: Set up a timer for periodic updates
    fibaro.setTimeout(5000, function()
        self:updateView("lbl1", "text", "Timer update at " .. os.date("%c"))
    end)
end

function QuickApp:button(event)
    self:debug("Button pressed!")
    self:updateView("lbl1", "text", "Button pressed at " .. os.date("%c"))

    -- Example: Toggle a property or call an API
    local currentValue = self:getVariable("counter") or "0"
    local newValue = tostring(tonumber(currentValue) + 1)
    self:setVariable("counter", newValue)
    self:updateView("lbl1", "text", "Button count: " .. newValue)
end

-- Add more QuickApp methods here as needed
-- function QuickApp:turnOn()
-- function QuickApp:turnOff()
-- function QuickApp:setValue(value)
