--%%proxy:true


function QuickApp:onInit()
  print("HelperId",fibaro.plua.config.helperConnected)
  if fibaro.plua.DIR[self.id].device.isProxy then
    print("This is a proxy QuickApp")
  end
  print("Hc3",fibaro.plua.config.hc3_url)
    print("User",fibaro.plua.config.hc3_user)
end
