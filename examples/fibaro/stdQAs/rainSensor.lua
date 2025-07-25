--%%name:RainSensor
--%%type:com.fibaro.rainSensor
--%%description:"My description"
function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

function QuickApp:updateRainValue(value)
    self:setVariable("value",value)
end
