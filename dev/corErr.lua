--%%name:TestErr
--%%var:a=8

local a,b = api.get("/icons")
print("Icons response:", #a, b)

net.HTTPClient():request("http://hc3/api/icons", {
    options = {
        method = "GET",
        headers = {
          ["Accept"] = "application/json", 
        ["Authorization"] = "Basic  YWRtaW46QWRtaW4xNDc3IQ==",
        ["X-Fibaro-Version"] = "1"
      }
    },
    success = function(response)
        ---print("HTTP Success:", response.status, response.data)
        local data = json.decode(response.data)
        print("Decoded:",#data)
        print("Decoded icons:", #data.device, #data.room, #data.scene)
    end,
    error = function(err)
        print("HTTP Error:", err)
    end
})