--%%name:Files
--%%type:com.fibaro.binarySwitch
--%%file:examples/fibaro/libQA.lua,libA
--%%file:examples/fibaro/libQB.lua,libB
--%%file:$plua.lib.aeslua53,aes
--%%project:888

function QuickApp:onInit()
  self:debug("onInit")
  FunA()
  FunB()
end
