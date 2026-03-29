--%%name:HTTPTestQA
--%%type:com.fibaro.deviceController
--%%offline:true

function QuickApp:onInit()
    self:debug(self.name, self.id)

    local url = "https://httpbin.org/get?SNs=EH257001316"
    local http = net.HTTPClient()

    http:request(url, {
        options = { method = "GET" },
        success = function(response)
            local ok, data = pcall(json.decode, response.data)
            if ok then
                self:debug("Response:", json.encodeFormated(data))
            else
                self:debug("Raw response:", response.data)
            end
        end,
        error = function(err)
            self:error("HTTP error:", tostring(err))
        end
    })
end
