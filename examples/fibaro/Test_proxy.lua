--%%name:TestProxy
--%%proxy:true
--%%var:x=42
--%%interfaces:{}
--%% proxyupdate:ui,vars,interfaces
--%% offline:true

--%%u:{label='l1', text="Hello"}

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
  self:debug(self.name,self.id)
  --api.delete("/devices/4119")
  -- Set variable through internal api, should be visible on proxy
  self:internalStorageSet("testVar","testValue")

  -- Get direct access to internal storage
  local a,b = api.hc3.restricted.get("/plugins/"..self.id.."/variables")
  -- SHould return 'con' variable usde for proxy connection, and 'testVar'
  self:debug(json.encode(a))

  local t0,n = os.clock(),10
  for i=1,n do
    self:internalStorageSet("testVar","testValue"..i)
  end
  print("Time for internalStorageSet:",(os.clock()-t0)/n*1000,"ms")

  local children = api.get("/devices?parentId="..self.id)
  if children == nil or next(children) == nil then
    self:createChildDevice({name="MyChild",type="com.fibaro.binarySwitch"},MyChild)
  else
    local map = {["com.fibaro.binarySwitch"]=MyChild}
    self:initChildDevices(map)
  end

  self:updateView('l1','text','Hello again')
  setInterval(function() print("PING")end,4000) -- Keep alive
end