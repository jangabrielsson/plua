--%%name:ThermostatHeatCool
--%%type:com.fibaro.thermostatHeatCool
--%%description:Heat+cool thermostat template
-- Also use for: com.fibaro.hvacSystemHeatCool, com.fibaro.hvacSystemAuto

-- Actions: setThermostatMode, setHeatingThermostatSetpoint, setCoolingThermostatSetpoint
-- Properties: supportedThermostatModes, thermostatMode, heatingThermostatSetpoint,
--             coolingThermostatSetpoint, temperature

function QuickApp:setThermostatMode(mode)
    self:updateProperty("thermostatMode", mode)
end

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
    self:updateProperty("supportedThermostatModes", {"Off", "Heat", "Cool", "Auto"})
    self:updateProperty("thermostatMode", "Auto")
    self:setHeatingThermostatSetpoint(21)
    self:setCoolingThermostatSetpoint(23)
    self:updateTemperature(22)
end
