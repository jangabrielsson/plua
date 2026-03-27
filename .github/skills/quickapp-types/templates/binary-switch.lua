--%%name:My Switch
--%%type:com.fibaro.binarySwitch
--%%u:{label="statusLbl",text="State: Off"}
--%%u:{{button="onBtn",text="Turn On",onReleased="turnOn"},{button="offBtn",text="Turn Off",onReleased="turnOff"}}

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:updateProperty("value", false)
end

function QuickApp:turnOn(event)
    -- add hardware/API call here
    self:updateProperty("value", true)
    self:updateView("statusLbl", "text", "State: On")
    self:debug("Turned on")
end

function QuickApp:turnOff(event)
    -- add hardware/API call here
    self:updateProperty("value", false)
    self:updateView("statusLbl", "text", "State: Off")
    self:debug("Turned off")
end
