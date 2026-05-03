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

function QuickApp:setValue(val)
    assert(type(val)=='number',"Value should be a number")
    self:updateProperty("value", val)    
end