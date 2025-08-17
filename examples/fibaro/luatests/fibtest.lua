--%%name:fibtest
local lfs = require('lfs')
local function printf(fmt, ...) print(string.format(fmt, ...)) end
local fmt = string.format 

local path = lfs.currentdir().."/examples/fibaro/luatests/"
local testQA

local function loadFiles()
  for file,m in lfs.dir(path) do
    if file:match('%.lua$') and file ~= 'fibtest.lua' then
      testQA(file)
    end
  end
end

FibTest = FibTest
class 'FibTest'
function FibTest:__init(file)
  self.file = file
  self.runtime = os.clock()
  self.time = os.time()
end

function FibTest:setup(args)
  self.name = args.name or self.file:match("([^/]+)%.lua$")
  self.numberOfTests = args.tests or 1
  self.testsCompleted = 0
  self.errors = {}
end

function fibaro.plua.EVENT._qaEnvSetup(ev)
  local info = ev.info
  if info.device.name == 'fibtest' then return end
  function info.env.QuickApp.debug(...) end -- Disable debug output
  function info.env.print(...) end
end

function FibTest:cleanup()
  api.delete("/devices/"..self.info.device.id)
end

function FibTest:testCompleted()
  self.testsCompleted = self.testsCompleted + 1
  if self.testsCompleted >= self.numberOfTests then
    self:done()
  end
end

function FibTest:testError(msg)
  table.insert(self.errors, msg)
  self:testCompleted()
end

function FibTest:assert(value, fmt, ...)
  if value then self:testCompleted()
  else self:testError(string.format(fmt, ...)) end
end

function FibTest:done()
  if #self.errors > 0 then
    for _, err in ipairs(self.errors) do
      printf("❌: '%s' failed with errors: %s", self.name, table.concat(self.errors, ", "))
    end
  else
    printf("✅: %-20s passed (CT:%0.3fs, RT:%0.3fs)", "'"..self.name.."'", os.clock()-self.runtime, os.time()-self.time)
  end
  self:cleanup()
end

function FibTest:runQA(func, info)
  self.info = info
  local function runner()
    xpcall(func,function(err)
      printf("❌: '%s' failed with error: %s", self.name, tostring(err))
      self:cleanup()
    end)
  end
  setTimeout(runner,0)
end

function coroutine.wraptest(func, info) 
  if info.device.name == 'fibtest' then return func() end
  info.env.FIBTEST:runQA(func,info) 
end

-- print("❌: " .. test.name .. " failed with error: " .. err)

function testQA(file)
  local ft = FibTest(file)
  local function fibtestPrint(...) end
  local qa = fibaro.plua.lib.loadQA(path..file,{env={FIBTEST=ft, print=fibtestPrint}})
end

loadFiles()