--%%name:MultilevelSwitch
--%%type:com.fibaro.multilevelSwitch
--%%description:"Multilevel switch template"
--%%desktop:true

-- Multilevel switch type should handle actions: turnOn, turnOff, setValue
-- To update multilevel switch state, update property "value" with integer 0-99

function QuickApp:turnOn()
    self:debug("multilevel switch turned on")
    self:updateProperty("value", 99)
end

function QuickApp:turnOff()
    self:debug("multilevel switch turned off")
    self:updateProperty("value", 0)    
end

-- Value is type of integer (0-99)
function QuickApp:setValue(value)
    self:debug("multilevel switch set to: " .. tostring(value))
    self:updateProperty("value", value)    
end

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end 