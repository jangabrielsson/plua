--%%name:MyQA
--%%type:com.fibaro.binarySwitch
--%%offline:true

function QuickApp:onInit()
  self:debug(self.name,self.id)
end

function QuickApp:turnOn()
  self:debug("Turning on")
  self:updateProperty("value", true)
end

function QuickApp:turnOff()
  self:debug("Turning off")
  self:updateProperty("value", false)
end