--%%name:Timers
--%%type:com.fibaro.binarySwitch

function QuickApp:onInit()
  self:debug("onInit")

  local timerB = setTimeout(function()
    self:debug("setTimeout B")
  end, 2000)

  setTimeout(function()
    self:debug("setTimeout A")
    print("Cancelling timer B")
    clearTimeout(timerB)
  end, 1000)

  local ref,n = nil,0
  ref = setInterval(function()
    print("PING!",n)
    n = n+1
    if n > 4 then
      clearInterval(ref)
    end
  end, 1000)

  self:debug("onInit done")
end

