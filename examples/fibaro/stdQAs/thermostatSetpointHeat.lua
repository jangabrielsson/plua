--%%name:ThermostatSetpointHeat
--%%type:com.fibaro.thermostatSetpointHeat
--%%description:"Thermostat setpoint heat template"
-- Thermostat setpoint heat should handle actions: setHeatingThermostatSetpoint
-- Properties that should be updated:
-- * heatingThermostatSetpoint - set point for heating, supported units: "C" - Celsius, "F" - Fahrenheit
-- * temperature - current temperature, supported units: "C" - Celsius, "F" - Fahrenheit

-- handle action for setting set point for heating
function QuickApp:setHeatingThermostatSetpoint(value) 
    self:updateProperty("heatingThermostatSetpoint", { value= value, unit= "C" })
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
    self:setHeatingThermostatSetpoint(21)
    self:updateTemperature(20)
end 