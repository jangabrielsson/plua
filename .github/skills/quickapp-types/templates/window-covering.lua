--%%name:WindowCovering
--%%type:com.fibaro.windowCovering
--%%description:Window covering template

-- Actions: open, close, stop, setValue
-- value property: integer 0-99 (% open)

function QuickApp:open()
    self:debug("Opening")
    -- add hardware/API call here
    self:updateProperty("value", 99)
end

function QuickApp:close()
    self:debug("Closing")
    -- add hardware/API call here
    self:updateProperty("value", 0)
end

function QuickApp:stop()
    self:debug("Stopped")
    -- add hardware/API call here
end

-- value: integer 0-99
function QuickApp:setValue(value)
    self:debug("Setting position:", value)
    -- add hardware/API call here
    self:updateProperty("value", value)
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
end
