--%%name=Init
--%%debug=http:true
--%%offline=true
--%%state=true
--%%webui=true
--%%conceal=token:"<put you HASS api token here>"

function QuickApp:onInit()

  self:debug("QuickApp Initialized", self.name, self.id)
  self:debug("Sunset", fibaro.getValue(1, "sunsetHour"))

  local location = api.get("/settings/location")
  print("Location:", location.latitude, location.longitude)

  local info = api.get("/settings/info")
  print("Info:", info.softVersion)

  local home = api.get("/home")
  print("Home:", home.currency)

  api.put("/home",{currency = "USD"}) -- Only offline...
  home = api.get("/home")
  print("Home:", home.currency)
end
