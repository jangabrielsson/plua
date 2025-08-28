
--%%name:RestartTest


function QuickApp:onInit()
  self:debug("QuickApp initialized")
  plugin.restart(self.id)
end