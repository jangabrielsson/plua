--%%name:My Temperature Sensor
--%%type:com.fibaro.temperatureSensor
--%%var:pollInterval=60
--%%u:{label="valueLbl",text="Value: --"}

-- Change type to any of: com.fibaro.humiditySensor, com.fibaro.lightSensor,
-- com.fibaro.multilevelSensor, com.fibaro.energyMeter, com.fibaro.powerMeter

function QuickApp:onInit()
    self:debug(self.name, self.id)
    local interval = tonumber(self:getVariable("pollInterval")) * 1000
    setTimeout(function() self:poll() end, 100)  -- immediate first poll
    setInterval(function() self:poll() end, interval)
end

function QuickApp:poll()
    -- replace with real sensor read / HTTP call
    local value = 21.5
    local unit = "C"   -- change as appropriate

    -- For temperature/humidity/climate: use {value=, unit=}
    self:updateProperty("value", {value=value, unit=unit})

    -- For simple numeric sensors (light, power, energy): just use the number
    -- self:updateProperty("value", value)

    self:updateView("valueLbl", "text", string.format("Value: %.1f %s", value, unit))
    self:debug("Value:", value, unit)
end
