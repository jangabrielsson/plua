--%%name:ThermostatHeatCool
--%%type:com.fibaro.thermostatHeatCool
--%%description:"Thermostat heat/cool template"
-- Thermostat heat/cool should handle actions: setThermostatMode, setHeatingThermostatSetpoint, setCoolingThermostatSetpoint
-- Properties that should be updated:
-- * supportedThermostatModes - array of modes supported by the thermostat eg. {"Off", "Heat", "Cool", "Auto"}
-- * thermostatMode - current mode of the thermostat
-- * heatingThermostatSetpoint - set point for heating, supported units: "C" - Celsius, "F" - Fahrenheit
-- * coolingThermostatSetpoint - set point for cooling, supported units: "C" - Celsius, "F" - Fahrenheit
-- * temperature - current temperature, supported units: "C" - Celsius, "F" - Fahrenheit

-- handle action for mode change 
function QuickApp:setThermostatMode(mode)
    self:updateProperty("thermostatMode", mode)
end

-- handle action for setting set point for heating
function QuickApp:setHeatingThermostatSetpoint(value) 
    self:updateProperty("heatingThermostatSetpoint", { value= value, unit= "C" })
end

-- handle action for setting set point for cooling
function QuickApp:setCoolingThermostatSetpoint(value) 
    self:updateProperty("coolingThermostatSetpoint", { value= value, unit= "C" })
end

-- Update current temperature
function QuickApp:updateTemperature(value)
    self:updateProperty("temperature", { value= value, unit= "C" })
end

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end

    -- set supported modes for thermostat
    self:updateProperty("supportedThermostatModes", {"Off", "Heat", "Cool", "Auto"})

    -- setup default values
    self:updateProperty("thermostatMode", "Auto")
    self:setHeatingThermostatSetpoint(21)
    self:setCoolingThermostatSetpoint(23)
    self:updateTemperature(22)
end 