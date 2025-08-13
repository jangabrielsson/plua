--%%desktop:true
--%%u:{label="lbl1",text="Initial text"}
--%%u:{button="btn1",text="Update Label",onReleased="btn1"}

local function onUIEvent(event)
    if event.elementName == "btn1" then
        print("🔄 Button clicked - updating label text via updateView")
        quickApp:updateView("lbl1", "text", "Button clicked at " .. os.date("%H:%M:%S"))
    end
end

function QuickApp:onInit()
    print("🚀 QuickApp started with ID:", self.id)
    print("💡 Click the button to test UI updates")
    
    -- Schedule automatic updates every 3 seconds for testing
    setTimeout(function()
        local timestamp = os.date("%H:%M:%S")
        print("🕒 Auto-updating label at", timestamp)
        self:updateView("lbl1", "text", "Auto-updated: " .. timestamp)
    end, 3000)
    
    setTimeout(function()
        local timestamp = os.date("%H:%M:%S")
        print("🕒 Auto-updating label at", timestamp)
        self:updateView("lbl1", "text", "Second update: " .. timestamp)
    end, 6000)
end
