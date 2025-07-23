--%%name:Basic
--%%type:com.fibaro.binarySwitch
--%%debug:false
--%%var:X=9
--%% offline:true

---@class MyChild : QuickAppChild
MyChild = {}
class 'MyChild'(QuickAppChild)
function MyChild:__init(dev)
  QuickAppChild.__init(self,dev)
  self:debug("MyChild:__init")
end

function MyChild:test() print("Test child") end

function QuickApp:onInit()
  self:debug(self.name, self.id)

  -- Create children
  for i = 1,5 do 
    self:createChildDevice({name="MyChild"..i,type="com.fibaro.binarySwitch"},MyChild)
  end
  for _,c in ipairs(api.get("/devices?parentId="..self.id)) do 
    print(c.name)
  end

  -- Access variable set in header
  print("X=",self:getVariable("X"))

  -- Test calling ourself
  fibaro.call(self.id,"test",1,2)

  local refresh = RefreshStateSubscriber()
  local handler = function(event)
    if event.type == "DevicePropertyUpdatedEvent" then
      print(json.encode(event.data))
    end
  end
  refresh:subscribe(function() return true end,handler)
  refresh:run()

  fibaro.sleep(1000)
  self:updateProperty('value',false)
  print("value=",fibaro.getValue(self.id,"value"))
  self:updateProperty('value',true)
  print("value=",fibaro.getValue(self.id,"value"))

  setInterval(function() end,1000) -- Keep script alive
end

function QuickApp:test(x,y)
  print("test",x,y)
end