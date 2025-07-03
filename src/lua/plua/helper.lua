local copas = require("copas")

local helperStarted = false
local HELPER_UUID = "hc3emu-00-01"
local HELPER_VERSION = "1.0.2"

local helperRes = {}

local function installHelper()
  local fqa = Emu.config.loadResource("hc3emuHelper.fqa",true)
  if not fqa then
    Emu:ERRORF("Failed to load helper")
    return nil
  end
  fqa.visible = false
  fqa.initialProperties.quickAppUuid = HELPER_UUID
  fqa.initialProperties.model = HELPER_VERSION
  local helper,err = Emu.tools.uploadFQA(fqa)
  if not helper then
    Emu:ERRORF("Failed to install helper: %s",err or "Unknown error")
    return nil
  end
  Emu.api.hc3.put("/devices/"..helper.id,{visible=false}) -- Hide helper
  return helper
end

---@class RequestServer : SocketServer
RequestServer = {}
class 'RequestServer'(SocketServer)
function RequestServer:__init(ip,port,pi) 
  SocketServer.__init(self,ip,port,pi) 
  self.queue = copas.queue.new()
end

local function sendParts(str,write,n0)
  local len = #str
  local n = (len-1) // n0
  local i = 1
  local p = str:sub(i,i+n0-1)
  i = i+n0
  write(string.format("%03d:%s\n",n+1,p))
  while n > 0 do
    p = str:sub(i,i+n0-1)
    write(p)
    i = i+n0
    n = n-1
  end
end

local function receieveParts(read)
  local data = read()
  if data == nil then return end
  local n = tonumber(data:sub(1,3))
  if not n then print("Not n","x",data) return end
  data = data:sub(5)
  local buff = {data}
  for i=2,n do 
    local l = read()
    if not l then  print("Not l",i) break end
    buff[#buff+1] = l
  end
  return table.concat(buff):gsub("\n","")
end

function RequestServer:handler(io)
  while true do
    local req = self.queue:pop(math.huge)
    --print("SEND:",req.request)
    sendParts(req.request,io.write,500)
    --copas.send(skt,req.request)
    local reqdata = receieveParts(io.read)
    --print("REC:",reqdata)
    req.response = reqdata
    req.sem:destroy()
    if not reqdata then break end
  end
end
function RequestServer:send(msg)
  local req = {request=msg,response=nil,sem = copas.semaphore.new(1,0,math.huge)}
  self.queue:push(req)
  req.sem:take()
  return req.response
end

local connection = nil
local function startHelper()
  if helperStarted then return connection end
  local helpers = (Emu.api.hc3.get("/devices?property=[quickAppUuid,"..HELPER_UUID.."]") or {})
  local helper
  if #helpers > 1 then
    Emu:ERRORF("Multiple helper instances found, will remove all but latest")
    table.sort(helpers,function(a,b) return a.id < b.id end)
    for i=1,#helpers-1 do
      Emu.api.hc3.delete("/devices/"..helpers[i].id)
    end
  end
  helper = helpers[#helpers]
  if not helper or helper.properties.model ~= HELPER_VERSION then
    if helper then Emu.api.hc3.delete("/devices/"..helper.id) end -- Old, remove and install new helper
    helper = installHelper()
  end
  if not helper then
    return Emu:ERRORF("Failed to install helper")
  end
  local helperId = helper.id
  if helperId then
    Emu.api.hc3.post("/devices/"..helperId.."/action/close",{ args={Emu.config.pip2,Emu.config.hport}} )
    connection = RequestServer(Emu.config.hip,Emu.config.hport,Emu.PI)
    connection:start()
    Emu.api.hc3.post("/devices/"..helperId.."/action/connect",{args={Emu.config.pip2,Emu.config.hport}})
  end
  
  helperStarted = true

  Emu:process({
    pi = Emu.PI,
    fun=function()
    while true do
      local _ = connection and connection:send("Ping")
      copas.pause(10)
    end
  end})
end

return setmetatable({}, { -- Lazy access to helper, start when needed
  __index = function(t,k)
    if k == 'connection' then 
      if not helperStarted then startHelper() end
      if connection == nil then error("Failed to start helper",2) end
      return connection
    end
    return rawget(t,k)
  end,
})
