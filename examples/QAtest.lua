--%%name:QAtest
--%%type:com.fibaro.binarySwitch
--%%file:libQA.lua,lib
print("QAtest")
function QuickApp:onInit()
  self:debug("onInit")
  local n,ref = 0,nil
  ref = setInterval(function()
    print("PING",os.date("%Y-%m-%d %H:%M:%S"))
    n = n+1
    if n > 5 then
      clearInterval(ref)
    end
  end, 1000)
end

-- function QuickApp:onStart()
--   self:debug("onStart")
-- end

-- function QuickApp:onStop()
--   self:debug("onStop")
-- end