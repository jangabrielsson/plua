--%%name:HeatDetector
--%%type:com.fibaro.heatDetector
--%%description:"My description"
-- Heat detector type has no actions to handle
-- To update heat detector state, update property "value" with boolean
-- Eg. self:updateProperty("value", true) will indicate that heat was detected 

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

function QuickApp:breached(state)
    self:debug("heat detector breached: " .. tostring(state))
    self:updateProperty("value", state)
end