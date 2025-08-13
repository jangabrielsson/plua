--%%name:WindowReuseTest
--%%type:com.fibaro.device  
--%%desktop:true
--%%debug:true
--%%u:{label="lbl1",text="QA Window Reuse Test"}
--%%u:{button="btn1",text="Create QA 6001 (small)",onReleased="createSmallWindow"}
--%%u:{button="btn2",text="Create QA 6001 again (should reuse)",onReleased="reuseSmallWindow"}
--%%u:{button="btn3",text="Create QA 6002 (large)",onReleased="createLargeWindow"}

function QuickApp:onInit()
    self:debug("WindowReuseTest initialized with ID: " .. self.id)
    self:updateView("lbl1", "text", "QA " .. self.id .. " - Click buttons to test")
end

function QuickApp:createSmallWindow()
    self:debug("Creating small window for QA 6001...")
    
    local emu = fibaro.plua
    local success = emu.lib.createQuickAppWindow(
        6001, 
        "QA 6001 Small Window", 
        400,  -- Small size
        300, 
        100,  -- Top-left position
        100
    )
    
    self:debug("QA 6001 small window creation: " .. tostring(success))
    self:updateView("lbl1", "text", "Created QA 6001 (400x300)")
end

function QuickApp:reuseSmallWindow()
    self:debug("Trying to reuse QA 6001 window (should reuse, not create new)...")
    
    local emu = fibaro.plua
    local success = emu.lib.createQuickAppWindow(
        6001,  -- Same QA ID as before
        "QA 6001 Reused Window", 
        600,  -- Different size (should be ignored due to reuse)
        500, 
        200,  -- Different position (should be ignored due to reuse)
        200
    )
    
    self:debug("QA 6001 reuse attempt: " .. tostring(success))
    self:updateView("lbl1", "text", "Reused QA 6001 (should still be 400x300)")
end

function QuickApp:createLargeWindow()
    self:debug("Creating large window for QA 6002...")
    
    local emu = fibaro.plua
    local success = emu.lib.createQuickAppWindow(
        6002, 
        "QA 6002 Large Window", 
        800,  -- Large size
        600, 
        400,  -- Different position
        300
    )
    
    self:debug("QA 6002 large window creation: " .. tostring(success))
    self:updateView("lbl1", "text", "Created QA 6002 (800x600)")
end
