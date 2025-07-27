--%%name:ThermostatCool
--%%type:com.fibaro.thermostatCool
--%%description:"Thermostat cool template"
--%%desktop:true

-- Thermostat cool should handle actions: setThermostatMode, setCoolingThermostatSetpoint
-- Properties that should be updated:
-- * supportedThermostatModes - array of modes supported by the thermostat eg. {"Off", "Cool"}
-- * thermostatMode - current mode of the thermostat
-- * coolingThermostatSetpoint - set point for cooling, supported units: "C" - Celsius, "F" - Fahrenheit
-- * temperature - current temperature, supported units: "C" - Celsius, "F" - Fahrenheit

-- handle action for mode change 
function QuickApp:setThermostatMode(mode)
    self:updateProperty("thermostatMode", mode)
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
    self:updateProperty("supportedThermostatModes", {"Off", "Cool"})

    -- setup default values
    self:updateProperty("thermostatMode", "Cool")
    self:setCoolingThermostatSetpoint(23)
    self:updateTemperature(24)
end 