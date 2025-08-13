--%%name:CrossSessionTest
--%%type:com.fibaro.device  
--%%desktop:true
--%%debug:true
--%%u:{label="lbl1",text="Cross-Session Reuse Test"}
--%%u:{button="btn1",text="Check Window Count",onReleased="checkWindows"}

function QuickApp:onInit()
    self:debug("CrossSessionTest initialized with ID: " .. self.id)
    self:updateView("lbl1", "text", "QA " .. self.id .. " - Window should reuse on restart")
    
    -- Test if this window was reused or newly created
    local windowInfo = "Window info: This should show if reused or new"
    self:debug(windowInfo)
end

function QuickApp:checkWindows()
    self:debug("Checking all browser windows...")
    
    -- This would call a Python function to list windows, but let's simulate
    self:updateView("lbl1", "text", "Check logs for window info")
    
    -- Log some info to help debug
    self:debug("Current QA ID: " .. self.id)
    self:debug("If you restart EPLua and run this QA again,")
    self:debug("the same Safari window should be reused")
end
