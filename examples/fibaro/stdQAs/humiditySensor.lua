--%%name:HumiditySensor
--%%type:com.fibaro.humiditySensor
--%%description:"My description"
function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

-- Humidity sensor type have no actions to handle
-- To update humidity, update property "value" with floating point number
-- Eg. self:updateProperty("value", 90.28) 