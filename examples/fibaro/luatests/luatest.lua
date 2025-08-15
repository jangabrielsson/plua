local lfs = require('lfs')

local path = lfs.currentdir().."/examples/fibaro/luatests/"
local testFile

local function loadFiles()
  for file,m in lfs.dir(path) do
    if file:match('%.lua$') and file ~= 'luatest.lua' then
      testFile(file)
    end
  end
end

local lt = {}
function lt.assertType(value, expectedType)
  assert(type(value) == expectedType, "Expected type " .. expectedType .. " but got " .. type(value))
end

function lt.add(name, method, ...)
  if type(name) == 'table' then table.insert(lt.tests, name) return end
  if not lt.tests then lt.tests = {} end
  local args = {...}
  table.insert(lt.tests, {name = name, func = function() lt[method](table.unpack(args)) end})
end

local function testSync(test)
  local status, err = pcall(test.func)
  if not status then
    print("❌: " .. test.name .. " failed with error: " .. err)
  else
    print("✅: " .. test.name .. " passed")
  end
end

local function testAsync(t)
  local rtime = os.clock()
  local time = os.time()
  function done()
    print("✅: " .. t.name .. " completed",os.clock()-rtime,"s",os.time()-time,"s")
  end
  local co = coroutine.create(t.func)
  local stat,value = coroutine.resume(co,done)
  if not stat then
    print("❌: " .. t.name .. " - " .. t.name .. " failed with error: " .. value)
  end
end

function testFile(file)
  lt.tests = {}
  lt.file = file
  lt.name = ""
  local stat,err = pcall(function()
    return loadfile(path..file,"t",_G)(lt)
  end)
  if not stat then
    print("❌:" .. file .. " with error: " .. err)
  end
  for _,t in ipairs(lt.tests) do
    if t.func then
      if t.isAsync then testAsync(t) else testAsync(t) end
    end
  end
end

loadFiles()