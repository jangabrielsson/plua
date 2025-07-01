Emu=Emu
local fileNum = 0
local function createTempName(suffix)
  fileNum = fileNum + 1
  return os.date("hc3emu%M%M")..fileNum..suffix
end

local function printBuff()
  local self,buff = {},{}
  function self:printf(...) buff[#buff+1] = string.format(...) end
  function self:print(str) buff[#buff+1] = str end
  function self:tostring() return table.concat(buff,"\n") end
  return self
end

local function remove(t,e)
  for i,v in ipairs(t) do if v == e then table.remove(t,i) break end end
  return t
end

local function findFirstLine(src)
  local n,first,init = 0,nil,nil
  for line in string.gmatch(src,"([^\r\n]*\r?\n?)") do
    n = n+1
    line = line:match("^%s*(.*)")
    if not (line=="" or line:match("^[%-]+")) then 
      if not first then first = n end
    end
    if line:match("%s*QuickApp%s*:%s*onInit%s*%(") then
      if not init then init = n end
    end
  end
  return first or 1,init
end

local function loadQAString(src,optionalDirectives) -- Load QA from string and run it
  local path = Emu.config.tempDir..createTempName(".lua")
  local f = io.open(path,"w")
  assert(f,"Can't open file "..path)
  f:write(src)
  f:close()
  ---@diagnostic disable-next-line: need-check-nil
  return Emu:installQuickAppFile(path)
end


local function markArray(t) if type(t)=='table' then json.initArray(t) end end
local function arrayifyFqa(fqa)
  markArray(fqa.initialInterfaces)
  markArray(fqa.initialProperties.quickAppVariables)
  markArray(fqa.initialProperties.uiView)
  markArray(fqa.initialProperties.uiCallbacks)
  markArray(fqa.initialProperties.supportedDeviceRoles)
end

local function uploadFQA(fqa)
  assert(type(fqa) == "table", "fqa must be a table")
  assert(fqa.name, "fqa must have a name")
  assert(fqa.type, "fqa must have a type")
  assert(fqa.files, "fqa must have files")
  assert(fqa.files[1], "fqa must have file(s)")
  local haveMain = false
  for _,f in ipairs(fqa.files) do
    if f.isMain then haveMain = true break end
  end
  assert(haveMain, "fqa must have a main file")
  arrayifyFqa(fqa)
  local res,code = Emu.api.hc3.post("/quickApp/",fqa)
  if not code or code > 201 then
    Emu:ERRORF("Failed to upload FQA: %s", res)
  else
    Emu:DEBUG("Successfully uploaded FQA with ID: %s", res.id)
  end
  return res,code
end

local function getFQA(id) -- Creates FQA structure from installed QA
  local dev = Emu.devices[id]
  assert(dev,"QuickApp not found, ID"..tostring(id))
  local struct = dev.device
  local files = {}
  for _,f in ipairs(dev.files) do
    if f.content == nil then f.content = Emu.lib.readFile(f.fname) end
    files[#files+1] = {name=f.name, isMain=f.name=='main', isOpen=false, type='lua', content=f.content}
  end
  local initProps = {}
  local savedProps = {
    "uiCallbacks","quickAppVariables","uiView","viewLayout","apiVersion","useEmbededView",
    "manufacturer","useUiView","model","buildNumber","supportedDeviceRoles", 
    "userDescription","typeTemplateInitialized","quickAppUuid","deviceRole"
  }
  for _,k in ipairs(savedProps) do initProps[k]=struct.properties[k] end
  return {
    apiVersion = "1.3",
    name = struct.name,
    type = struct.type,
    initialProperties = initProps,
    initialInterfaces = struct.interfaces,
    files = files
  }
end

local function saveQA(id,fileName) -- Save installed QA to disk as .fqa  //Move to QA class
  local dev = Emu.devices[id]        
  fileName = fileName or dev.headers.save
  assert(fileName,"No save filename found")
  local fqa = getFQA(id)
  arrayifyFqa(fqa)
  local vars = table.copy(fqa.initialProperties.quickAppVariables or {})
  markArray(vars) -- copied
  fqa.initialProperties.quickAppVariables = vars
  local conceal = dev.headers.conceal or {}
  for _,v in ipairs(vars) do
    if conceal[v.name] then 
      v.value = conceal[v.name]
    end
  end
  local f = io.open(fileName,"w")
  assert(f,"Can't open file "..fileName)
  f:write(json.encode(fqa))
  f:close()
  Emu:DEBUG("Saved QuickApp to %s",fileName)
end

local function loadQA(path,optionalHeaders,noRun)   -- Load QA from file and maybe run it
  optionalHeaders = optionalHeaders or {}
  optionalHeaders.norun = tostring(noRun==true) -- If noRun is true, don't run the QuickApp
  local struct = Emu:installQuickAppFile(path,optionalHeaders)
  return struct
end

local saveProject
local function unpackFQAAux(id,fqa,path) -- Unpack fqa and save it to disk
  local sep = Emu.config.fileSeparator
  assert(type(path) == "string", "path must be a string")
  local fname = ""
  fqa = fqa or Emu.api.hc3.get("/quickApp/export/"..id) 
  assert(fqa, "Failed to download fqa")
  local name = fqa.name
  local typ = fqa.type
  local files = fqa.files
  local props = fqa.initialProperties or {}
  local ifs = fqa.initialInterfaces or {}
  ifs = remove(ifs,"quickApp")
  if next(ifs) == nil then ifs = nil end
  
  if path:sub(-4):lower() == ".lua" then
    fname = path:match("([^/\\]+)%.[Ll][uU][Aa]$")
    path = path:sub(1,-(#fname+4+1))
  else
    if path:sub(-1) ~= sep then path = path..sep end
    fname = name:gsub("[%s%-%.%%!%?%(%)]","_")
    if id then if fname:match("_$") then fname = fname..id else fname = fname.."_"..id end end
  end
  
  local mainIndex
  for i,f in ipairs(files) do if files[i].isMain then mainIndex = i break end end
  assert(mainIndex,"No main file found")
  local mainContent = files[mainIndex].content
  table.remove(files,mainIndex)
  
  mainContent = mainContent:gsub("(%-%-%%%%.-\n)","") -- Remove old directives
  
  local pr = printBuff()
  pr:printf('if require and not QuickApp then require("hc3emu") end')
  pr:printf('--%%%%name=%s',name)
  pr:printf('--%%%%type=%s',typ)
  if ifs then pr:printf('--%%%%interfaces=%s',json.encode(ifs):gsub('.',{['[']='{', [']']='}'})) end
  
  local qvars = props.quickAppVariables or {}
  for _,v in ipairs(qvars) do
    pr:printf('--%%%%var=%s:%s',v.name,type(v.value)=='string' and '"'..v.value..'"' or v.value)
  end
  pr:printf('--%%%%project=%s',id)
  if props.quickAppUuid then pr:printf('--%%%%uid=%s',props.quickAppUuid) end
  if props.model then pr:printf('--%%%%model=%s',props.model) end
  if props.manufacturer then pr:printf('--%%%%manufacturer=%s',props.manufacturer) end
  if props.deviceRole then pr:printf('--%%%%role=%s',props.deviceRole) end
  if props.userDescription then pr:printf('--%%%%description=%s',props.userDescription) end
  
  local savedFiles = {}
  for _,f in ipairs(files) do
    local fn = path..fname.."_"..f.name..".lua"
    Emu.lib.writeFile(fn,f.content)
    pr:printf("--%%%%file=%s:%s",fn,f.name)
    savedFiles[#savedFiles+1] = {name=f.name, fname=fn}
  end
  
  local UI = ""
  if id then
    Emu.lib.ui.logUI(id,function(str) UI = str end)
  else
    local UIstruct = Emu.lib.ui.viewLayout2UI(props.viewLayout or {},props.uiCallbacks or {})
    Emu.lib.ui.dumpUI(UIstruct,function(str) UI = str end)
  end
  UI = UI:match(".-\n(.*)") or ""
  pr:print(UI)
  
  pr:print("")
  pr:print(mainContent)
  local mainFilePath = path..fname..".lua"
  Emu.lib.writeFile(mainFilePath,pr:tostring())
  savedFiles[#savedFiles+1] = {name='main', fname=mainFilePath}
  saveProject(id,{files=savedFiles},path) -- Save project file
  return mainFilePath
end

--@F 
local function downloadFQA(id,path) -- Download QA from HC3,unpack and save it to disk
  assert(type(id) == "number", "id must be a number")
  assert(type(path) == "string", "path must be a string")
  return unpackFQAAux(id,nil,path)
end

function saveProject(id,dev,path)  -- Save project to .project file
  path = path or ""
  local r = {}
  for _,f in ipairs(dev.files) do
    r[f.name] = f.fname
  end
  local f = io.open(path..".project","w")
  assert(f,"Can't open file "..path..".project")
  f:write(json.encodeFormated({files=r,id=id}))
  f:close()
end

return {
  createTempName = createTempName,
  findFirstLine = findFirstLine,
  loadQAString = loadQAString,
  uploadFQA = uploadFQA,
  getFQA = getFQA,
  saveQA = saveQA,
  loadQA = loadQA,
  downloadFQA = downloadFQA,
  saveProject = saveProject,
}