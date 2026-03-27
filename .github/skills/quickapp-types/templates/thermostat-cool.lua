--%%name:ThermostatCool
--%%type:com.fibaro.thermostatCool
--%%description:Cool-only thermostat template
-- Also use for: com.fibaro.hvacSystemCool

-- Actions: setThermostatMode, setCoolingThermostatSetpoint
-- Properties: supportedThermostatModes, thermostatMode, coolingThermostatSetpoint, temperature

function QuickApp:setThermostatMode(mode)
    self:updateProperty("thermostatMode", mode)
end

function QuickApp:setCoolingThermostatSetpoint(value)
    self:updateProperty("coolingThermostatSetpoint", {value=value, unit="C"})
end

function QuickApp:updateTemperature(value)
    self:updateProperty("temperature", {value=value, unit="C"})
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:updateProperty("supportedThermostatModes", {"Off", "Cool"})
    self:updateProperty("thermostatMode", "Cool")
    self:setCoolingThermostatSetpoint(23)
    self:updateTemperature(24)
end
