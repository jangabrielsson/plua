--%%name:ThermostatSetpointHeatCool
--%%type:com.fibaro.thermostatSetpointHeatCool
--%%description:Heat+cool setpoint-only thermostat template
-- Also use for: com.fibaro.thermostatSetpoint

-- Actions: setHeatingThermostatSetpoint, setCoolingThermostatSetpoint
-- Properties: heatingThermostatSetpoint, coolingThermostatSetpoint, temperature

function QuickApp:setHeatingThermostatSetpoint(value)
    self:updateProperty("heatingThermostatSetpoint", {value=value, unit="C"})
end

function QuickApp:setCoolingThermostatSetpoint(value)
    self:updateProperty("coolingThermostatSetpoint", {value=value, unit="C"})
end

function QuickApp:updateTemperature(value)
    self:updateProperty("temperature", {value=value, unit="C"})
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:setHeatingThermostatSetpoint(21)
    self:setCoolingThermostatSetpoint(23)
    self:updateTemperature(22)
end
