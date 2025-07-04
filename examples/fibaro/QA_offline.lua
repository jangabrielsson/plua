--%%name:Offline
--%%type:com.fibaro.binarySwitch
--%%offline:true

function QuickApp:onInit()
  self:debug("Offline test - Testing all GET endpoints")
  
  -- Test all GET endpoints systematically
  self:testCoreEndpoints()
  self:testDeviceEndpoints()
  self:testGlobalVariablesEndpoints()
  self:testRoomsEndpoints()
  self:testSectionsEndpoints()
  self:testCustomEventsEndpoints()
  self:testRefreshStatesEndpoints()
  self:testIosDevicesEndpoints()
  self:testHomeEndpoints()
  self:testDebugMessagesEndpoints()
  self:testWeatherEndpoints()
  self:testPluginsEndpoints()
  self:testQuickAppEndpoints()
  self:testSettingsEndpoints()
  self:testAlarmEndpoints()
  self:testNotificationCenterEndpoints()
  self:testProfilesEndpoints()
  self:testIconsEndpoints()
  self:testUsersEndpoints()
  self:testEnergyDevicesEndpoints()
  self:testPanelsEndpoints()
  self:testDiagnosticsEndpoints()
  self:testProxyEndpoints()
  
  self:debug("All endpoint tests completed!")
end

-- Core endpoints
function QuickApp:testCoreEndpoints()
  self:debug("=== Testing Core Endpoints ===")
  
  -- Note: /health and /api/status are custom embedded API server endpoints
  -- not HC3 API endpoints, so we skip them in offline mode
  self:debug("✓ Core endpoints test completed (skipping custom server endpoints)")
end

-- Device endpoints
function QuickApp:testDeviceEndpoints()
  self:debug("=== Testing Device Endpoints ===")
  
  -- Get all devices
  local a,b = api.get("/devices")
  assert(b < 206, "/api/devices failed: "..b)
  self:debug("✓ /api/devices endpoint working")
  
  -- Get specific device (using device ID 1 as test)
  local a,b = api.get("/devices/1")
  assert(b < 206, "/api/devices/1 failed")
  self:debug("✓ /api/devices/{id} endpoint working")
  
  -- Get device property
  local a,b = api.get("/devices/1/properties/sunsetHour")
  assert(b < 206, "/api/devices/1/properties/sunsetHour failed")
  self:debug("✓ /api/devices/{id}/properties/{name} endpoint working")
  
  -- Get device action (GET version)
  local a,b = api.get("/devices/"..self.id.."/action/turnOn")
  assert(b < 206, "/api/devices/ID/action/turnOn failed")
  self:debug("✓ /api/devices/{id}/action/{name} endpoint working")
  
  -- Call action endpoint
  -- local a,b = api.get("/callAction")
  -- assert(b < 206, "/api/callAction failed")
  -- self:debug("✓ /api/callAction endpoint working")
  
  -- Device hierarchy
  -- local a,b = api.get("/devices/hierarchy")
  -- assert(b < 206, "/api/devices/hierarchy failed")
  -- self:debug("✓ /api/devices/hierarchy endpoint working")
end

-- Global Variables endpoints
function QuickApp:testGlobalVariablesEndpoints()
  self:debug("=== Testing Global Variables Endpoints ===")
  
  -- Get all global variables
  local a,b = api.get("/globalVariables")
  assert(b < 206, "/api/globalVariables failed")
  self:debug("✓ /api/globalVariables endpoint working")
  
  -- Get specific global variable
  local a,b = api.get("/globalVariables/testVar")
  assert(b < 206, "/api/globalVariables/testVar failed")
  self:debug("✓ /api/globalVariables/{name} endpoint working")
end

-- Rooms endpoints
function QuickApp:testRoomsEndpoints()
  self:debug("=== Testing Rooms Endpoints ===")
  
  -- Get all rooms
  local a,b = api.get("/rooms")
  assert(b < 206, "/api/rooms failed")
  self:debug("✓ /api/rooms endpoint working")
  
  -- Get specific room
  local a,b = api.get("/rooms/219")
  assert(b < 206, "/api/rooms/219 failed")
  self:debug("✓ /api/rooms/{id} endpoint working")
end

-- Sections endpoints
function QuickApp:testSectionsEndpoints()
  self:debug("=== Testing Sections Endpoints ===")
  
  -- Get all sections
  local a,b = api.get("/sections")
  assert(b < 206, "/api/sections failed")
  self:debug("✓ /api/sections endpoint working")
  
  -- Get specific section
  local a,b = api.get("/sections/219")
  assert(b < 206, "/api/sections/219 failed")
  self:debug("✓ /api/sections/{id} endpoint working")
end

