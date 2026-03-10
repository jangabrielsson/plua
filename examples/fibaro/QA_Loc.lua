--%%name:iosLocation
--%%type:com.fibaro.binarySwitch

--%%description:Track mobile devices and publish geofence events based on location updates from the Fibaro iOS app. Configure the locations to track and the devices to monitor using quick app variables.

-- QuickApp Variables:
-- <name>;<model>;<userId>;<deviceId>
-- If <userId> and <deviceId> are numbers, they will be used in the geofence event. Otherwise, the device will be tracked but no events will be published.

--%%var:a="Tim’s iPhone;iPhone 14 Pro;Tim;-"
--%%var:b="Jan’s 14 pro;iPhone 14 Pro;2;923"
--%%var:c="Danielas iPhone;iPhone 14 Pro;Dani;-"

local testData = [[ [{"name":"Jan’s Mac mini","accuracy":35.0,"lat":59.317291522247,"lon":18.064077324446,"map":"https://maps.apple.com/?q=59.317291522247096,18.064077324446178","model":"Mac mini (2024)","timestamp":1773130439956},{"name":"JanG's iPhone","model":"iPhone 6"},{"name":"AirPods Pro","model":"AirPods Pro"},{"name":"AirPods Pro","model":"AirPods Pro (2nd generation)"},{"name":"iPad","model":"iPad Air (5th generation)"},{"name":"Jan’s MacBook Pro","model":"MacBook Pro 13\""},{"name":"Jan’s Air","accuracy":36.0,"battery":0.98,"lat":59.316990338473,"lon":18.064056167843,"map":"https://maps.apple.com/?q=59.31699033847287,18.064056167842715","model":"MacBook Air","timestamp":1773130439798},{"name":"Jan’s 14 pro","accuracy":2.9501323295153,"battery":0.83,"lat":59.317082997879,"lon":18.063908126456,"map":"https://maps.apple.com/?q=59.317082997878614,18.063908126456315","model":"iPhone 14 Pro","timestamp":1773130446666},{"name":"Jan Gabrielsson’s iPad","model":"iPad Air"},{"name":"Jan’s Apple Watch","model":"Apple Watch Series 6 (GPS)"},{"name":"Jan’s Apple Watch","accuracy":19.606477032153,"battery":0.76,"lat":59.31707762767,"lon":18.063910931302,"map":"https://maps.apple.com/?q=59.31707762766998,18.063910931301844","model":"Apple Watch Series 10","timestamp":1773130444774},{"name":"Max’s iPhone","model":"iPhone 4"},{"name":"Max’s iPhone","model":"iPhone 4s"},{"name":"Max iPad","model":"iPad"},{"name":"Max iPad","model":"iPad"},{"name":"Max’s iPhone","model":"iPhone 6s"},{"name":"Max’s iPhone (2)","model":"iPhone 8"},{"name":"Max’s iPhone","accuracy":6.4809076210924,"battery":0.88,"lat":52.368162566409,"lon":4.9338917330797,"map":"https://maps.apple.com/?q=52.36816256640923,4.933891733079689","model":"iPhone 13 mini","timestamp":1773130446578},{"name":"Max’s Apple Watch","accuracy":27.999069985384,"battery":1.0,"lat":52.36821594663,"lon":4.9336090056101,"map":"https://maps.apple.com/?q=52.368215946629626,4.933609005610088","model":"Apple Watch Series 6 (GPS)","timestamp":1773130444244},{"name":"Max’s AirPods Pro","accuracy":6.0519829546848,"lat":52.368164733266,"lon":4.9338812298405,"map":"https://maps.apple.com/?q=52.368164733266,4.933881229840456","model":"AirPods Pro (2nd generation)","timestamp":1773102565413},{"name":"Max AirPods Pro","model":"AirPods Pro"},{"name":"Max’s MacBook Pro","accuracy":35.0,"battery":0.44,"lat":52.368205156412,"lon":4.9336781643485,"map":"https://maps.apple.com/?q=52.36820515641211,4.933678164348495","model":"MacBook Pro (14-inch, Nov 2023)","timestamp":1773130441714},{"name":"Max’s iPad","model":"iPad Pro 11-inch (M5)"},{"name":"Danielas MacBook Air","model":"MacBook Air 11\""},{"name":"Jan Gabrielssons iMac","model":"iMac"},{"name":"Danielas iPhone","model":"iPhone 6"},{"name":"Danielas iPhone","model":"iPhone XS"},{"name":"Danielas MacBook Air","model":"MacBook Air (Mid 2019)"},{"name":"Danielas iPhone","accuracy":12.014971917086,"battery":0.85,"lat":59.393691064661,"lon":18.035585082414,"map":"https://maps.apple.com/?q=59.39369106466088,18.035585082414215","model":"iPhone 14 Pro","timestamp":1773130443700},{"name":"AirPods Pro","model":"AirPods Pro"},{"name":"Apple Watch för Daniela","accuracy":121.495014,"battery":0.95,"lat":59.393792867552,"lon":18.03564967496,"map":"https://maps.apple.com/?q=59.393792867551774,18.035649674960393","model":"Apple Watch Series 10","timestamp":1773130443627},{"name":"Daniela – AirPods Pro","accuracy":22.339353504181,"lat":59.393633516315,"lon":18.035468212971,"map":"https://maps.apple.com/?q=59.39363351631458,18.035468212970795","model":"AirPods Pro (3rd generation)","timestamp":1773126401563},{"name":"Tim’s MacBook Pro","accuracy":35.0,"battery":0.16,"lat":59.318183003066,"lon":18.033185154307,"map":"https://maps.apple.com/?q=59.31818300306563,18.033185154307382","model":"MacBook Pro (14-inch, 2024)","timestamp":1773130441706},{"name":"Tim’s AirPods Pro","accuracy":19.252410136876,"lat":59.318160446956,"lon":18.033268251819,"map":"https://maps.apple.com/?q=59.31816044695618,18.03326825181892","model":"AirPods Pro (3rd generation)","timestamp":1773099805119},{"name":"Tim Gabrielsson’s iPad","accuracy":3.2570571196555,"battery":0.6,"lat":59.318185262284,"lon":18.03325367143,"map":"https://maps.apple.com/?q=59.31818526228352,18.03325367142958","model":"iPad Pro 11-inch","timestamp":1773130446305},{"name":"Tim’s iPhone","accuracy":14.448445183243,"battery":0.01,"lat":59.318236840734,"lon":18.033092213185,"map":"https://maps.apple.com/?q=59.31823684073358,18.0330922131846","model":"iPhone 14 Pro","timestamp":1773130443390}]
]]

