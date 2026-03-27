--%%name:AlarmPartition
--%%type:com.fibaro.alarmPartition
--%%description:Alarm partition template

-- Actions: arm, disarm
-- armed property: boolean
-- alarm property: boolean (true = breached)

function QuickApp:arm()
    self:debug("Arming")
    -- add hardware/API call here
    self:updateProperty("armed", true)
end

function QuickApp:disarm()
    self:debug("Disarming")
    -- add hardware/API call here
    self:updateProperty("armed", false)
end

-- Call this to indicate a breach/alarm state
function QuickApp:setBreached(state)
    self:updateProperty("alarm", state)
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:updateProperty("armed", false)
    self:updateProperty("alarm", false)
end
