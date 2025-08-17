--%%name:Color2
--%%type:com.fibaro.multilevelSwitch
--%%project:3908
--%%description:Hello

function QuickApp:onInit()
  self:debug(self.name,self.id)
  net.HTTPClient():request("http://google.com", {
    options = {
      method = "PUT"
    },
    success = function(res) print("OK",res.status)  end,
    error = function(err) print("ERR",err) end
  })
end
