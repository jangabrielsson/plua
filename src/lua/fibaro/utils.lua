local Emu = ...
local fmt = string.format

function urlencode(str) -- very useful
  if str then
    str = str:gsub("\n", "\r\n")
    str = str:gsub("([^%w %-%_%.%~])", function(c)
      return ("%%%02X"):format(string.byte(c))
    end)
    str = str:gsub(" ", "%%20")
  end
  return str
end

function table.copy(obj)
  if type(obj) == 'table' then 
    local res = {} for k,v in pairs(obj) do res[k] = table.copy(v) end
    return res
  else return obj end
end

local function equal(e1,e2)
  if e1==e2 then return true
  else
    if type(e1) ~= 'table' or type(e2) ~= 'table' then return false
    else
      for k1,v1 in pairs(e1) do if e2[k1] == nil or not equal(v1,e2[k1]) then return false end end
      for k2,_  in pairs(e2) do if e1[k2] == nil then return false end end
      return true
    end
  end
end
table.equal = equal

local function merge(a, b)
  if type(a) == 'table' and type(b) == 'table' then
    for k,v in pairs(b) do if type(v)=='table' and type(a[k] or false)=='table' then merge(a[k],v) else a[k]=v end end
  end
  return a
end

function table.merge(a,b) return merge(table.copy(a),b) end

function table.member(key,tab)
  for i,elm in ipairs(tab) do if key==elm then return i end end
end

