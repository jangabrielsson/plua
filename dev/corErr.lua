--%%name:TestErr
--%%offline:true
--%%speed:24


function QuickApp:onInit()
    fibaro.speedTime(24,function()
    setInterval(function()
    print(fibaro.getValue(1,"sunriseHour"))
    print(fibaro.getValue(1,"sunsetHour"))
    end,1000*60*60)
end)
end
