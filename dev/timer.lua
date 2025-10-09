
local function timer(time,callback)
  assert(type(time)=='string' and time:match("^%d%d:%d%d$"),"Invalid time format, expected HH:MM")
  assert(type(callback)=='function',"Callback must be a function")
  local h,m = time:match("^(%d%d):(%d%d)$")
  local t = os.date("*t")
  local offset = (h-t.hour)*3600 + (m-t.min)*60
  return setTimeout(callback,offset*1000)
end

local ref = timer("21:08",function() print("Timer at 21:08") end)
print(ref)