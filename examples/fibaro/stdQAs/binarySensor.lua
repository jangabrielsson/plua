--%%name:BinarySensor
--%%type:com.fibaro.binarySensor
--%%description:"My description"
function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

-- Binary sensor type have no actions to handle
-- To update binary sensor state, update property "value" with boolean
-- Eg. self:updateProperty("value", true) will set sensor to breached state 

function QuickApp:breached(state)
    self:debug("binary sensor breached: " .. tostring(state))
    self:updateProperty("value", state)
end