--%%name:TemperatureSensor
--%%type:com.fibaro.temperatureSensor
--%%description:"My description"
function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

-- Temperature sensor type have no actions to handle
-- To update temperature, update property "value" with floating point number, supported units: "C" - Celsius, "F" - Fahrenheit
-- Eg. self:updateProperty("value", { value= 18.12, unit= "C" }) 