--%%name:RemoteController
--%%type:com.fibaro.remoteController
--%%description:"My description"
--%%desktop:true

-- Remote controller type have no actions to handle

-- Method for emitting central scene events. Default value for keyAttribute is "Pressed" 
-- Sample usage: self:emitCentralSceneEvent(1, "Pressed")
function QuickApp:emitCentralSceneEvent(keyId, keyAttribute)
    if keyAttribute == nil then
        keyAttribute = "Pressed"
    end

    local eventData = {
        type = "centralSceneEvent",
        source = self.id,
        data = {
            keyAttribute = keyAttribute,
            keyId = keyId
        }
    }
    api.post("/plugins/publishEvent", eventData)
end

-- To update controls you can use method self:updateView(<component ID>, <component property>, <desired value>). Eg:  
-- self:updateView("slider", "value", "55") 
-- self:updateView("button1", "text", "MUTE") 
-- self:updateView("label", "text", "TURNED ON") 

-- This is QuickApp inital method. It is called right after your QuickApp starts (after each save or on gateway startup). 
-- Here you can set some default values, setup http connection or get QuickApp variables.
-- To learn more, please visit: 
--    * https://manuals.fibaro.com/home-center-3/
--    * https://manuals.fibaro.com/home-center-3-quick-apps/

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end

    -- Setup supported keys and attributes of the device
    -- Scenes will display possible triggers according to these values
    self:updateProperty("centralSceneSupport",  {
        { keyAttributes = { "Pressed","Released","HeldDown","Pressed2","Pressed3" }, keyId = 1 },
        { keyAttributes = { "Pressed","Released","HeldDown","Pressed2","Pressed3" }, keyId = 2 },
        { keyAttributes = { "Pressed","Released","HeldDown","Pressed2","Pressed3" }, keyId = 3 },
        { keyAttributes = { "Pressed","Released","HeldDown","Pressed2","Pressed3" }, keyId = 4 },
        { keyAttributes = { "Pressed","Released","HeldDown","Pressed2","Pressed3" }, keyId = 5 },
        { keyAttributes = { "Pressed","Released","HeldDown","Pressed2","Pressed3" }, keyId = 6 },
    })
end 