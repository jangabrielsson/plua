--%%name:Basic
--%%type:com.fibaro.binarySwitch
--%%save:dev/basic.fqa
--%% proxy:true
--%%project:888
--%%desktop:true

function QuickApp:onInit()
  self:debug(self.name,self.id)

  print(coroutine.running())
  -- self:internalStorageSet("test","X")
  -- print("ISS",self:internalStorageGet("test"))

  setInterval(function() end,1000)
end

function QuickApp:turnOn()
  self:debug("Turning on")
  self:updateProperty("value",true)
end

function QuickApp:turnOff()
  self:debug("Turning off")
  self:updateProperty("value",false)
end