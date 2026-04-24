--%%name:UserTime

--%%time:2026/11/30 12:00:00
--%%file:$fibaro.lib.speed,speed


local t = os.date("%Y/%m/%d %H:%M:%S")
print("Hello from the future",t)

local function test()
  setInterval(function() 
    local t = os.date("%Y/%m/%d %H:%M:%S")
    print("Current time is",t)
  end, 3600*1000)
end

fibaro.speedTime(24,test)