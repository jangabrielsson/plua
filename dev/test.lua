--%%name:Test
--%%u:{switch='tt', text='Test', value='true', onReleased='onTestChanged'}
--%%desktop:true

function QuickApp:onInit()
  self:debug('onInit')
end

function QuickApp:onTestChanged(value)
  self:debug('onTestChanged', type(value.values[1]))
end