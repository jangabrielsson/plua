--%%name:UIRefreshTest
--%%type:com.fibaro.binarySwitch
--%%save:dev/ui_refresh_test.fqa
--%%desktop:true
--%%u:{label="status",text="Initial status"}
--%%u:{button="update",text="Update Status",onReleased="updateStatus"}
--%%u:{label="counter",text="Counter: 0"}

function QuickApp:onInit()
    self.counter = 0
    self:debug("UI Refresh Test QA initialized")
    
    -- Update the status every 3 seconds to test background updates
    setInterval(function()
        self.counter = self.counter + 1
        local timestamp = os.date("%H:%M:%S")
        
        self:updateView("status", "text", "Updated at " .. timestamp)
        self:updateView("counter", "text", "Counter: " .. self.counter)
        
        self:debug("Background update " .. self.counter .. " at " .. timestamp)
    end, 3000)
end

function QuickApp:updateStatus()
    local timestamp = os.date("%H:%M:%S")
    self:updateView("status", "text", "Button clicked at " .. timestamp)
    self:debug("Button clicked at " .. timestamp)
end
