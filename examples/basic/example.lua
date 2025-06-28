-- Load fibaro only if not already loaded (for compatibility with different environments)
if not fibaro then
  require('fibaro')
end

local b = json.decode('{}')
print(type(b))
b = json.decode("[]")
print(type(b))

fibaro.debug("EXAMPLE", "Hello", "World")
fibaro.trace("EXAMPLE", "Hello", "World")
fibaro.warning("EXAMPLE", "Hello", "World")
fibaro.error("EXAMPLE", "Hello", "World")

print(json.encode({4,3,5,6}))

net.HTTPClient():request("https://www.google.com", {
  options = {
    method = "GET",
    headers = {
      ["Content-Type"] = "application/json"
    }
  },
  success = function(response)
    --print(response.body:gsub("<","&lt;"):gsub(">","&gt;"))
  end,
  error = function(status)
    print("Error: " .. status)
  end
})

print(json.encodeFormated((api.get("/devices?name=test"))))

for i=1,10 do
  print(i)
end
