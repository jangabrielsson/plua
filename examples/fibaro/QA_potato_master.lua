--%%name:PotatoMaster
--%%type:com.fibaro.multilevelSwitch
--%% debug:true
--%%offline:true

function QuickApp:onInit()
  self:debug("onInit",self.name,self.id)
  setTimeout(function()
    fibaro.call(5556,"pass","Potato")
  end,0)
  local n = 100
  for i=1,n do
    local friend = i == n and 5555 or 5556+i
    fibaro.plua.lib.loadQA("examples/fibaro/QA_potato_client.lua",{"var:friend="..friend})
  end
  setInterval(function()
    print("PING")
  end,2000)
end

function QuickApp:pass(str)
  print("Already have a potato")
end