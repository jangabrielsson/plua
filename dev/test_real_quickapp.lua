--%%name:TestNewWindows
--%%type:com.fibaro.device  
--%%desktop:true
--%%debug:true
--%%u:{label="lbl1",text="QA 3001 - Main Window"}
--%%u:{button="btn1",text="Create QA 3002",onReleased="createSecondQA"}
--%%u:{button="btn2",text="Create QA 3003",onReleased="createThirdQA"}

function QuickApp:onInit()
    self:debug("TestNewWindows QA initialized - this should be QA 3001")
    self:debug("ID: " .. self.id)
    
    -- Update the label to show the actual QA ID
    self:updateView("lbl1", "text", "QA " .. self.id .. " - Main Window")
end

function QuickApp:createSecondQA()
    self:debug("Creating window for QA 3002...")
    
    local emu = fibaro.plua
    local success = emu.lib.createQuickAppWindow(
        3002, 
        "QA 3002 Window", 
        500, 
        350, 
        300, 
        200
    )
    
    self:debug("QA 3002 window creation: " .. tostring(success))
    
    if success then
        self:updateView("lbl1", "text", "Created QA 3002 window!")
    else
        self:updateView("lbl1", "text", "Failed to create QA 3002 window")
    end
end

function QuickApp:createThirdQA()
    self:debug("Creating window for QA 3003...")
    
    local emu = fibaro.plua
    local success = emu.lib.createQuickAppWindow(
        3003, 
        "QA 3003 Window", 
        600, 
        450, 
        400, 
        250
    )
    
    self:debug("QA 3003 window creation: " .. tostring(success))
    
    if success then
        self:updateView("lbl1", "text", "Created QA 3003 window!")
    else
        self:updateView("lbl1", "text", "Failed to create QA 3003 window")
    end
end
