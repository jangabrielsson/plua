--%%name:TestQA
--%%type:com.fibaro.multilevelSwitch

---ENDOFHEADERS----

fibaro.plua.lib.loadQAString([[
--%%name:SQA
--%%type:com.fibaro.multilevelSwitch
--%%breakonload:true

function QuickApp:onInit()
  self:debug(self.name, self.id)
end

function QuickApp:turnOn()
  self:debug("Turning on")
  self:updateProperty("value", 99)
end

function QuickApp:turnOff()
  self:debug("Turning off")
  self:updateProperty("value", 0)
end

]])

function QuickApp:onInit()
  self:debug("TestQA started")
end


