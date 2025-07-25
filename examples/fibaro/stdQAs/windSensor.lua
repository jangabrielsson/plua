--%%name:WindSensor
--%%type:com.fibaro.windSensor
--%%description:"My description"
-- Wind sensor type have no actions to handle
-- To update wind value, update property "value" with floating point number
-- Eg. self:updateProperty("value", 81.42) 

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

function QuickApp:updateWind(value)
    self:debug("wind sensor update: " .. tostring(value))
    self:updateProperty("value", value)
end