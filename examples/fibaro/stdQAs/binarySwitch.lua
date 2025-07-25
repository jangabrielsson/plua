--%%name:BinarySwitch
--%%type:com.fibaro.binarySwitch
--%%description:"My description"
-- Binary switch type should handle actions turnOn, turnOff
-- To update binary switch state, update property "value" with boolean

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

function QuickApp:turnOn()
    self:debug("binary switch turned on")
    self:updateProperty("value", true)
end

function QuickApp:turnOff()
    self:debug("binary switch turned off")
    self:updateProperty("value", false)    
end 