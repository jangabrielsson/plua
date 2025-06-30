--%%name:Basic
--%%type:com.fibaro.binarySwitch
--%%debug:false
--%%var:X=9
--%% offline:true

--%%u:{button='b1', text='Test button', onReleased='Fopp'}

---@class MyChild : QuickAppChild
MyChild = {}
class 'MyChild'(QuickAppChild)
function MyChild:__init(dev)
  QuickAppChild.__init(self,dev)
  self:debug("MyChild:__init")
end

function MyChild:test() print("Test child") end

print(json.encodeFast(json.initArray({})))

function QuickApp:onInit()
  self:debug("onInit")

  -- for i = 1,5 do 
  --   self:createChildDevice({name="MyChild"..i,type="com.fibaro.binarySwitch"},MyChild)
  -- end
  -- for _,c in ipairs(api.get("/devices?parentId="..self.id)) do 
  --   print(c.name)
  -- end
  -- print(self:getVariable("X"))
  -- setTimeout(function() print("OKOKOK") end,1)
  -- plugin.restart()
  -- function _PY.newRefreshStatesEvent(event)
  --   print("New",json.encode(event))
  -- end

  -- print(fibaro.plua.lib.hc3_url)
  -- print(fibaro.plua.lib.hc3_creds)
  -- _PY.pollRefreshStates(0, fibaro.plua.lib.hc3_url.."/api/refreshStates?last=", {
  --   headers = {Authorization = fibaro.plua.lib.hc3_creds}
  -- })

  -- --_PY.addEvent(json.encode({type='fopp',data={a=1,b=2}}))

  -- setInterval(function() end,1000) -- keep script alive

  -- self:updateProperty("value",true)
  -- api.post("/globalVariables",{name="Test42", value = "Hello"})
  -- print("Test42 =",fibaro.getGlobalVariable("Test42"))
  -- local v = api.get("/weather")
  -- print(string.format("Temperature is %.02f°",v.Temperature))
  -- local devices = api.get("/devices?interface=quickApp")
  -- print(json.encodeFormated(devices[1]))
  -- setTimeout(function() fopp() end,0)
  -- local me = api.get("/devices/5555")
  -- print(json.encodeFormated(me))
  -- local v = api.get("/devices/5555/properties/deviceIcon")
  -- print(v.value)
  -- fibaro.call(self.id,"test",1,2)
  -- self:updateProperty('value',false)
  -- print(fibaro.getValue(self.id,"value"))
  -- self:updateProperty('value',true)
  -- print(fibaro.getValue(self.id,"value"))

--   local refresh = RefreshStateSubscriber()
--   local handler = function(event)
--     if event.type == "DevicePropertyUpdatedEvent" then
--       print(json.encode(event.data))
--     end
--   end
--   refresh:subscribe(function() return true end,handler)
--   refresh:run()
--   setInterval(function() end,1000)
end

-- function QuickApp:test(x,y)
--   print("test",x,y)
-- end