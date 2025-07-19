  local function foo()
    print("A")
    local co = coroutine.running()
    setTimeout(function() coroutine.resume(co) print("D") end, 1000)
    print("B")
    coroutine.yield()
    print("C")
  end
  coroutine.wrap(foo)()
  