function string.starts(str, start) return str:sub(1,#start)==start end

function string.split(inputstr, sep)
  local t={}
  for str in string.gmatch(inputstr, "([^"..(sep or "%s").."]+)") do t[#t+1] = str end
  return t
end

if not table.maxn then
  function table.maxn(t) local c=0 for _ in pairs(t) do c=c+1 end return c end
end

getmetatable("").__idiv = function(str,len) return (#str < len or #str < 4) and str or str:sub(1,len-2)..".." end -- truncate strings

local function readFile(fname,silent)
  local f = io.open(fname, "r")
  if not f and silent then return end
  assert(f, "Cannot open file: " .. fname)
  local code = f:read("*a")
  f:close()
  return code
end

local function writeFile(filename, content)
  local file = io.open(filename, "w")
  if file then
    file:write(content)
    file:close()
    return true
  else
    Emu:ERROR(fmt("Error writing to file %s", filename))
    return false
  end
end

local function prettyCall(fun,errPrint)
  xpcall(fun,function(err)
    local info = debug.getinfo(3)
    if info.what == "C" then
      info = debug.getinfo(2)
    end
    local msg = (type(err) == "string" and err:match("^.-](:%d+:.*)$")) or tostring(err)
    local source = info.source:match("^.+/(.+)$") or info.short_src
    if Emu.traceback then
      msg = msg .. "\n" .. debug.traceback()
    end
    (errPrint or print)(source..":"..msg)
    return false
  end)
  return true
end

local typeColor = {
  DEBUG = "light_green",
  TRACE = "plum2",
  WARNING = "darkorange",
  ERROR = "light_red",
  INFO = "light_blue",
}

-- Adds a debug message to the emulator's debug output.
-- @param tag - The tag for the debug message.
-- @param msg - The message string.
-- @param typ - The type of message (e.g., "DEBUG", "ERROR").
local function __fibaro_add_debug_message(tag, msg, typ, nohtml)
  tag = tag or "PLUA"
  Emu.lib.log.debugOutput(tag, msg, typ)
end

local logStr = function(...) 
  local b = {} 
  for _,e in ipairs({...}) do 
    b[#b+1]=tostring(e) 
  end 
  return table.concat(b," ")
end

------------------- sunCalc -------------------
local sunCalc
do
  ---@return number
  local function sunturnTime(date, rising, latitude, longitude, zenith, local_offset)
    local rad,deg,floor = math.rad,math.deg,math.floor
    local frac = function(n) return n - floor(n) end
    local cos = function(d) return math.cos(rad(d)) end
    local acos = function(d) return deg(math.acos(d)) end
    local sin = function(d) return math.sin(rad(d)) end
    local asin = function(d) return deg(math.asin(d)) end
    local tan = function(d) return math.tan(rad(d)) end
    local atan = function(d) return deg(math.atan(d)) end
    
    local function day_of_year(date2)
      local n1 = floor(275 * date2.month / 9)
      local n2 = floor((date2.month + 9) / 12)
      local n3 = (1 + floor((date2.year - 4 * floor(date2.year / 4) + 2) / 3))
      return n1 - (n2 * n3) + date2.day - 30
    end
    
    local function fit_into_range(val, min, max)
      local range,count = max - min,nil
      if val < min then count = floor((min - val) / range) + 1; return val + count * range
      elseif val >= max then count = floor((val - max) / range) + 1; return val - count * range
      else return val end
    end
    
    -- Convert the longitude to hour value and calculate an approximate time
    local n,lng_hour,t =  day_of_year(date), longitude / 15,nil
    if rising then t = n + ((6 - lng_hour) / 24) -- Rising time is desired
    else t = n + ((18 - lng_hour) / 24) end -- Setting time is desired
    local M = (0.9856 * t) - 3.289 -- Calculate the Sun^s mean anomaly
    -- Calculate the Sun^s true longitude
    local L = fit_into_range(M + (1.916 * sin(M)) + (0.020 * sin(2 * M)) + 282.634, 0, 360)
    -- Calculate the Sun^s right ascension
    local RA = fit_into_range(atan(0.91764 * tan(L)), 0, 360)
    -- Right ascension value needs to be in the same quadrant as L
    local Lquadrant = floor(L / 90) * 90
    local RAquadrant = floor(RA / 90) * 90
    RA = RA + Lquadrant - RAquadrant; RA = RA / 15 -- Right ascension value needs to be converted into hours
    local sinDec = 0.39782 * sin(L) -- Calculate the Sun's declination
    local cosDec = cos(asin(sinDec))
    local cosH = (cos(zenith) - (sinDec * sin(latitude))) / (cosDec * cos(latitude)) -- Calculate the Sun^s local hour angle
    if rising and cosH > 1 then return -1 --"N/R" -- The sun never rises on this location on the specified date
    elseif cosH < -1 then return -1 end --"N/S" end -- The sun never sets on this location on the specified date
    
    local H -- Finish calculating H and convert into hours
    if rising then H = 360 - acos(cosH)
    else H = acos(cosH) end
    H = H / 15
    local T = H + RA - (0.06571 * t) - 6.622 -- Calculate local mean time of rising/setting
    local UT = fit_into_range(T - lng_hour, 0, 24) -- Adjust back to UTC
    local LT = UT + local_offset -- Convert UT value to local time zone of latitude/longitude
    ---@diagnostic disable-next-line: missing-fields
    return os.time({day = date.day,month = date.month,year = date.year,hour = floor(LT),min = math.modf(frac(LT) * 60)})
  end
  
  ---@diagnostic disable-next-line: param-type-mismatch
  local function getTimezone(now) return os.difftime(now, os.time(os.date("!*t", now))) end
  
  function sunCalc(time,latitude,longitude)
    local loc = Emu.api.get("/settings/location")
    local lat = latitude or loc.latitude or 0
    local lon = longitude or loc.longitude or 0
    time = time or Emu.lib.userTime()
    local utc = getTimezone(time) / 3600
    local zenith,zenith_twilight = 90.83, 96.0 -- sunset/sunrise 90°50′, civil twilight 96°0′
    
    local date = os.date("*t",time or os.time())
    if date.isdst then utc = utc + 1 end
    local rise_time = os.date("*t", sunturnTime(date, true, lat, lon, zenith, utc))
    local set_time = os.date("*t", sunturnTime(date, false, lat, lon, zenith, utc))
    local rise_time_t,set_time_t = rise_time,set_time
    pcall(function() rise_time_t = os.date("*t", sunturnTime(date, true, lat, lon, zenith_twilight, utc)) end)
    pcall(function() set_time_t = os.date("*t", sunturnTime(date, false, lat, lon, zenith_twilight, utc)) end)
    local sunrise,sunset,sunrise_t,sunset_t = "00:00","00:00","00:00","00:00"
    pcall(function() sunrise = fmt("%.2d:%.2d", rise_time.hour, rise_time.min) end)
    pcall(function() sunset = fmt("%.2d:%.2d", set_time.hour, set_time.min) end)
    pcall(function() sunrise_t = fmt("%.2d:%.2d", rise_time_t.hour, rise_time_t.min) end)
    pcall(function() sunset_t = fmt("%.2d:%.2d", set_time_t.hour, set_time_t.min) end)
    return sunrise, sunset, sunrise_t, sunset_t
  end
end 

local function parseTime(str)
  local D,h = str:match("^(.*) ([%d:]*)$")
  if D == nil and str:match("^[%d/]+$") then D,h = str,os.date("%H:%M:%S")
  elseif D == nil and str:match("^[%d:]+$") then D,h = os.date("%Y/%m/%d"),str
  elseif D == nil then error("Bad time value: "..str) end
  local y,m,d = D:match("(%d+)/(%d+)/?(%d*)")
  if d == "" then y,m,d = os.date("%Y"),y,m end
  local H,M,S = h:match("(%d+):(%d+):?(%d*)")
  if S == "" then H,M,S = H,M,0 end
  assert(y and m and d and H and M and S,"Bad time value: "..str)
  return os.time({year=y,month=m,day=d,hour=H,min=M,sec=S})
end

---------------------------
Emu.lib.readFile = readFile
Emu.lib.writeFile = writeFile
Emu.lib.sunCalc = sunCalc
Emu.lib.logStr = logStr
Emu.lib.__fibaro_add_debug_message = __fibaro_add_debug_message
Emu.lib.prettyCall = prettyCall
Emu.lib.parseTime = parseTime