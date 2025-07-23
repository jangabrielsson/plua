--%%name:QATest
--%%type:com.fibaro.binarySwitch
--%%proxy:true

--%%u:{label='lbl1', text='My label'}
--%%u:{button='button_ID_1_1', text='Turn on', onReleased='turnOn2'}

function QuickApp:onInit()
  self:debug("onInit")
  setInterval(function() self:debug("Interval") end,3000) -- Keep the QA alive
end

function QuickApp:test(x,y)
  self:debug("Plus",x,y,"=",x+y)
end

function QuickApp:turnOn()
  print("Turn on")
end

function QuickApp:turnOff()
  print("Turn off")
end

function QuickApp:turnOn2()
  print("Turn on 2")
end