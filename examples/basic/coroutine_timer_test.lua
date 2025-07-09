-- Test coroutine pattern with timer callbacks
-- Based on the pattern from test1.lua

local function async_call(str, func)
  setTimeout(function()
    func("echo:"..str)
  end, 1000)
end

local function ask(str)
  local co = coroutine.running()
  async_call(str, function(resp) coroutine.resume(co, resp) end)
  return coroutine.yield()
end

-- Test function that runs in a coroutine
local function test_timer()
  print("Testing coroutine pattern with timer...")
  local result = ask("Hello")
  print("Result:", result)
  print("Test completed!")
end

-- Start the test in a coroutine
local co = coroutine.create(test_timer)
coroutine.resume(co) 