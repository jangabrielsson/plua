--%%name:WindowReuseDebug
--%%type:com.fibaro.device  
--%%desktop:true
--%%debug:true
--%%u:{label="lbl1",text="Window Reuse Debug Test"}
--%%u:{button="btn1",text="Update Text",onReleased="updateText"}

function QuickApp:onInit()
    self:debug("WindowReuseDebug initialized with ID: " .. self.id)
    self:debug("Desktop window should open automatically")
    
    -- Update the label to show we're alive
    self:updateView("lbl1", "text", "QA " .. self.id .. " initialized at " .. os.date("%H:%M:%S"))
end

function QuickApp:updateText()
    local timestamp = os.date("%H:%M:%S")
    self:debug("Button clicked at " .. timestamp)
    self:updateView("lbl1", "text", "Button clicked at " .. timestamp)
end
