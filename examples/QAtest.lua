--%%name:QAtest
--%%type:com.fibaro.binarySwitch
--%%file:libQA.lua,lib
print("QAtest")
function QuickApp:onInit()
  self:debug("onInit")
  local endTime,ref = os.time()+5,nil
  local n = 0
  -- ref = setInterval(function()
  --   print("PING",os.date("%Y-%m-%d %H:%M:%S"),n)
  --   n = n+1
  --   if endTime <= os.time() then
  --     clearInterval(ref)
  --   end
  -- end, 500)
  local function loop()
    print("PING",os.date("%Y-%m-%d %H:%M:%S"),n)
    n = n+1
    if endTime > os.time() then
      setTimeout(loop,500)
    end
  end
  loop()
end

function QuickApp:onStart()
  self:debug("onStart")
end

function QuickApp:onStop()
  self:debug("onStop")
end