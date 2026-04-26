--%%name:UserTime

--%%time:2026/11/30 12:00:00
--%%speed:24


local t = os.date("%Y/%m/%d %H:%M:%S")
print("Hello from the future",t)
local a = _PY
local function test()
  setInterval(function() 
    local t = os.date("%Y/%m/%d %H:%M:%S")
    print("Current time is",t)
  end, 3600*1000)
end

local time = fibaro.plua.DIR[plugin.mainDeviceId].headers.speed
fibaro.speedTime(time,test)