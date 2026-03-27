--%%name:Device Sync Sensor
--%%type:com.fibaro.doorSensor
--%%var:deviceId=0
--%%u:{label="statusLbl",text="Status: --"}
--%%u:{label="sourceLbl",text="Source: --"}

-- Watches another sensor/device and mirrors its 'value' property.
-- Set deviceId variable to the ID of the device to sync with.
-- Reacts instantly to changes via RefreshStateSubscriber (no polling).

local watchedId = 0

function QuickApp:applyValue(val)
    local bVal = (val == true or val == "true" or val == 1 or val == "1")
    self:updateProperty("value", bVal)
    self:updateView("statusLbl", "text", "Status: " .. (bVal and "OPEN/true" or "CLOSED/false"))
    self:updateView("sourceLbl", "text",
        string.format("Source: device %d  —  %s", watchedId, os.date("%H:%M:%S")))
    self:debug(string.format("Synced from device %d: %s", watchedId, tostring(bVal)))
end

function QuickApp:onInit()
    self:debug(self.name, self.id)

    watchedId = tonumber(self:getVariable("deviceId")) or 0
    if watchedId == 0 then
        self:error("deviceId variable is not set — please set it to the ID of the device to watch")
        return
    end

    -- Sync current state immediately
    local val = fibaro.getValue(watchedId, "value")
    if val ~= nil then self:applyValue(val) end

    -- React to live changes via event stream
    self.rss = RefreshStateSubscriber()
    self.rss:subscribe(
        function(event)
            return event.type == "DevicePropertyUpdatedEvent"
               and event.data.id == watchedId
               and event.data.property == "value"
        end,
        function(event)
            self:applyValue(event.data.newValue)
        end
    )
    self.rss:run()

    self:debug(string.format("Watching device %d via RefreshStateSubscriber", watchedId))
end

function QuickApp:onDestroy()
    if self.rss then self.rss:stop() end
end
