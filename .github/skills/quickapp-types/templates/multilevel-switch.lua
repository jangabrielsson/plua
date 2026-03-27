--%%name:My Dimmer
--%%type:com.fibaro.multilevelSwitch
--%%u:{label="valueLbl",text="Value: 0%"}
--%%u:{slider="levelSlider",text="Level",min="0",max="99",value="0",onChanged="setLevel"}
--%%u:{{button="onBtn",text="On",onReleased="turnOn"},{button="offBtn",text="Off",onReleased="turnOff"}}

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:updateProperty("value", 0)
end

function QuickApp:turnOn(event)
    self:setValue(99)
end

function QuickApp:turnOff(event)
    self:setValue(0)
end

function QuickApp:setLevel(event)
    local v = tonumber(event.values[1])
    self:setValue(v)
end

function QuickApp:setValue(v)
    v = math.max(0, math.min(99, tonumber(v)))
    -- add hardware/API call here
    self:updateProperty("value", v)
    self:updateView("levelSlider", "value", tostring(v))
    self:updateView("valueLbl", "text", "Value: " .. v .. "%")
    self:debug("Set value:", v)
end
