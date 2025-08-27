local Emu = ...

local fmt = string.format 

local fileNum = 0
local function createTempName(suffix)
  fileNum = fileNum + 1
  return os.date("plua%M%M")..fileNum..suffix
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

local lfs = require("lfs")
local function loadQAString(src,options) -- Load QA from string and run it
  local path = Emu.config.tempdir..createTempName(".lua")
  lfs.mkdir(Emu.config.tempdir)
  local f = io.open(path,"w")
  assert(f,"Can't open file "..path)
  f:write(src)
  f:close()
  ---@diagnostic disable-next-line: need-check-nil
  return Emu:installQuickAppFile(path, options or {})
end


local function markArray(t) if type(t)=='table' then json.initArray(t) end end
local function arrayifyFqa(fqa)
  markArray(fqa.initialInterfaces)
  markArray(fqa.initialProperties.quickAppVariables)
  markArray(fqa.initialProperties.uiView)
  markArray(fqa.initialProperties.uiCallbacks)
  markArray(fqa.initialProperties.supportedDeviceRoles)
  return fqa
end

-- Screen dimension and QuickApp window functions
local function getScreenDimension()
  local dims = _PY.get_screen_dimensions()
  if dims then
    return dims.width, dims.height
  else
    return 1920, 1080  -- Fallback
  end
end

local function createQuickAppWindow(qaId, title, width, height, x, y, backgroundColor)
  title = title or fmt("QuickApp %s", qaId)
  width = width or 800
  height = height or 600
  x = x or 100
  y = y or 100
  backgroundColor = backgroundColor or ""
  
  local success = _PY.open_quickapp_window(qaId, title, width, height, x, y, backgroundColor)
  if success then
    Emu:DEBUG(fmt("Created QuickApp window for QA %s: %s (%dx%d at %d,%d)", qaId, title, width, height, x, y))
    if backgroundColor ~= "" then
      Emu:DEBUG(fmt("Applied background color: %s", backgroundColor))
    end
  else
    Emu:WARNING(fmt("Failed to create QuickApp window for QA %s", qaId))
  end
  return success
end

local function setQuickAppWindowBackground(qaId, color)
  -- For existing windows, we can't change the background color after creation
  -- This function is kept for compatibility but will return false for existing windows
  Emu:WARNING(fmt("Cannot change background color for existing QuickApp window %s. Use createQuickAppWindow with backgroundColor parameter instead.", qaId))
  return false
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
  --fqa.files = {}
  local encodedFQA = json.encodeFast(fqa)
  --print("Uploading FQA:",encodedFQA)
  local res,code = Emu.api.hc3.post("/quickApp/",encodedFQA)
  if not code or code > 201 then
    Emu:ERROR("Failed to upload FQA: "..tostring(code))
  else
    Emu:INFO("Successfully uploaded FQA with ID: "..(res.id or "unknown"))
  end
  return res,code
end

