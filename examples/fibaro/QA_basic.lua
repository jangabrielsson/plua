--%%name:Basic
--%%type:com.fibaro.binarySwitch
--%%save:dev/basic.fqa
--%% proxy:true
--%%project:888
--%%desktop:true

function QuickApp:onInit()
  self:debug(self.name,self.id)

  self:updateProperty("value",true)
  --setTimeout(function() self:updateProperty("value",false) end,3000)
  -- self:internalStorageSet("test","X")
  -- print("ISS",self:internalStorageGet("test"))

  local val = true
  setInterval(function() 
    val = not val
    print(val)
    self:updateProperty("value",val) 
    end,2000)
end

function QuickApp:turnOn()
  self:debug("Turning on")
  setTimeout(function() self:updateProperty("value",true) end,0)
end

function QuickApp:turnOff()
  self:debug("Turning off")
  setTimeout(function() self:updateProperty("value",false) end,0)
end