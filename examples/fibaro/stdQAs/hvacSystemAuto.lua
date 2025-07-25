--%%name:HVACSystemAuto
--%%type:com.fibaro.hvacSystemAuto
--%%description:"My description"
-- Thermostat auto should handle actions: setThermostatMode, setCoolingThermostatSetpoint, setHeatingThermostatSetpoint
-- Properties that should be updated:
-- * supportedThermostatModes - array of modes supported by the thermostat eg. {"Auto", "Off", "Heat", "Cool"}
-- * thermostatMode - current mode of the thermostat
-- * coolingThermostatSetpoint - set point for cooling, supported units: "C" - Celsius, "F" - Fahrenheit
-- * heatingThermostatSetpoint - set point for heating, supported units: "C" - Celsius, "F" - Fahrenheit

-- handle action for mode change 
function QuickApp:setThermostatMode(mode)
    self:updateProperty("thermostatMode", mode)
end

-- handle action for setting set point for cooling
function QuickApp:setCoolingThermostatSetpoint(value) 
    self:updateProperty("coolingThermostatSetpoint", { value= value, unit= "C" })
end

-- handle action for setting set point for heating
function QuickApp:setHeatingThermostatSetpoint(value) 
    self:updateProperty("heatingThermostatSetpoint", { value= value, unit= "C" })
end

-- To update controls you can use method self:updateView(<component ID>, <component property>, <desired value>). Eg:  
-- self:updateView("slider", "value", "55") 
-- self:updateView("button1", "text", "MUTE") 
-- self:updateView("label", "text", "TURNED ON") 

-- This is QuickApp inital method. It is called right after your QuickApp starts (after each save or on gateway startup). 
-- Here you can set some default values, setup http connection or get QuickApp variables.
-- To learn more, please visit: 
--    * https://manuals.fibaro.com/home-center-3/
--    * https://manuals.fibaro.com/home-center-3-quick-apps/

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end

    -- set supported modes for thermostat
    self:updateProperty("supportedThermostatModes", {"Auto", "Off", "Heat", "Cool"})

    -- setup default values
    self:updateProperty("thermostatMode", "Auto")
    self:setCoolingThermostatSetpoint(23)
    self:setHeatingThermostatSetpoint(20)
end

-- HVAC system auto type have no actions to handle 