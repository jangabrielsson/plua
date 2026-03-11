
-- bar(
-- setTimeout(function() foo() end,0)

function QuickApp:onInit()
local sensor = fibaro.plua.lib.loadQAString([[
--%%name:BinarySwitch
--%%type:com.fibaro.binarySwitch
function QuickApp:onInit()
    print("Loaded")
end
function QuickApp:test()
    print("Test") 
    fibaro.call(nil,"mm") 
end
]])

    --setTimeout(function()
    fibaro.call(5556,"test")
   -- end,0)
end
