--%%name:Basic
--%%type:com.fibaro.binarySwitch

function QuickApp:onInit()
  self:debug("onInit")

  local devices = api.get("/devices?interface=quickApp")
  print(json.encodeFormated(devices[1]))
end

