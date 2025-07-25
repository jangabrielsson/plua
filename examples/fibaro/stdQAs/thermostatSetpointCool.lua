--%%name:ThermostatSetpointCool
--%%type:com.fibaro.thermostatSetpointCool
--%%description:"Thermostat setpoint cool template"
-- Thermostat setpoint cool should handle actions: setCoolingThermostatSetpoint
-- Properties that should be updated:
-- * coolingThermostatSetpoint - set point for cooling, supported units: "C" - Celsius, "F" - Fahrenheit
-- * temperature - current temperature, supported units: "C" - Celsius, "F" - Fahrenheit

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

    -- setup default values
    self:setCoolingThermostatSetpoint(23)
    self:updateTemperature(24)
end 