--%%name:Weather
--%%type:com.fibaro.weather
--%%description:"My description"
-- Weather type have no actions to handle
-- To update temperature, update property "Temperature" with floating point number, supported units: "C" - Celsius, "F" - Fahrenheit
-- To update humidity, update property "Humidity" with floating point number
-- To update wind speed, update property "Wind" with floating point number
-- Eg. self:updateProperty("Temperature", { value= 18.12, unit= "C" })
-- To update weather condition, update properties "ConditionCode" and "WeatherCondition" or use method QuickApp:setCondition
-- Eg. self:setCondition("clear")

-- Posible conditions: "unknown", "clear", "rain", "snow", "storm", "cloudy", "partlyCloudy", "fog"
function QuickApp:setCondition(condition)
    local conditionCodes = { 
        unknown = 3200,
        clear = 32,
        rain = 40,
        snow = 38,
        storm = 4,
        cloudy = 30,
        partlyCloudy = 30,
        fog = 20,
    }

    local conditionCode = conditionCodes[condition]

    if conditionCode then
        self:updateProperty("ConditionCode", conditionCode)
        self:updateProperty("WeatherCondition", condition)
    end
end

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end 