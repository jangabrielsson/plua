--%%name:ThermostatSetpointCool
--%%type:com.fibaro.thermostatSetpointCool
--%%description:Cool setpoint-only thermostat template

-- Actions: setCoolingThermostatSetpoint
-- Properties: coolingThermostatSetpoint, temperature

function QuickApp:setCoolingThermostatSetpoint(value)
    self:updateProperty("coolingThermostatSetpoint", {value=value, unit="C"})
end

function QuickApp:updateTemperature(value)
    self:updateProperty("temperature", {value=value, unit="C"})
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:setCoolingThermostatSetpoint(23)
    self:updateTemperature(24)
end
