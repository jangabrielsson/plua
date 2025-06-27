--%%name:Basic
--%%type:com.fibaro.binarySwitch

-- fibaro.hc3_url = "http://127.0.0.1:8000/"
-- local a,code = api.get("/devices")
-- print(json.encode(a),code)
json = require('plua.json')

local b,code = net.HTTPClient():request("http://127.0.0.1:8000/api/devices",{
  options = {
    method = "GET",
    headers = {
      ["Content-Type"] = "application/json",
    }
  },
  success = function(response)
    print(json.encode(response))
  end,
  error = function(err)
    print("Err:",err)
  end,
})


-- function QuickApp:onInit()
--   self:debug("onInit")
--   print("A")
--   setTimeout(function() print("PING") end, 1000)
--   fibaro.sleep(1000)
--   print("B")
-- end
