--%%name:Children
--%%type:com.fibaro.binarySwitch
--%%debug:false
--%%var:X=9
--%%offline:true

---@class MyChild : QuickAppChild
MyChild = {}
class 'MyChild'(QuickAppChild)
function MyChild:__init(dev)
  QuickAppChild.__init(self,dev)
  self:debug("onInit",self.name,self.id)
end
function MyChild:turnOn() self:updateProperty("value",true) end
function MyChild:turnOff() self:updateProperty("value",false) end

function QuickApp:onInit()
  self:debug(self.name, self.id)

  -- Create children
  for i = 1,5 do 
    self:createChildDevice({name="MyChild"..i,type="com.fibaro.binarySwitch"},MyChild)
  end
  local children = api.get("/devices?parentId="..self.id)
  for _,c in ipairs(children) do 
    print(c.name)
  end

  setInterval(function() print("PING")end,2000) -- Keep alive
end

function QuickApp:turnOn() print("ON") self:updateProperty("value",true) end
function QuickApp:turnOff() print("OFF") self:updateProperty("value",false) end