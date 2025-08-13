--%%name:TestWindowQA
--%%type:com.fibaro.device  
--%%desktop:true
--%%debug:true
--%%u:{label="lbl1",text="Hello from QA 5555!"}
--%%u:{button="btn1",text="Test Button",onReleased="testButton"}

function QuickApp:onInit()
    self:debug("TestWindowQA initialized - should open in new Safari window")
    
    -- Test creating additional windows manually
    local emu = fibaro.plua
    
    setTimeout(function()
        self:debug("Creating window for QA 6666...")
        local success = emu.lib.createQuickAppWindow(
            6666, 
            "Test QA 6666", 
            500, 
            350, 
            300, 
            200
        )
        self:debug("QA 6666 window creation: " .. tostring(success))
        
        setTimeout(function()
            self:debug("Creating window for QA 7777...")
            local success2 = emu.lib.createQuickAppWindow(
                7777, 
                "Test QA 7777", 
                600, 
                450, 
                400, 
                250
            )
            self:debug("QA 7777 window creation: " .. tostring(success2))
        end, 3000)
    end, 2000)
end

function QuickApp:testButton()
    self:debug("Button clicked in QA " .. self.id)
    self:updateView("lbl1", "text", "Button clicked at " .. os.date("%H:%M:%S"))
end
