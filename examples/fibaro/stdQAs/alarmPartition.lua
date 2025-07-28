--%%name:alarmPartition
--%%type:com.fibaro.alarmPartition
--%%description:"My description"

-- Alarm partition type should handle following actions: arm, disarm
-- To update arm state of alarm partition, update property "armed" with boolean
-- To update alarm state of alarm partiton, update property "alarm" with boolean
-- Eg. self:updateProperty("alarm", true) will indicate that alarm partition was breached

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

function QuickApp:arm()
    self:debug("alarm partition armed")
    self:updateProperty("armed", true)
end

function QuickApp:disarm()
    self:debug("alarm partition disarmed")
    self:updateProperty("armed", false)    
end 

function QuickApp:breached(state)
    self:debug("alarm partition breached: " .. tostring(state))
    self:updateProperty("alarm", state)    
end 