local function info2FQA(info)
  local struct = info.device
  local files = {}
  for name,f in pairs(info.files) do
    if f.content == nil then f.content = Emu.lib.readFile(f.path) end
    files[#files+1] = {name=name, isMain=name=='main', isOpen=false, type='lua', content=f.content}
  end
  local ncbs = {}
  for i,cb in ipairs(struct.properties.uiCallbacks or {}) do
    if cb.name:sub(1,2) ~= "__" then ncbs[#ncbs+1] = cb end
  end
  struct.properties.uiCallbacks = ncbs
  local initProps = {}
  local savedProps = {
    "uiCallbacks","quickAppVariables","uiView","viewLayout","apiVersion","useEmbededView",
    "manufacturer","useUiView","model","buildNumber","supportedDeviceRoles", 
    "userDescription","typeTemplateInitialized","quickAppUuid","deviceRole"
  }
  for _,k in ipairs(savedProps) do initProps[k]=struct.properties[k] end
  local struct = {
    apiVersion = "1.3",
    name = struct.name,
    type = struct.type,
    initialProperties = initProps,
    initialInterfaces = struct.interfaces,
    files = files
  }
  return arrayifyFqa(struct)
end

local function getFQA(id) -- Creates FQA structure from installed QA
  local dev = Emu.DIR[id]
  assert(dev,"QuickApp not found, ID"..tostring(id))
  return info2FQA(dev)
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

local function loadQA(path,options)   -- Load QA from file and maybe run it
  options = options or {} 
  options.headers = options.headers or {}
  table.insert(options.headers,"norun:"..tostring(options.noRun==true)) -- If noRun is true, don't run the QuickApp
  local struct = Emu:installQuickAppFile(path,options)
  return struct
end

local saveProject
local function unpackFQAAux(id,fqa,path) -- Unpack fqa and save it to disk
  local sep = "/"
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
  pr:printf('--%%%%name:%s',name)
  pr:printf('--%%%%type:%s',typ)
  if ifs then pr:printf('--%%%%interfaces:%s',json.encode(ifs):gsub('.',{['[']='{', [']']='}'})) end
  
  local qvars = props.quickAppVariables or {}
  for _,v in ipairs(qvars) do
    pr:printf('--%%%%var:%s=%s',v.name,type(v.value)=='string' and '"'..v.value:gsub('"','\\"')..'"' or v.value)
  end
  if id then pr:printf('--%%%%project:%s',id) end
  if props.quickAppUuid then pr:printf('--%%%%uid:%s',props.quickAppUuid) end
  if props.model then pr:printf('--%%%%model:%s',props.model) end
  if props.manufacturer then pr:printf('--%%%%manufacturer:%s',props.manufacturer) end
  if props.deviceRole then pr:printf('--%%%%role:%s',props.deviceRole) end
  if props.userDescription and props.userDescription ~= "" then 
    pr:printf('--%%%%description:%s',props.userDescription)
  end
  
  local savedFiles = {}
  for _,f in ipairs(files) do
    local fn = path..fname.."_"..f.name..".lua"
    Emu.lib.writeFile(fn,f.content)
    pr:printf("--%%%%file:%s,%s",fn,f.name)
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
  if UI ~= "" then pr:print(UI) end
  
  pr:print("")
  if mainContent ~= "" then pr:print(mainContent) end
  local mainFilePath = path..fname..".lua"
  local content = pr:tostring()
  --print(content)
  Emu.lib.writeFile(mainFilePath,content)
  savedFiles[#savedFiles+1] = {name='main', fname=mainFilePath}
  if id then saveProject(id,{files=savedFiles},path) end -- Save project file
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
  for name,f in pairs(dev.files) do
    r[name] = f.path
  end
  local f = io.open(path..".project","w")
  assert(f,"Can't open file "..path..".project")
  f:write(json.encodeFormated({files=r,id=id}))
  f:close()
end


local function findIdAndName(fname)
  local function find(path)
    local f = io.open(path,"r")
    if not f then return false,nil end
    local p = f:read("*a")
    f:close()
    local _,data = pcall(json.decode,p)
    data = data or {}
    for qn,fn in pairs(data.files or {}) do
      if fn==fname then
        return true,data.id, qn, data
      end
    end
  end
  local path,file = fname:match("^(.-)([^/\\]+)$")
  if not path then path = "" end
  local p1 = path..".project"
  local p2 = ".project"
  local _,id,name,data = find(p1)
  if id then return true,id,name,data end
  return find(p2)
end

local function updateQAparts(id,parts,silent)
  local qa = Emu.api.hc3.get("/devices/"..id)
  if not qa then
    return Emu:ERROR(fmt("QuickApp on HC3 with ID %s not found %s", tostring(id)))
  end
  
  if parts.files then
    local oldFiles = Emu.api.hc3.get("/quickApp/"..id.."/files") or {}
    local oldMap,existingFiles,newFiles = {},{},{}
    for _,f in ipairs(oldFiles) do oldMap[f.name] = f end
    for n,_ in pairs(parts.files) do
      local flag = oldMap[n]
      oldMap[n]=nil
      if flag then existingFiles[n] = true else newFiles[n] = true end
    end
    
    -- Delete files no longer part of QA
    for name,_ in pairs(oldMap) do
      local r,err = Emu.api.hc3.delete("/quickApp/"..id.."/files/"..name)
      if err > 206 then
        return Emu:ERROR(fmt("Failed to delete file %s from QuickApp %s: %s", name, id, err))
      else
        Emu:INFO(fmt("Deleted file %s from QuickApp %s", name, id))
      end
    end
    
    -- Create new files
    for name,_ in pairs(newFiles) do
      local path = parts.files[name]
      local f = {name=name, isMain=false, isOpen=false, type='lua', content=Emu.lib.readFile(path)}
      local r,err = Emu.api.hc3.post("/quickApp/"..id.."/files",f)
      if err > 206 then
        return Emu:ERROR(fmt("Failed to create file %s in QuickApp %s: %s", name, id, err))
      else
        Emu:INFO(fmt("Created file %s in QuickApp %s", name, id))
      end
    end
    
    -- Update existing files
    local ufiles = {}
    for name,_ in pairs(existingFiles) do
      local path = parts.files[name]
      local ef = Emu.api.hc3.get("/quickApp/"..id.."/files/"..name)
      local content = Emu.lib.readFile(path)
      if content == ef.content then
        Emu:INFO(fmt("Untouched file %s:%s in QuickApp %s", name, path, id))
      else
        local f = {name=name, isMain=name=='main', isOpen=false, type='lua', content=content}
        ufiles[#ufiles+1] = f
      end
    end
    if ufiles[1] then
      local r,err = Emu.api.hc3.put("/quickApp/"..id.."/files",ufiles)
      if err > 206 then
        return Emu:ERROR(fmt("Failed to update files for QuickApp %s: %s", id, err))
      else
        for name,_ in pairs(existingFiles) do
          Emu:INFO(fmt("Updated file %s:%s in QuickApp %s", name, parts.files[name], id))
        end
      end
    end
    
  end
  
  local function update(prop,value)
    return Emu.api.hc3.post("/plugins/updateProperty",{
      deviceId = id,
      propertyName = prop,
      value = value
    })
  end
  
  -- Update UI...
  if parts.viewLayout then
    local res,err = Emu.api.hc3.put("/devices/"..id,{
      properties = {
        viewLayout = parts.viewLayout,
        uiCallbacks = parts.uiCallbacks
      }
    })
    if err > 206 then return Emu:ERROR(fmt("Failed to update QuickApp viewLayout for %s: %s", id, err)) end
    -- r, err = update("uiView", fqa.initialProperties.uiView)
    -- if err > 206 then ERROR("Failed to update QuickApp uiView for %s: %s", id, err) end
    -- r, err = update("uiCallbacks", fqa.initialProperties.uiCallbacks)
    -- if err > 206 then ERROR("Failed to update QuickApp uiCallbacks for %s: %s", id, err) end
  end
  
  if parts.UI then
    local uiCallbacks,viewLayout,uiView,UImap = Emu:createUI(parts.UI or {})
    local res,err = Emu.api.hc3.put("/devices/"..id,{
      properties = {
        viewLayout = viewLayout,
        uiCallbacks = uiCallbacks
      }
    })
    if err > 206 then return Emu:ERROR(fmt("Failed to update QuickApp viewLayout for %s: %s", id, err)) end
  end

  -- Update other properties
  if parts.props then
    local updateProps = {
      "quickAppVariables","manufacturer","model","buildNumber",
      "userDescription","quickAppUuid","deviceRole"
    }
    for _,prop in ipairs(updateProps) do 
      local value = parts.props[prop]
      if value ~= nil and value ~= "" and value ~= qa.properties[prop] then 
        update(prop, value) 
        if prop == "quickAppVariables" then
          value = json.encode(value)
          if #value > 40 then 
            value = value:sub(1, 40) .. "..."
          end
        end
        if not silent then Emu:INFO(fmt("Updated property %s to '%s' for QuickApp %s", prop, value, id)) end
      end
    end
    
  end
  
  if parts.interfaces then
    local function trueMap(arr) local r={} for _,v in ipairs(arr) do r[v]=true end return r end
    -- Update interfaces
    local interfaces = parts.interfaces or {}
    local oldInterfaces = qa.interfaces or {}
    local newMap,oldMap = trueMap(interfaces),trueMap(oldInterfaces)
    if not newMap.quickApp then newMap.quickApp = true end
    local newIfs,oldIfs = {},{}
    for i,_ in pairs(newMap) do if not oldMap[i] then newIfs[#newIfs+1] = i end end
    for i,_ in pairs(oldMap) do if not newMap[i] then oldIfs[#oldIfs+1] = i end end
    if #newIfs > 0 then 
      local res,code = Emu.api.hc3.restricted.post("/plugins/interfaces", {action = 'add', deviceId = id, interfaces = newIfs})  -- TODO
      if code > 206 then
        return Emu:ERROR(fmt("Failed to add interfaces to QuickApp %s: %s", id, code))
      else
        if not silent then Emu:INFO(fmt("Added interfaces to QuickApp %s: %s", id, table.concat(newIfs, ", "))) end
      end
    end
    if #oldIfs > 0 then 
      local res,code = Emu.api.hc3.restricted.post("/plugins/interfaces", {action = 'delete', deviceId = id, interfaces = oldIfs}) -- TODO
      if code > 206 then
        return Emu:ERROR(fmt("Failed to delete interfaces from QuickApp %s: %s", id, code))
      else
        if not silent then Emu:INFO(fmt("Deleted interfaces from QuickApp %s: %s", id, table.concat(oldIfs, ", "))) end
      end
    end
  end

  if not silent then Emu:INFO("Done") end
end

local function updateQA(fname)
  Emu:INFO(fmt("Updating QA: %s",tostring(fname))) -- fname
  local exist,id,qn,data = findIdAndName(fname)
  assert(exist,"No .project file found for " .. fname)
  assert(id,"No entry for "..fname.." in .project file")
  assert(data,"No .project found for "..fname)
  local qa = Emu.api.hc3.get("/devices/"..id)
  if not qa then
    return Emu:ERROR(fmt("QuickApp on HC3 with ID %s not found %s", tostring(id)))
  end
  local info = Emu:createInfoFromFile(fname)
  Emu:registerDevice(info)
  local fqa = Emu.lib.getFQA(info.device.id)
  assert(fqa, "Emulator installation error")
  assert(qa.type == fqa.type, "QuickApp type mismatch: expected " .. fqa.type .. ", got " .. qa.type)
  updateQAparts(id,{
    files = fqa.files, 
    interfaces = fqa.initialInterfaces, 
    quickVars = fqa.initialProperties.quickAppVariables,
    props = fqa.initialProperties,
    viewLayout = fqa.initialProperties.viewLayout,
    uiCallbacks = fqa.initialProperties.uiCallbacks
  })
end

local function updateFile(fname)
  Emu:INFO("Updating file",fname)
  local exist,id,qn = findIdAndName(fname)
  assert(exist,"No .project file found for " .. fname)
  assert(id,"No entry for "..fname.." in .project file")
  local qa = Emu.api.hc3.get("/devices/"..id)
  if not qa then
    return Emu:ERROR("QuickApp on HC3 with ID %s not found "..tostring(id))
  end
  local content = Emu.lib.readFile(fname)
  local f = {name=qn, isMain=qn=='main', isOpen=false, type='lua', content=content}
  local r,err = Emu.api.hc3.put("/quickApp/"..id.."/files/"..qn,f)
  if not r then 
    local r,err = Emu.api.hc3.post("/quickApp/"..id.."/files",f)
    if err then
      Emu:ERROR(fmt("creating QA:%s, file:%s, QAfile%s",id,fname,qn))
    else
      Emu:INFO(fmt("Created QA:%s, file:%s, QAfile%s",id,fname,qn))
    end
  else 
    Emu:INFO(fmt("Updated QA:%s, file%s, QAfile:%s ",id,fname,qn))
  end
end

local function luaToFQA(code)
    local info = Emu:createInfoFromContent("",code)
    return info2FQA(info)
end

Emu.lib.createTempName = createTempName
Emu.lib.findFirstLine = findFirstLine
Emu.lib.loadQAString = loadQAString
Emu.lib.uploadFQA = uploadFQA
Emu.lib.getFQA = getFQA
Emu.lib.saveQA = saveQA
Emu.lib.loadQA = loadQA
Emu.lib.downloadFQA = downloadFQA
Emu.lib.unpackFQAAux = unpackFQAAux
Emu.lib.saveProject = saveProject
Emu.lib.updateQA = updateQA
Emu.lib.updateFile = updateFile
Emu.lib.getScreenDimension = getScreenDimension
Emu.lib.createQuickAppWindow = createQuickAppWindow
Emu.lib.setQuickAppWindowBackground = setQuickAppWindowBackground
Emu.lib.updateFile = updateFile
Emu.lib.updateQAparts = updateQAparts
Emu.lib.info2FQA = info2FQA
Emu.lib.luaToFQA = luaToFQA
Emu.lib.createTempName = createTempName