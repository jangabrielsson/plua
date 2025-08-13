-- Test WebSocket reconnection after window reuse
-- Run this, open a QuickApp window, stop EPLua, restart, and verify UI updates work

--%%desktop:true

class "TestReconnectQA"(QuickApp)

function TestReconnectQA:onInit()
    self:debug("TestReconnectQA:onInit")
    
    -- Set up a timer to periodically update the UI
    self.counter = 0
    
    -- Start immediate UI updates
    self:updateCounter()
    
    -- Set up interval to update every 3 seconds
    setInterval(function()
        self:updateCounter()
    end, 3000)
end

function TestReconnectQA:updateCounter()
    self.counter = self.counter + 1
    local timestamp = os.date("%H:%M:%S")
    
    -- Update both label and button text
    self:updateView("lbl1", "text", string.format("Counter: %d (Updated: %s)", self.counter, timestamp))
    self:updateView("btn1", "text", string.format("Count: %d", self.counter))
    
    self:debug(string.format("Updated counter to %d at %s", self.counter, timestamp))
end

function TestReconnectQA:testBtn()
    self:debug("Button clicked! Forcing update...")
    self:updateCounter()
end

--%%u:{label="lbl1",text="Starting..."}
--%%u:{button="btn1",text="Test Button",onReleased="testBtn"}
