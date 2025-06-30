--%%name:Files
--%%type:com.fibaro.binarySwitch
--%%file:examples/fibaro/libQA.lua,libA
--%%file:examples/fibaro/libQB.lua,libB

function QuickApp:onInit()
  self:debug("onInit")
  FunA()
  FunB()
end
