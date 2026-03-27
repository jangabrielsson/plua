--%%name:ThermostatSetpointHeat
--%%type:com.fibaro.thermostatSetpointHeat
--%%description:Heat setpoint-only thermostat template

-- Actions: setHeatingThermostatSetpoint
-- Properties: heatingThermostatSetpoint, temperature

function QuickApp:setHeatingThermostatSetpoint(value)
    self:updateProperty("heatingThermostatSetpoint", {value=value, unit="C"})
end

function QuickApp:updateTemperature(value)
    self:updateProperty("temperature", {value=value, unit="C"})
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:setHeatingThermostatSetpoint(21)
    self:updateTemperature(20)
end
