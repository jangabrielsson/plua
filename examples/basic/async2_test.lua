setTimeout(function() print("B") end,0)
--setTimeout(function() print("D - keeping program alive") end, 2000)
net.HTTPClient():request("http://www.google.com",{
  success = function(response)
    print("C")
  end,
  error = function(response)
    print("Err",response)
  end
})
print("A")
setInterval(function() print("PONG") end, 2000)
print("A1")
