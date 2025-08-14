--%%name:LogConfig

function QuickApp:onInit()
  for k,v in pairs(fibaro.plua.config) do
    v = type(v)=='table' and json.encode(v) or tostring(v)
    print(k,v)
  end
end