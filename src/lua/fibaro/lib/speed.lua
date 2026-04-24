local speed = {}
local timeOffset = os.time() 

local old__fibaro_add_debug_message = fibaro.plua.lib.__fibaro_add_debug_message

function fibaro.plua.lib.__fibaro_add_debug_message(tag, msg, typ, time)
  local t = time or os.time()
  old__fibaro_add_debug_message(tag, msg, typ, t)
end

local _setTimeout,_clearTimeout,_setInterval,_clearInterval = setTimeout,clearTimeout,setInterval,clearInterval
local _time,_date = os.time,os.date

local orgTime,orgDate,timeOffset = os.time,os.date,0

local function round(x) return math.floor(x+0.5) end
function speed.userTime(a) 
  return a == nil and round(_time() + timeOffset) or _time(a) 
end
local function userMilli() return _time() + timeOffset end
function speed.userDate(a, b) 
  return b == nil and orgDate(a, speed.userTime()) or _date(a, round(b)) 
end

local function getTimeOffset() return timeOffset end
local function setTimeOffset(offs) timeOffset = offs end

local function createQueue()
  local self = {}
  local times = nil -- linked list of sorted timers
  
  function self:add(t,fun,id)
    local v = nil
    v = {time=t,fun=fun,id=id}
    if not times then times = v return v end
    if t < times.time then
      times.prev = v
      v.next = times
      times = v
      return v
    end
    local p = times
    while p.next and p.next.time < t do p = p.next end
    v.next = p.next
    if p.next then p.next.prev = v end
    p.next = v
    v.prev = p
    return v
  end
  
  function self:remove(v)
    if v and not v.dead then
      v.dead = true
      if v.prev == nil then
        times = v.next
        if times then times.prev = nil end
      elseif v.next == nil then
        v.prev.next = nil
      else
        v.prev.next = v.next
        v.next.prev = v.prev
      end
    end
  end
  
  function self:pop() local t = times; if times then times.dead=true  times = times.next end return t end
  function self:peek() return times end
  return self
end

local timers = createQueue()
local timerID = 0
local timerIDs = {}

function speed.setTimeout(fun,ms)
  timerID = timerID + 1
  local v = timers:add(speed.userTime()+ms/1000,fun,timerID)
  timerIDs[timerID] = v
  return timerID
end

function speed.clearTimeout(ref)
  if timerIDs[ref] then
    timers:remove(timerIDs[ref])
    timerIDs[ref] = nil
  end
end

local intervID = 0
local intervIDs = {}

function speed.setInterval(fun,ms)
  local function loop()
    if not intervIDs[intervID] then return end
    fun()
    if not intervIDs[intervID] then return end
    intervIDs[intervID] = speed.setTimeout(loop,ms)
  end
  intervID = intervID + 1
  intervIDs[intervID] = speed.setTimeout(loop,ms)
  return intervID
end

function speed.clearInterval(ref)
  if intervIDs[ref] then
    speed.clearTimeout(intervIDs[ref])
    intervIDs[ref] = nil
  end
end

local running = false
function speed.loop()
  if running then return end
  running = true
  while speed.userTime() <= speed.stopTime do
    local t = timers:pop()
    if not t then break end
    local offs = t.time - _time()
    setTimeOffset(offs)
    --print(os.date("%Y-%m-%d %H:%M:%S",speed.userTime())," Timer:",t.id)
    t.fun()
  end
end
  
function fibaro.speedTime(speedTime,fun)
  speed.stopTime = os.time() + speedTime*3600
  setTimeout = speed.setTimeout
  clearTimeout = speed.clearTimeout
  setInterval = speed.setInterval
  clearInterval = speed.clearInterval
  os.time = speed.userTime
  os.date = speed.userDate
  setTimeout(fun,0)
  speed.loop()
end