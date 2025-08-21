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
  local pr = buffPrint("\n")
  pr:printf("%-30s %-8s %-8s", "Name", "Type", "Value")
  pr:printf("%s",("-"):rep(128))
  for _, var in ipairs(vars) do
    pr:printf("%-30s %-9s %-9s", var.name, var.isEnum and "Enum" or "Var", var.value:sub(1,128))
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
    assert(type(rsrc) == "string", "Resource name must be a string")
    for k,v in pairs(listFuns) do
      if k:match("^" .. rsrc) then
        v()
      end
    end
  end
}