local locations = {} -- hc3 defined locations
local home = {} -- home data
local tracks = {} -- devices we track

local oldTrace = QuickApp.trace
function QuickApp:trace(a,...)
  if a == 'onAction: ' then return end
  oldTrace(self,a,...)
end

local function calculateDistance(lat1, long1, lat2, long2)
  local rad = 3.141592654 / 180.0
  local dlat1  = lat1  * rad
  local dlong1 = long1 * rad
  local dlat2  = lat2  * rad
  local dlong2 = long2 * rad
  local dLong = dlong1 - dlong2
  local dLat  = dlat1 - dlat2
  local aHarv = (math.sin(dLat / 2.0) ^ 2.0) + math.cos(dlat1)
  * math.cos(dlat2) * (math.sin(dLong / 2) ^ 2)
  return 6371200 * 2 * math.atan(math.sqrt(aHarv), math.sqrt(1.0 - aHarv))
end

function QuickApp:onInit()
  self:debug("iosLocation")
  local locs = api.get("/panels/location")
  for k,v in ipairs(locs) do
    locations[v.id] = {id=v.id, radius=v.radius, lat=v.latitude, lon=v.longitude, name=v.name}
    self:debug("Location:",v.id,v.name,v.radius)
    if v.home then
      home.id = v.id
      home.name = v.name
      home.lat = v.latitude
      home.lon = v.longitude
      home.radius = v.radius
    end
  end
  local qvars = fibaro.getValue(self.id,"quickAppVariables")
  for _,q in ipairs(qvars) do
    local name,model,userId,deviceId = table.unpack(q.value:split(";"))
    userId = tonumber(userId) or userId
    deviceId = tonumber(deviceId) or deviceId
    tracks[#tracks+1] = { 
      userId = userId,
      deviceId = deviceId,
      name = name, 
      model = model, 
      loc = nil
    }
  end

  setInterval(function() -- Test code to simulate location updates from the iOS app
    self:iosLocation(json.decode(testData))
  end, 10*1000) -- Check every 10 seconds
end

local function isTracking(dev) -- If we are tracking this device, return id, else false
  for _,d in pairs(tracks) do
    if d.name:match(dev.name) and d.model:match(dev.model) then return d end
  end
  return false
end

function QuickApp:publishGeofenceEvent(userId, mobileDeviceId, locationId, geofenceAction, timestamp)
  local body = {
    userId = userId,
    deviceId = mobileDeviceId,
    locationId = locationId,
    geofenceAction = geofenceAction, 
    timestamp = timestamp,
  }
  return api.post("/events/publishEvent/GeofenceEvent", body)
end

local function postLocation(uid,did,locId,action,ts)
  print("user:",uid,",locId:",locId,",action:",action,",time:",os.time()-ts)
  if tonumber(uid) then
    quickApp:publishGeofenceEvent(uid,did,locId,action,ts)
  end
end

local function checkLocation(devData,dev)
  local uid = devData.userId
  local did = devData.deviceId
  local ts = dev.timestamp and dev.timestamp // 1000 or os.time()
  for _,loc in pairs(locations) do
    local dist = calculateDistance(dev.lat,dev.lon,loc.lat,loc.lon)
    if dist <= loc.radius then
      local oldLocId = devData.locId
      devData.loc = loc.name
      devData.locId = loc.id
      if oldLocId == loc.id then -- Same place, do nothing
        --
      elseif oldLocId == nil then -- Comming from away
        postLocation(uid,did,devData.locId,"enter",ts) -- Enter new
      else -- Comming from another position
        postLocation(uid,did,oldLocId,"leave",ts) -- Exit old loc
        postLocation(uid,did,devData.locId,"enter",ts) -- Enter new
      end
      return
    end
  end 
  if devData.locId or devData.loc == nil then -- old place, no longer
    local oldLocId = devData.locId
    devData.loc = "away"
    devData.locId = nil
    postLocation(uid,did,oldLocId,"leave",ts)
  else -- Already away/exited
  end
end

function QuickApp:iosLocation(locdata)
  for _,data in ipairs(locdata) do
    if data.lat then -- Only process location updates, ignore devices without location data 
      local deviceData = isTracking(data)
      if deviceData then 
        checkLocation(deviceData,data) 
      end
    end
  end
end
