print("Hello")

local p = package.searchpath("socket",package.path)
print(p)
local a =setTimeout(function() print("A") end, 5000)
clearTimeout(a)
 fibaro.sleep(1000)
local n,ref = 0,nil
ref = setInterval(function()
  n = n+1
  print("B",n)
  if n > 5 then
    print("Stop")
    clearInterval(ref)
  end
end, 1000)

function QuickApp:onInit()
  self:debug(self.name,self.id)
  setInterval(function () print("C") end, 1000)
end
