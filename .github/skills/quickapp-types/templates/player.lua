--%%name:Player
--%%type:com.fibaro.player
--%%description:Media player template

-- Actions: play, pause, stop, next, prev, setVolume, setMute
-- Properties: volume (0-100), mute (boolean), power (boolean)

function QuickApp:play()
    self:debug("Play")
    -- add hardware/API call here
    self:updateProperty("power", true)
end

function QuickApp:pause()
    self:debug("Pause")
    -- add hardware/API call here
end

function QuickApp:stop()
    self:debug("Stop")
    -- add hardware/API call here
    self:updateProperty("power", false)
end

function QuickApp:next()
    self:debug("Next track")
    -- add hardware/API call here
end

function QuickApp:prev()
    self:debug("Previous track")
    -- add hardware/API call here
end

-- volume: integer 0-100
function QuickApp:setVolume(volume)
    self:debug("Volume:", volume)
    -- add hardware/API call here
    self:updateProperty("volume", volume)
end

-- mute: 0 (unmute) or non-zero (mute) — note: HC3 passes 0/1 not boolean
function QuickApp:setMute(mute)
    local m = mute ~= 0
    self:debug("Mute:", m)
    -- add hardware/API call here
    self:updateProperty("mute", m)
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:updateProperty("power", false)
    self:updateProperty("volume", 50)
    self:updateProperty("mute", false)
end
