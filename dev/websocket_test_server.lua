-- Test script that runs continuously to keep the server alive
-- for testing WebSocket connections

function QuickApp:onInit()
    self.id = 5555
    self.name = "WEBSOCKET_TEST_SERVER"
    
    self:debug("🌐 WebSocket test server started")
    self:debug("📡 Server will broadcast updates every 5 seconds")
    self:debug("🔗 Connect WebSocket to: ws://localhost:8080/ws")
    
    self.counter = 0
    
    -- Run continuously and broadcast updates
    self:run(function()
        while true do
            fibaro.sleep(5000) -- Wait 5 seconds
            
            self.counter = self.counter + 1
            local message = string.format("Update #%d at %s", self.counter, os.date("%H:%M:%S"))
            
            self:debug(string.format("📡 Broadcasting: %s", message))
            
            -- Test broadcast
            self:updateView("status_label", "text", message)
            self:updateView("counter_value", "text", tostring(self.counter))
            
            -- Continue for 30 broadcasts (2.5 minutes)
            if self.counter >= 30 then
                self:debug("🔚 Test completed - 30 broadcasts sent")
                break
            end
        end
    end)
end

return QuickApp
