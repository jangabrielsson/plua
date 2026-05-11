
-- bar(
-- setTimeout(function() foo() end,0)

local a = api.get("/notificationCenter")
print(a)
setInterval(function() print("tick") end, 1000)