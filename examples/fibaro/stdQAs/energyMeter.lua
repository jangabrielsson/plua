--%%name:EnergyMeter
--%%type:com.fibaro.energyMeter
--%%description:"My description"
--%%desktop:true

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

-- Energy meter type have no actions to handle
-- To update energy consumption, update property "value" with appropriate floating point number
-- Reported value must be in kWh
-- Eg. 
-- self:updateProperty("value", 226.137) 

function QuickApp:updateEnergy(value)
    self:debug("energy meter update: " .. tostring(value))
    self:updateProperty("value", value)
end