--%%name:Files
--%%type:com.fibaro.binarySwitch
--%%file:demos/libQA.lua,libA
--%%file:demos/libQB.lua,libB

function QuickApp:onInit()
  self:debug("onInit")
  FunA()
  FunB()
end
