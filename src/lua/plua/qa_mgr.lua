local fmt = string.format
local preprocessQA
__TAG = "FIBARO"

local headers = {}
function headers.name(str,info) info.name = str end
function headers.type(str,info) info.type = str end
function headers.file(str,info)
  local path,name = str:match("^([^,]+),(.+)$")
  assert(path,"Invalid file header: "..str)
  if _PY.file_exists(path) then
    info.files[name] = path
  else
    error(fmt("File not found: '%s'",path))
  end
end

function preprocessQA(filename,content)
  local shortname = filename:match("([^/\\]+%.lua)")
  print("Preprocessing QA",shortname)
  local name = shortname:match("(.+)%.lua")
  local info = {name=name or "MyQA",type='com.fibaro.binarySwitch',files={}}
  local code = "\n"..content
  code:gsub("\n%-%-%%%%([%w_]-):([^\n]*)",function(key,str) 
    str = str:match("^%s*(.-)%s*$") or str
    str = str:match("^(.*)%s* %-%- (.*)$") or str
    if headers[key] then
      headers[key](str,info)
    else print(fmt("Unknown header key: '%s' - ignoring",key)) end 
  end)
  return content,info
end

local function printError(func)
  return function(filename)
    local ok,err = pcall(func,filename)
    if not ok then
      err = err:match("^.-qa_mgr%.lua:%d+:(.*)") or err
      local msg = err:match("^.-](:%d+:.*)$")
      if msg then err = filename..msg end
      fibaro.error(__TAG,err)
    end
  end
end

local function loadFile(path,name,content)
  if not content then
    local file = io.open(path, "r")
    assert(file, "Failed to open file: " .. path)
    content = file:read("*all")
    file:close()
  end
  local func, err = load(content, path)
  if func then func() return true
  else error(err) end
end

_PY.mainHook = function(filename)
  if not (filename and filename:match("%.lua$")) then return false end

  -- Read the file content
  local file = io.open(filename, "r")
  assert(file, "Failed to open file: " .. filename)
  local content = file:read("*all")
  file:close()
  
  -- Do preprocessing for Fibaro environment
  local preprocessed,info = preprocessQA(filename,content)
  
  info.id = info.id or 555
  info.type = info.type or 'com.fibaro.binarySwitch'
  __TAG = info.name..info.id or __TAG

  -- Load and execute included files + main file
  for name,path in pairs(info.files) do
    loadFile(path,name)
  end
  loadFile(filename,'main',preprocessed)

  setTimeout(function()
    -- print("Looking for QuickApp")
    if QuickApp and QuickApp.onInit then
      -- print("QuickApp detected. Creating QuickApp instance.")
      quickApp = QuickApp(info)
    end
  end, 0)
end

_PY.mainHook = printError(_PY.mainHook)