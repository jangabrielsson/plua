--%%name:Simple QA
--%%type:com.fibaro.binarySwitch

FIBTEST:setup{name='Simple QA'}

function QuickApp:onInit()
  self:debug(self.name,self.id)
  FIBTEST:done()
end
