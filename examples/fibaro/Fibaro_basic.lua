print("Hello")

local a =setTimeout(function() print("A") end, 5000)
clearTimeout(a)

local n,ref = 0,nil
ref = setInterval(function()
  n = n+1
  print("B")
  if n > 5 then
    print("Stop")
    clearInterval(ref)
  end
end, 1000)
