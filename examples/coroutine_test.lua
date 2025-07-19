


local function asyncFun(a, b)
  local co = coroutine.running()
  setTimeout(function() coroutine.resume(co, a + b) end, 1000)  -- Simulate async delay
  return coroutine.yield()  -- Yield until the async operation completes
end

local res = asyncFun(8,9)
print("Result from asyncFun:", res)