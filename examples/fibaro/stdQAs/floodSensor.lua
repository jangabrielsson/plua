--%%name:FloodSensor
--%%type:com.fibaro.floodSensor
--%%description:"Flood sensor template"
-- Flood sensor type have no actions to handle
-- To update flood sensor state, update property "value" with boolean
-- Eg. self:updateProperty("value", true) will indicate that flood was detected 

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end 

function QuickApp:breached(state)
    self:debug("flood sensor breached: " .. tostring(state))
    self:updateProperty("value", state)
end