--%%name:My Controller
--%%type:com.fibaro.deviceController
--%%var:interval=30
--%%u:{label="statusLbl",text="Status: Idle"}
--%%u:{button="refreshBtn",text="Refresh Now",onReleased="refreshNow"}

function QuickApp:onInit()
    self:debug(self.name, self.id)
    local interval = tonumber(self:getVariable("interval")) * 1000
    self:updateView("statusLbl", "text", "Status: Running")
    setInterval(function() self:refresh() end, interval)
end

function QuickApp:refresh()
    self:debug("Polling...")
    -- add polling logic here
end

function QuickApp:refreshNow(event)
    self:refresh()
end
