--%%name:HTTPTestQA
--%%type:com.fibaro.deviceController
--%%offline:true

function QuickApp:onInit()
    self:debug(self.name, self.id)
    local location = 'foppolo'
    local url = "https://wttr.in/gg/" .. location
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
