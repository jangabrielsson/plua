local function printf(fmt, ...) print(string.format(fmt, ...)) end

print("Diagnostic mode enabled. Running tests...")
local json = require('json')
require("fibaro")

local function checkIfNotNil(msg,val)
  if type(val)=='table' then val = json.encode(val) end
  if val == nil then 
    printf("⚠️  %-20s: %s", msg, "nil")
  else
    printf("✅ %-20s: %s", msg, tostring(val))
  end
end

printf("================ Std configs ===============")
local keys = {
  "hc3_url",
  "hc3_user",
  "hc3_password",
  "hc3_pin",
  "hc3_creds",
  "offline",
  "scripts",
  "api_host",
  "luaLibPath",
  "debugger",
  "tempdir",
  "environment",
  "cwd",
  "user",
  "homedir",
  "enginePath",
  "api_port",
  "platform",
  "python_version",
}
for _, key in ipairs(keys) do
  checkIfNotNil(key,fibaro.plua.config[key])
end

if fibaro.plua.config.hc3_creds then
  printf("================ HC3 info ===============")
  local hc3,code = fibaro.plua.api.get("/settings/info")
  if code == 200 then
    printf("✅ HC3 Serialnumber    : %s", hc3.serialNumber)
    printf("✅ HC3 Name.           : %s", hc3.hcName)
    printf("✅ HC3 Software version: %s", hc3.softVersion)
    local ep = fibaro.plua.api.get("/settings/network/enabledProtocols")
    printf("✅ HC3 Protocols.      : %s", json.encode(ep))
  else
    printf("❌ HC3 API Error: %s", code)
  end
end
