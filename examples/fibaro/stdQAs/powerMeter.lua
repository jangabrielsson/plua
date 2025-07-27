--%%name:PowerMeter
--%%type:com.fibaro.powerMeter
--%%description:"My description"
--%%desktop:true

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

-- Power meter type have no actions to handle
-- To update energy consumption, update property "value" with appropriate floating point number
-- Reported value must be in W
-- Eg. 
-- self:updateProperty("value", 226.137)
-- Power meter contains property rateType, which has two possible values:
-- - production - responsible for production power measurement
-- - consumption - responsible for consumption power measurement
-- Eg.
-- self:updateProperty("rateType", "production")
-- self:updateProperty("rateType", "consumption") 

function QuickApp:updateValue(value)
    self:debug("power meter update value: " .. tostring(value))
    self:updateProperty("value", value)
end

function QuickApp:updateRateType(rateType)
    self:debug("power meter update rate type: " .. tostring(rateType))
    self:updateProperty("rateType", rateType)
end