--%%name:TemperatureSensor
--%%type:com.fibaro.temperatureSensor
--%%description:"My description"
--%%desktop:true

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
function QuickApp:setValue(val)
    assert(type(val)=='table',"Value should be a table with keys 'value' and 'unit'")
    local value = val.value
    local unit = val.unit
    assert(type(value)=='number',"Value should be a number")
    assert(unit=="C" or unit=="F","Unit should be either 'C' or 'F'")
    self:updateProperty("value", { value= value, unit= unit })    
end