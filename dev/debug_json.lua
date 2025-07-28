

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

--[[

The key insight is that on Windows, certain cleanup operations (especially threading-related ones) can sometimes deadlock, so we need aggressive timeout protection to ensure the process can always exit.
--]]