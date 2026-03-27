--%%name:RemoteController
--%%type:com.fibaro.remoteController
--%%description:Remote controller template

-- No actions to handle.
-- Use emitCentralSceneEvent to emit button press events.
-- HC3 Scenes can trigger on these events.
-- keyAttributes: "Pressed", "Released", "HeldDown", "Pressed2", "Pressed3"

function QuickApp:emitCentralSceneEvent(keyId, keyAttribute)
    keyAttribute = keyAttribute or "Pressed"
    api.post("/plugins/publishEvent", {
        type = "centralSceneEvent",
        source = self.id,
        data = { keyAttribute = keyAttribute, keyId = keyId }
    })
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    -- Declare supported keys so HC3 scenes can list them as triggers
    self:updateProperty("centralSceneSupport", {
        { keyId = 1, keyAttributes = {"Pressed","Released","HeldDown","Pressed2","Pressed3"} },
        { keyId = 2, keyAttributes = {"Pressed","Released","HeldDown","Pressed2","Pressed3"} },
        { keyId = 3, keyAttributes = {"Pressed","Released","HeldDown","Pressed2","Pressed3"} },
        { keyId = 4, keyAttributes = {"Pressed","Released","HeldDown","Pressed2","Pressed3"} },
    })
    -- Example: emit button 1 press after 2 seconds
    -- setTimeout(function() self:emitCentralSceneEvent(1, "Pressed") end, 2000)
end
