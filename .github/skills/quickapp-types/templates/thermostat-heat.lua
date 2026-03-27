--%%name:ThermostatHeat
--%%type:com.fibaro.thermostatHeat
--%%description:Heat-only thermostat template
-- Also use for: com.fibaro.hvacSystemHeat

-- Actions: setThermostatMode, setHeatingThermostatSetpoint
-- Properties: supportedThermostatModes, thermostatMode, heatingThermostatSetpoint, temperature

function QuickApp:setThermostatMode(mode)
    self:updateProperty("thermostatMode", mode)
end

function QuickApp:setHeatingThermostatSetpoint(value)
    self:updateProperty("heatingThermostatSetpoint", {value=value, unit="C"})
end

function QuickApp:updateTemperature(value)
    self:updateProperty("temperature", {value=value, unit="C"})
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:updateProperty("supportedThermostatModes", {"Off", "Heat"})
    self:updateProperty("thermostatMode", "Heat")
    self:setHeatingThermostatSetpoint(21)
    self:updateTemperature(20)
end
