

local max = 1000

for i=1,1000 do
  local n = i
  setTimeout(function() 
    print(n)
    if n == max then 
      print("Done")
      os.exit() 
    end 
  end,1)
end