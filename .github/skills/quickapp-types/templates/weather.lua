--%%name:Weather
--%%type:com.fibaro.weather
--%%description:Weather station template
--%%var:pollInterval=300

-- No actions to handle.
-- Property names are CAPITALISED: Temperature, Humidity, Wind, ConditionCode, WeatherCondition
-- Temperature/Wind use {value=n, unit="C"} format; Humidity is a plain number.
-- Conditions: "unknown","clear","rain","snow","storm","cloudy","partlyCloudy","fog"

local conditionCodes = {
    unknown=3200, clear=32, rain=40, snow=38,
    storm=4, cloudy=30, partlyCloudy=30, fog=20,
}

function QuickApp:setCondition(condition)
    local code = conditionCodes[condition]
    if code then
        self:updateProperty("WeatherCondition", condition)
        self:updateProperty("ConditionCode", code)
    end
end

function QuickApp:poll()
    -- replace with real data source / HTTP call
    self:updateProperty("Temperature", {value=18.5, unit="C"})
    self:updateProperty("Humidity", 62)
    self:updateProperty("Wind", 5.2)
    self:setCondition("partlyCloudy")
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    local interval = tonumber(self:getVariable("pollInterval")) * 1000
    setTimeout(function() self:poll() end, 100)
    setInterval(function() self:poll() end, interval)
end