-- Custom Events endpoints
function QuickApp:testCustomEventsEndpoints()
  self:debug("=== Testing Custom Events Endpoints ===")
  
  -- Get all custom events
  local a,b = api.get("/customEvents")
  assert(b < 206, "/api/customEvents failed")
  self:debug("✓ /api/customEvents endpoint working")
  
  -- Get specific custom event
  local a,b = api.get("/customEvents/testEvent")
  assert(b < 206, "/api/customEvents/testEvent failed")
  self:debug("✓ /api/customEvents/{name} endpoint working")
end

-- Refresh States endpoints
function QuickApp:testRefreshStatesEndpoints()
  self:debug("=== Testing Refresh States Endpoints ===")
  
  -- Get refresh states
  local a,b = api.get("/refreshStates")
  -- assert(b < 206, "/api/refreshStates failed")
  -- self:debug("✓ /api/refreshStates endpoint working")
end

-- iOS Devices endpoints
function QuickApp:testIosDevicesEndpoints()
  self:debug("=== Testing iOS Devices Endpoints ===")
  
  -- Get iOS devices
  local a,b = api.get("/iosDevices")
  assert(b < 206, "/api/iosDevices failed")
  self:debug("✓ /api/iosDevices endpoint working")
end

-- Home endpoints
function QuickApp:testHomeEndpoints()
  self:debug("=== Testing Home Endpoints ===")
  
  -- Get home information
  local a,b = api.get("/home")
  assert(b < 206, "/api/home failed")
  self:debug("✓ /api/home endpoint working")
end

-- Debug Messages endpoints
function QuickApp:testDebugMessagesEndpoints()
  self:debug("=== Testing Debug Messages Endpoints ===")
  
  -- Get debug messages
  local a,b = api.get("/debugMessages")
  assert(b < 206, "/api/debugMessages failed")
  self:debug("✓ /api/debugMessages endpoint working")
end

-- Weather endpoints
function QuickApp:testWeatherEndpoints()
  self:debug("=== Testing Weather Endpoints ===")
  
  -- Get weather information
  local a,b = api.get("/weather")
  assert(b < 206, "/api/weather failed")
  self:debug("✓ /api/weather endpoint working")
end

-- Plugins endpoints
function QuickApp:testPluginsEndpoints()
  self:debug("=== Testing Plugins Endpoints ===")
  
  -- Get plugin variables
  local a,b = api.get("/plugins/1/variables")
  assert(b < 206, "/api/plugins/1/variables failed")
  self:debug("✓ /api/plugins/{id}/variables endpoint working")
  
  -- Get specific plugin variable
  api.post("/plugins/"..self.id.."/variables",{name="testVar",value="testValue"})
  local a,b = api.get("/plugins/"..self.id.."/variables/testVar")
  assert(b < 206, "/api/plugins/1/variables/testVar failed")
  self:debug("✓ /api/plugins/{id}/variables/{name} endpoint working")
end

-- QuickApp endpoints
function QuickApp:testQuickAppEndpoints()
  self:debug("=== Testing QuickApp Endpoints ===")
  
  -- Get QuickApp files
  local a,b = api.get("/quickApp/"..self.id.."/files")
  assert(b < 206, "/api/quickApp/"..self.id.."/files failed")
  self:debug("✓ /api/quickApp/{id}/files endpoint working")
  
  -- Get specific QuickApp file
  local a,b = api.get("/quickApp/"..self.id.."/files/main")
  assert(b < 206, "/api/quickApp/"..self.id.."/files/main failed")
  self:debug("✓ /api/quickApp/{id}/files/{name} endpoint working")
  
  -- Export QuickApp
  local a,b = api.get("/quickApp/export/"..self.id)
  assert(b < 206, "/api/quickApp/export/"..self.id.." failed")
  self:debug("✓ /api/quickApp/export/{id} endpoint working")
end

-- Settings endpoints
function QuickApp:testSettingsEndpoints()
  self:debug("=== Testing Settings Endpoints ===")
  
  -- Get specific setting
  local a,b = api.get("/settings/location")
  assert(b < 206, "/api/settings/location failed")
  self:debug("✓ /api/settings/location endpoint working")

  local a,b = api.get("/settings/info")
  assert(b < 206, "/api/settings/info failed")
  self:debug("✓ /api/settings/info endpoint working")

end

-- Alarm endpoints
function QuickApp:testAlarmEndpoints()
  self:debug("=== Testing Alarm Endpoints ===")
  
  -- Get all partitions
  local a,b = api.get("/alarms/v1/partitions")
  assert(b < 206, "/api/alarms/v1/partitions failed")
  self:debug("✓ /api/alarms/v1/partitions endpoint working")
  
  -- Get specific partition
  local a,b = api.get("/alarms/v1/partitions/1")
  assert(b < 206, "/api/alarms/v1/partitions/1 failed")
  self:debug("✓ /api/alarms/v1/partitions/{id} endpoint working")
  
  -- Get alarm devices
  local a,b = api.get("/alarms/v1/devices")
  assert(b < 206, "/api/alarms/v1/devices failed")
  self:debug("✓ /api/alarms/v1/devices endpoint working")
