local fmt = string.format
local Emu

local function buffPrint(...)
  local b = {...}
  local self = { buff = {} }
  function self:printf(fmt, ...)
    local message = fmt:format(...)
    table.insert(b, message)
  end
  function self:toString()
    return table.concat(b, "\n")
  end
  return self
end

local YES = "✅"
local NO = "❌"
local RED = "🔴"
local GREEN = "⚪"
local RED = "🚨"

local function listQA()
  local qas = Emu.api.hc3.get("/devices?interface=quickApp")
  local pr = buffPrint("\n")
  pr:printf("%-5s %-30s %-30s %-8s %-8s %-8s", "ID", "Name", "Type", "Enabled","Visible","Modified")
  pr:printf("%s",("-"):rep(128))
  for _, qa in ipairs(qas) do
    pr:printf("%-5s %-30s %-30s %-9s %-9s %-8s", qa.id, qa.name, qa.type, qa.enabled and YES or NO, qa.visible and YES or NO, os.date("%Y-%m-%d %H:%M:%S",qa.modified))
  end
  
  print(pr:toString())
end

local function listScene()
  local scenes = Emu.api.hc3.get("/scenes")
  local pr = buffPrint("\n")
  pr:printf("%-5s %-30s %-8s %-8s %-8s", "ID", "Name", "Type","Enabled","Modified")
  pr:printf("%s",("-"):rep(128))
  for _, scene in ipairs(scenes) do
    pr:printf("%-5s %-30s %-9s %-9s %-8s", scene.id, scene.name, scene.type,scene.enabled and YES or NO, os.date("%Y-%m-%d %H:%M:%S",scene.updated))
  end
  print(pr:toString())
end

local function listGlobalVars()
  local vars = Emu.api.hc3.get("/globalVariables")
  table.sort(vars, function(a,b) return a.name < b.name end)
  local pr = buffPrint("\n")
  pr:printf("%-30s %-8s %-8s", "Name", "Type", "Value")
  pr:printf("%s",("-"):rep(128))
  for _, var in ipairs(vars) do
    pr:printf("%-30s %-9s %-9s", var.name, var.isEnum and "Enum" or "Var", var.value:sub(1,128))
  end
  print(pr:toString())
end

local function listAlarms()
  local alarms = Emu.api.hc3.get("/alarms/v1/partitions")
  local pr = buffPrint("\n")
  pr:printf("%-5s %-30s %-8s %-10s %-8s", "ID", "Name", "Armed", "Breached", "Modified")
  pr:printf("%s",("-"):rep(128))
  for _, alarm in ipairs(alarms) do
    pr:printf("%-5s %-30s %-9s %-9s %-8s", alarm.id, alarm.name, alarm.armed and RED or GREEN, alarm.breached and RED or GREEN, os.date("%Y-%m-%d %H:%M:%S", alarm.modified))
  end
  print(pr:toString())
end

local function listClimate()
  local climates = Emu.api.hc3.get("/panels/climate")
  local pr = buffPrint("\n")
  pr:printf("%-5s %-30s %-8s %-10s", "ID", "Name", "Active", "Mode")
  pr:printf("%s",("-"):rep(128))
  for _, clim in ipairs(climates) do
    pr:printf("%-5s %-30s %-9s %-9s", clim.id, clim.name, clim.active and YES or NO, clim.mode)
  end
  print(pr:toString())
end

local function listProfiles()
  local profiles = Emu.api.hc3.get("/profiles")
  local pr = buffPrint("\n")
  pr:printf("%-5s %-30s %-8s", "ID", "Name", "Active")
  pr:printf("%s",("-"):rep(128))
  for _, profile in ipairs(profiles.profiles) do
    pr:printf("%-5s %-30s %-9s", profile.id, profile.name, profile.id == profiles.activeProfile and YES or NO)
  end
  print(pr:toString())
end

local function listSprinklers()
  local sprinklers = Emu.api.hc3.get("/panels/sprinklers")
  local pr = buffPrint("\n")
  pr:printf("%-5s %-30s %-8s %-10s", "ID", "Name", "Active", "Days")
  pr:printf("%s",("-"):rep(128))
  for _, spr in ipairs(sprinklers) do
    pr:printf("%-5s %-30s %-9s %-9s", spr.id, spr.name, spr.isActive and YES or NO, json.encode(spr.days):sub(2,-2))
  end
  print(pr:toString())
end

local function listLocation()
  local location = Emu.api.hc3.get("/panels/location")
  local pr = buffPrint("\n")
  pr:printf("%-5s %-30s %-8s %-10s", "ID", "Name", "Home", "Address")
  pr:printf("%s",("-"):rep(128))
  for _, loc in ipairs(location) do
    pr:printf("%-5s %-30s %-9s %-9s", loc.id, loc.name, loc.home and YES or NO, loc.address)
  end
  print(pr:toString())
end

local listFuns = {
  qa = listQA,
  scene = listScene,
  gv = listGlobalVars,
  climate = listClimate,
  sprinkler = listSprinklers,
  profile = listProfiles,
  alarm = listAlarms,
  location = listLocation
}

return {
  sort = -1,
  doc = "List resources on HC3, qa, scene, gv, climate, sprinkler, profile, alarm, and location.",
  usage = ">plua -t list <rsrc name",
  fun = function(_Emu,rsrc)
    Emu = _Emu
    if rsrc == nil then
      print("Please provide a resource name to list, e.g., qa, scene, gv, climate, sprinkler, profile, alarm, or location.")
      return
    end
    assert(type(rsrc) == "string", "Resource name must be a string") 
    for k,v in pairs(listFuns) do
      if k:match("^" .. rsrc) then
        v()
      end
    end
  end
}