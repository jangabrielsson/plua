


local devs,code = api.get("/rooms")
if devs then
  print("There are " .. #devs .. " CEs")
end
