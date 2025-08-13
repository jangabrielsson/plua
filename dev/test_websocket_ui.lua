-- Test WebSocket UI updates in browser
-- This script tests real-time UI updates using QuickApp updateView()

function QuickApp:onInit()
    self.id = 5555
    self.name = "TEST_WEBSOCKET_UI"
    
    -- Create initial UI
    self:updateView("label1", "text", "Initial value")
    self:updateView("button1", "text", "Click me")
    
    -- Schedule UI updates every 2 seconds
    self.updateCounter = 0
    
    self:run(function()
        while true do
            fibaro.sleep(2000)
            self.updateCounter = self.updateCounter + 1
            
            -- Update the label with current time and counter
            local timeStr = os.date("%H:%M:%S")
            self:updateView("label1", "text", string.format("Updated at %s (count: %d)", timeStr, self.updateCounter))
            
            -- Change button text
            self:updateView("button1", "text", self.updateCounter % 2 == 0 and "Even Update" or "Odd Update")
            
            -- Exit after 5 updates for demo
            if self.updateCounter >= 5 then
                self:debug("Test completed - performed 5 UI updates")
                break
            end
        end
    end)
end

return QuickApp:new()
