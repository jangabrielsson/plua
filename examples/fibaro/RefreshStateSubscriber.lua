--%%name:RefreshStateSubscriber
--%%type:com.fibaro.binarySwitch  
  
  local refresh = RefreshStateSubscriber()
  local handler = function(event)
    if event.type == "DevicePropertyUpdatedEvent" then
      print(json.encode(event.data))
    end
  end
  refresh:subscribe(function() return true end,handler)
  refresh:run()

function QuickApp:onInit()
  self:debug("RefreshStateSubscriber initialized")
  -- Keep script alive
  self:updateProperty('value',not fibaro.getValue(self.id,"value"))
end