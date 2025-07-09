--%%name:Basic
--%%type:com.fibaro.binarySwitch
--%%save:dev/basic.fqa
--%%proxy:true

function QuickApp:onInit()
  self:debug(self.name,self.id)

  self:internalStorageSet("test","X")
  print("ISS",self:internalStorageGet("test"))

  setInterval(function() end,1000)
end