end

-- Notification Center endpoints
function QuickApp:testNotificationCenterEndpoints()
  self:debug("=== Testing Notification Center Endpoints ===")
  
  -- Get notification center
  local a,b = api.get("/notificationCenter")
  assert(b < 206, "/api/notificationCenter failed")
  self:debug("✓ /api/notificationCenter endpoint working")
end

-- Profiles endpoints
function QuickApp:testProfilesEndpoints()
  self:debug("=== Testing Profiles Endpoints ===")
  
  -- Get all profiles
  local a,b = api.get("/profiles")
  assert(b < 206, "/api/profiles failed")
  self:debug("✓ /api/profiles endpoint working")
  
  -- Get specific profile
  local a,b = api.get("/profiles/1")
  assert(b < 206, "/api/profiles/1 failed")
  self:debug("✓ /api/profiles/{id} endpoint working")
end

-- Icons endpoints
function QuickApp:testIconsEndpoints()
  self:debug("=== Testing Icons Endpoints ===")
  
  -- Get icons
  local a,b = api.get("/icons")
  assert(b < 206, "/api/icons failed")
  self:debug("✓ /api/icons endpoint working")
end

-- Users endpoints
function QuickApp:testUsersEndpoints()
  self:debug("=== Testing Users Endpoints ===")
  
  -- Get users
  local a,b = api.get("/users")
  assert(b < 206, "/api/users failed")
  self:debug("✓ /api/users endpoint working")
end

-- Energy Devices endpoints
function QuickApp:testEnergyDevicesEndpoints()
  self:debug("=== Testing Energy Devices Endpoints ===")
  
  -- Get energy devices
  local a,b = api.get("/energy/devices")
  assert(b < 206, "/api/energy/devices failed")
  self:debug("✓ /api/energy/devices endpoint working")
end

-- Panels endpoints
function QuickApp:testPanelsEndpoints()
  self:debug("=== Testing Panels Endpoints ===")
  
  -- Get panels location
  local a,b = api.get("/panels/location")
  assert(b < 206, "/api/panels/location failed")
  self:debug("✓ /api/panels/location endpoint working")
  
  -- Get panels climate
  local a,b = api.get("/panels/climate")
  assert(b < 206, "/api/panels/climate failed")
  self:debug("✓ /api/panels/climate endpoint working")
  
  -- Get specific panel climate
  local a,b = api.get("/panels/climate/1")
  assert(b < 206, "/api/panels/climate/1 failed")
  self:debug("✓ /api/panels/climate/{id} endpoint working")
  
  -- Get panels notifications
  local a,b = api.get("/panels/notifications")
  assert(b < 206, "/api/panels/notifications failed")
  self:debug("✓ /api/panels/notifications endpoint working")
  
  -- Get panels family
  local a,b = api.get("/panels/family")
  assert(b < 206, "/api/panels/family failed")
  self:debug("✓ /api/panels/family endpoint working")
  
  -- Get panels sprinklers
  local a,b = api.get("/panels/sprinklers")
  assert(b < 206, "/api/panels/sprinklers failed")
  self:debug("✓ /api/panels/sprinklers endpoint working")
  
  -- Get panels humidity
  local a,b = api.get("/panels/humidity")
  assert(b < 206, "/api/panels/humidity failed")
  self:debug("✓ /api/panels/humidity endpoint working")
  
  -- Get panels favorite colors
  local a,b = api.get("/panels/favoriteColors")
  assert(b < 206, "/api/panels/favoriteColors failed")
  self:debug("✓ /api/panels/favoriteColors endpoint working")
  
  -- Get panels favorite colors v2
  local a,b = api.get("/panels/favoriteColors/v2")
  assert(b < 206, "/api/panels/favoriteColors/v2 failed")
  self:debug("✓ /api/panels/favoriteColors/v2 endpoint working")
end

-- Diagnostics endpoints
function QuickApp:testDiagnosticsEndpoints()
  self:debug("=== Testing Diagnostics Endpoints ===")
  
  -- Get diagnostics
  local a,b = api.get("/diagnostics")
  assert(b < 206, "/api/diagnostics failed")
  self:debug("✓ /api/diagnostics endpoint working")
end

-- Proxy endpoints
function QuickApp:testProxyEndpoints()
  self:debug("=== Testing Proxy Endpoints ===")
  
  -- Test proxy with a simple URL
  local a,b = api.get("/proxy?url=http://example.com")
  assert(b < 206, "/api/proxy failed")
  self:debug("✓ /api/proxy endpoint working")
end 

function QuickApp:turnOn() print("Turn On") end
api.post("/globalVariables",{name="testVar",value="testValue"})
api.post("/customEvents",{name="testEvent",userDescription="Hello"})