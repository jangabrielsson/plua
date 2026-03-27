--%%name:My Thermostat
--%%type:com.fibaro.thermostat
--%%var:pollInterval=60
--%%u:{label="tempLbl",text="Temp: --°C"}
--%%u:{slider="setpointSlider",text="Setpoint",min="5",max="30",value="21",onChanged="setSetpoint"}
--%%u:{select="modeSelect",text="Mode",value="Heat",onToggled="setMode",
--      options={{type='option',text='Off',value='Off'},{type='option',text='Heat',value='Heat'},{type='option',text='Cool',value='Cool'},{type='option',text='Auto',value='Auto'}}}

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:updateProperty("supportedThermostatModes", {"Off","Heat","Cool","Auto"})
    self:updateProperty("thermostatMode", "Heat")
    self:updateProperty("heatingThermostatSetpoint", {value=21, unit="C"})
    self:updateProperty("temperature", {value=20.5, unit="C"})
    local interval = tonumber(self:getVariable("pollInterval")) * 1000
    setInterval(function() self:poll() end, interval)
end

function QuickApp:poll()
    -- replace with real sensor read / HTTP call
    local temp = 20.5
    self:updateProperty("temperature", {value=temp, unit="C"})
    self:updateView("tempLbl", "text", string.format("Temp: %.1f°C", temp))
end

function QuickApp:setSetpoint(event)
    local v = tonumber(event.values[1])
    -- add API call to set setpoint
    self:updateProperty("heatingThermostatSetpoint", {value=v, unit="C"})
    self:debug("Setpoint:", v)
end

function QuickApp:setMode(event)
    local mode = event.values[1]
    -- add API call to set mode
    self:updateProperty("thermostatMode", mode)
    self:debug("Mode:", mode)
end
