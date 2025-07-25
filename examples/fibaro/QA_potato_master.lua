--%%name:PotatoMaster
--%%type:com.fibaro.multilevelSwitch
--%% debug:true
--%%offline:true

function QuickApp:onInit()
  self:debug("onInit",self.name,self.id)
  setTimeout(function()
    fibaro.call(5001,"pass","Potato")
  end,0)
  for i=1,100 do
    local friend = i == 100 and 5001 or 5001+i
    fibaro.plua.loadQA("examples/QA_potato_client.lua",{var="friend="..friend})
  end
  setInterval(function()
    print("PING")
  end,2000)
end

function QuickApp:pass(str)
  print("Already have a potato")
end