--%%name:Binary Switch Status
--%%type:com.fibaro.deviceController
--%%u:{button="refreshBtn",text="Refresh",onReleased="onRefresh"}
--%%u:{label="tableLbl",text="Loading..."}

-- Lists all HC3 binarySwitch devices in an HTML table (ID, Name, Status).
-- Updates instantly when any switch changes state via RefreshStateSubscriber.

local switches = {}  -- [id] = { name, value }

local function buildHtmlTable()
    local rows = {
        "<table><tr><td><b>ID</b></td><td><b>Name</b></td><td><b>Status</b></td></tr>",
    }
    -- Collect and sort by ID for stable ordering
    local ids = {}
    for id in pairs(switches) do ids[#ids+1] = id end
    table.sort(ids)
    for _, id in ipairs(ids) do
        local dev = switches[id]
        local status = dev.value and "ON" or "OFF"
        local color  = dev.value and "green" or "gray"
        rows[#rows+1] = string.format(
            "<tr><td>%d</td><td>%s</td><td><font color='%s'>%s</font></td></tr>",
            id, dev.name, color, status)
    end
    rows[#rows+1] = "</table>"
    -- NOTE: no newlines between tags — each \n produces an extra blank line in HC3 label rendering
    return table.concat(rows, "")
end

function QuickApp:loadSwitches()
    local devices = api.get("/devices?type=com.fibaro.binarySwitch") or {}
    switches = {}
    for _, dev in ipairs(devices) do
        switches[dev.id] = { name = dev.name, value = dev.properties.value }
    end
    self:debug(string.format("Loaded %d binary switches", #devices))
    local tab = buildHtmlTable()
    print(tab)
    self:updateView("tableLbl", "text", tab)
end

function QuickApp:onRefresh()
    self:loadSwitches()
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:loadSwitches()

    self.rss = RefreshStateSubscriber()
    self.rss:subscribe(
        function(event)
            return event.type == "DevicePropertyUpdatedEvent"
                and event.data.property == "value"
                and switches[event.data.id] ~= nil
        end,
        function(event)
            switches[event.data.id].value = event.data.newValue
            self:updateView("tableLbl", "text", buildHtmlTable())
        end
    )
    self.rss:run()
end

function QuickApp:onDestroy()
    if self.rss then self.rss:stop() end
end
