--%%name:WindowSensor
--%%type:com.fibaro.windowSensor
--%%description:"My description"
-- Window sensor type have no actions to handle
-- To update window sensor state, update property "value" with boolean
-- Eg. self:updateProperty("value", true) will set sensor to breached state 

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

function QuickApp:breached(state)
    self:debug("window sensor breached: " .. tostring(state))
    self:updateProperty("value", state)
end