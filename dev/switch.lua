--%%name:Test
--%%desktop:true
--%%u:{switch="autoMode",text="Auto Mode",value=true,onToggled="toggleAutoMode"}

function QuickApp:onInit()
  self:debug("init")
  setTimeout(function()
  self:updateView('autoMode','text',"Fopp8")
  end,1000)
  --self:updateView('__turnOn','text',"Kopp2")
end

function QuickApp:toggleAutoMode(value)
  self:debug("Auto Mode Toggled:", value)
  --self:updateProperty("autoMode",value)
end