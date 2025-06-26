--%%name:MyQA
--%%type:com.fibaro.binarySwitch
--%%file:test/libQA.lua,lib

print("QAtest")
function QuickApp:onInit()
  self:debug("onInit")
  fibaro._plua.traceback = true
  fibaro._plua.shortTime = true
  
  net:HTTPClient():request("http://google.com",{
    success = function(response)
      print("success")
    end,
    error = function(response)
      print("error",response)
    end
  })
  -- local endTime,ref = os.time()+3,nil
  -- local n = 0
  -- ref = setInterval(function()
  --   print("PING",os.date("%Y-%m-%d %H:%M:%S"),n)
  --   n = n+1
  --   if endTime <= os.time() then
  --     clearInterval(ref)
  --   end
  -- end, 500)
--   local function loop()
--     print("PING",os.date("%Y-%m-%d %H:%M:%S"),n)
--     n = n+1
--     if endTime > os.time() then
--       setTimeout(loop,500)
--     end
--   end
--   loop()
end
print("Done")
function QuickApp:onStart()
  self:debug("onStart")
end

function QuickApp:onStop()
  self:debug("onStop")
end