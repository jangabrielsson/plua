--%%name:Temperature (wttr.in)
--%%type:com.fibaro.multilevelSensor
--%%proxy:true
--%%var:location="Stockholm"
--%%var:pollInterval=300
--%%u:{label="tempLbl",text="Temp: --"}
--%%u:{label="condLbl",text=""}
--%%u:{label="lastLbl",text="Last update: --"}

-- Fetches current temperature from wttr.in (no API key required)
-- Change location via the 'location' QuickApp variable

local http = net.HTTPClient()

function QuickApp:poll()
    local location = self:getVariable("location")
    if location == nil or location == "" then location = "Stockholm" end
    local url = "https://wttr.in/" .. location .. "?format=j1"
    http:request(url, {
        options = { method = "GET", timeout = 10000 },
        success = function(resp)
            if resp.status ~= 200 then
                self:error("HTTP error:", resp.status)
                return
            end
            local ok, data = pcall(json.decode, resp.data)
            if not ok or not data then
                self:error("JSON decode failed")
                return
            end
            local cc = data.current_condition and data.current_condition[1]
            if not cc then
                self:error("Unexpected response structure")
                return
            end
            local temp  = tonumber(cc.temp_C) or 0
            local feels = tonumber(cc.FeelsLikeC) or 0
            local desc  = cc.weatherDesc and cc.weatherDesc[1] and cc.weatherDesc[1].value or ""
            self:updateProperty("value", temp)
            self:updateView("tempLbl", "text",
                string.format("Temp: %.1f°C  (feels like %.1f°C)", temp, feels))
            self:updateView("condLbl", "text", desc)
            self:updateView("lastLbl", "text",
                "Last update: " .. os.date("%H:%M:%S"))
            self:debug(string.format("%s: %.1f°C (%s)", location, temp, desc))
        end,
        error = function(err)
            self:error("Request failed:", err)
        end
    })
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    local interval = tonumber(self:getVariable("pollInterval")) * 1000
    setTimeout(function() self:poll() end, 500)
    setInterval(function() self:poll() end, interval)
end
