currentZoneDetail,online = api.get("/panels/climate/"..zoneId)  -- working when HC3 on line
if online == 200 then -- We run on HC3
  print("getClimateZoneDetails() 1; connected to HC3")
else -- We run in the emulator so we will use a local PC file
  print("getClimateZoneDetails() 2; We run in the emulator and read ClimateZone.json file ")
  local f = fibaro.hc3emu.lua.io.open("ClimateZone.json", "r")
  assert(f,"Couln't open the file")
  currentZoneDetail = f:read("*a")
  f:close()
  if currentZoneDetail == nil then
    self:debug("currentZoneDetail is nil")
  else
    self:debug("currentZoneDetail is not nil")
    --print("getClimateZoneDetails(zoneId) 3; currentZoneDetail->", currentZoneDetail)
    currentZoneDetail = json.decode(currentZoneDetail)
    currentZoneDetail = currentZoneDetail[zoneId] -- in order to get the current zone details for the current ID
    
    self:setVariable("CurrentZoneDetail",currentZoneDetail)
    
    print("getClimateZoneDetails(zoneId) 4; json.encode(currentZoneDetail)->", json.encode(currentZoneDetail))
    return currentZoneDetail
  end
end
<following lines of code are ignored now>