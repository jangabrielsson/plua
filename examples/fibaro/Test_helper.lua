--%%name:TestHelper
--%%debug:true
--%%proxy:true

-- Deletes existing helper and installs new helper

local HELPER_UUID = "plua-00-01"

function QuickApp:onInit()
  --setTimeout(function()
  self:debug("TestHelper:onInit")
  local helpers = (api.hc3.get("/devices?property=[quickAppUuid,"..HELPER_UUID.."]") or {})
  for _,helper in ipairs(helpers) do
    self:debug("Helper:",helper.name,helper.id)
    --api.hc3.delete("/devices/"..helper.id)
  end
  -- Test if we can call the restricted api
  local a,b = api.hc3.restricted.get("/devices?property=[quickAppUuid,"..HELPER_UUID.."]")
  self:debug("a,b",a,b)
  --end,100)

  self:internalStorageSet("LICEMAN_LAST_STATE","value42")
  local a,b = self:internalStorageGet("LICEMAN_LAST_STATE")
  self:debug("internalStorageGet",a,b)
end