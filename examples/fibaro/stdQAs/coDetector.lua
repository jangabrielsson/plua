--%%name:CODetector
--%%type:com.fibaro.coDetector
--%%description:"My description"
function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

-- Carbon monoxide detector type has no actions to handle
-- To update carbon monoxide detector state, update property "value" with boolean
-- Eg. self:updateProperty("value", true) will indicate that carbon monoxide was detected 

function QuickApp:breached(state)
    self:debug("carbon monoxide detector breached: " .. tostring(state))
    self:updateProperty("value", state)
end