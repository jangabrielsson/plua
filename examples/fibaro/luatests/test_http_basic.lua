--%%name:HTTP basic
--%%type:com.fibaro.binarySwitch

FIBTEST:setup{name='HTTP basic',tests=3 }


function QuickApp:testHTTP(method,url,code,msg)
  self:debug(self.name,self.id)
  net.HTTPClient():request(url, {
    options = {
      method = method
    },
    success = function(res) FIBTEST:assert(res.status == code,"GET: Expected %s got %s",code,res.status) end,
    error = function(err)
      if type(code)=='function' then
        FIBTEST:assert(code(err),"ERR: Expected '%s' got '%s'",msg,err) 
      else
        FIBTEST:assert(err == code,"ERR: Expected '%s' got '%s'",code,err) 
      end
    end,
  })
end

function QuickApp:onInit()
  self:debug(self.name,self.id)
  self:testHTTP("GET","http://google.com",200)
  self:testHTTP("PUT","http://google.com",405)
  local errStr = "Cannot connect to host"
  self:testHTTP("GET","http://google.error",function(err) return tostring(err):match(errStr) end,errStr)
end
