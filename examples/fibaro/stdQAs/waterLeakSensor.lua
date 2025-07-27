--%%name:WaterLeakSensor
--%%type:com.fibaro.waterLeakSensor
--%%description:"My description"
--%%desktop:true

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end 