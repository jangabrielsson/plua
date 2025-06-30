--%%name:EmbeddedDevicePropertiesTest
--%%type:com.fibaro.binarySwitch
--%% offline:true

function QuickApp:onInit()
  self:debug("Testing embedded API server device properties endpoint...")

  -- Test the new endpoint using the api object
  local result1 = api.get("/devices/555/properties/state")
  self:debug("api.get /devices/555/properties/state:")
  self:debug("  Type:", type(result1))
  self:debug("  Result:", result1)
  
  -- Test with a different property
  local result2 = api.get("/devices/555/properties/name")
  self:debug("api.get /devices/555/properties/name:")
  self:debug("  Type:", type(result2))
  self:debug("  Result:", result2)
  
  self:debug("Embedded API server device properties endpoint test completed!")
end 