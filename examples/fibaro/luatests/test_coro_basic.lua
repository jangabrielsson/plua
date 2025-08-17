--%%name:Coro basic
--%%type:com.fibaro.binarySwitch

FIBTEST:setup{name='Coro basic', tests = 1}

function QuickApp:onInit()
  self:debug(self.name,self.id)
  
  coroutine.wrap(function()
    local co = coroutine.running()
    setTimeout(function() coroutine.resume(co,"Hello from coroutine") end, 0)
    local value = coroutine.yield()
    FIBTEST:assert(value == "Hello from coroutine","Coroutine did not return expected value")
  end)()
end
