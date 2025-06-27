--%%name:HTTP
--%%type:com.fibaro.binarySwitch

function QuickApp:onInit()
  self:debug("onInit")

  net.HTTPClient():request("http://google.com",{
    success = function(response)
      self:debug("success")
      print(response.data:sub(1,50))
    end,
    error = function(err)
      self:debug("error",err)
    end
  })

  self:debug("onInit done")
end


net.HTTPClient():request("http://google.com",{ success = function() print("OK") end })

 