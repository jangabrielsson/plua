--%%name:MotionSensor
--%%type:com.fibaro.motionSensor
--%%description:"My description"
--%%desktop:true

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

-- Motion sensor type has no actions to handle
-- To update motion sensor state, update property "value" with boolean
-- Eg. self:updateProperty("value", true) will indicate that motion was detected 