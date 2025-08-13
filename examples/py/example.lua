-- Sample Lua script for testing the EPLua CLI
print("Hello from EPLua!")
print("Setting up some timers...")

-- Test simple timeout
_PY.setTimeout(function()
    print("Timer 1: This runs after 1 second")
end, 1000)

-- Test interval
local count = 0
local intervalId 
intervalId = _PY.setInterval(function()
    count = count + 1
    print("Interval: Count is now " .. count)
    
    if count >= 3 then
        print("Stopping interval after 3 iterations")
        _PY.clearInterval(intervalId)
    end
end, 500)

-- Test multiple timeouts
_PY.setTimeout(function()
    print("Timer 2: This runs after 2 seconds")
end, 2000)

_PY.setTimeout(function()
    print("Timer 3: Final timer after 3 seconds")
    print("Script will complete soon...")
end, 3000)

local function wait(ms)
  local co = coroutine.running()
  _PY.setTimeout(function()
    coroutine.resume(co)
  end, ms)
  coroutine.yield()
end

print(_PY.to_json({2,3,4}))

local function testWait()
    print(os.date("%H:%M:%S") .. " - Waiting for 2 seconds...")
    wait(2000)
    print(os.date("%H:%M:%S") .. " - Wait complete!")
end

testWait()

print("Initial setup complete, waiting for timers...")
