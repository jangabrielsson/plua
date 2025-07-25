--%%name:Player
--%%type:com.fibaro.player
--%%description:"My description"
-- Player type should handle actions: play, pause, stop, next, prev, setVolume, setMute
-- To update player state, update properties:
-- * "volume" with integer 0-100
-- * "mute" with boolean
-- * "power" with boolean

function QuickApp:play()
    self:debug("handle play")
end

function QuickApp:pause()
    self:debug("handle pause")
end

function QuickApp:stop()
    self:debug("handle stop")
end

function QuickApp:next()
    self:debug("handle next")
end

function QuickApp:prev()
    self:debug("handle prev")
end

function QuickApp:setVolume(volume)
    self:debug("setting volume to:", volume)
    self:updateProperty("volume", volume)
end

function QuickApp:setMute(mute)
    if mute == 0 then 
        self:debug("setting mute to:", false)
        self:updateProperty("mute", false)
    else
        self:debug("setting mute to:", true)
        self:updateProperty("mute", true)
    end
end 

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end

-- Player type have no actions to handle