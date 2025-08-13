--%%name:UI Update Demo
--%%type:com.fibaro.binarySwitch
--%%desktop:true
--%%u:{button="btn1",text="Click Me!",onReleased="buttonPressed"}
--%%u:{label="status",text="Ready"}

local updateCount = 0

function QuickApp:onInit()
    self:debug("🚀 UI Update Demo started")
    self:updateView("status", "text", "Demo initialized")
    
    -- Automatically update UI every 2 seconds for demo
    setTimeout(function()
        self:autoUpdate()
    end, 2000)
end

function QuickApp:autoUpdate()
    updateCount = updateCount + 1
    local message = "Auto update #" .. updateCount .. " at " .. os.date("%H:%M:%S")
    
    self:debug("🔄 Auto updating status: " .. message)
    self:updateView("status", "text", message)
    
    if updateCount < 5 then
        setTimeout(function()
            self:autoUpdate()
        end, 2000)
    else
        self:debug("✅ Demo complete - shutting down soon")
        self:updateView("status", "text", "Demo complete! ✅")
    end
end

function QuickApp:buttonPressed()
    local timestamp = os.date("%H:%M:%S")
    local message = "Button clicked at " .. timestamp .. "!"
    
    self:debug("👆 Button pressed: " .. message)
    self:updateView("status", "text", message)
end
