--%%name:My Sensor
--%%type:com.fibaro.binarySensor   -- change to any binary sensor type:
-- com.fibaro.doorSensor, com.fibaro.windowSensor, com.fibaro.motionSensor,
-- com.fibaro.smokeSensor, com.fibaro.fireDetector, com.fibaro.heatDetector,
-- com.fibaro.floodSensor, com.fibaro.waterLeakSensor, com.fibaro.coDetector,
-- com.fibaro.gasDetector, com.fibaro.rainDetector
--%%var:pollInterval=60
--%%u:{label="statusLbl",text="State: Closed"}

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:updateProperty("value", false)
    local interval = tonumber(self:getVariable("pollInterval")) * 1000
    setInterval(function() self:poll() end, interval)
end

function QuickApp:poll()
    -- replace with real sensor read / HTTP call
    local triggered = false
    self:setState(triggered)
end

function QuickApp:setState(triggered)
    self:updateProperty("value", triggered)
    self:updateView("statusLbl", "text", triggered and "State: Open" or "State: Closed")
    self:debug("State:", triggered)
end
