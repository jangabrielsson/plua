--%%name:LogConfig

function QuickApp:onInit()
  local vs = {}
  for k,v in pairs(fibaro.plua.config) do
    v = type(v)=='table' and json.encode(v) or tostring(v)
    vs[#vs+1] = string.format("%s: %s", k, v)
  end
  table.sort(vs)
  for _,v in ipairs(vs) do
    print(v)
  end
end