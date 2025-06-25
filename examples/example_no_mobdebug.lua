_PLUA_VERSION = "1.0.0"
-- Removed MobDebug for VS Code compatibility test

print("PLua version: " .. _PLUA_VERSION)
print("Lua version: " .. _VERSION)
print("Python version: " .. _PY.get_python_version())

json = { encode = _PY.to_json, decode = _PY.parse_json }

-- Load the fibaro library
require('fibaro')

fibaro.debug("EXAMPLE", "Hello", "World")
fibaro.trace("EXAMPLE", "Hello", "World")
fibaro.warning("EXAMPLE", "Hello", "World")
fibaro.error("EXAMPLE", "Hello", "World")

print(json.encode({4,3,5,6}))

net.HTTPClient():request("https://www.google.com/", {
  options = {
  method = "GET",
  headers = {
  ["Content-Type"] = "application/json"
  }
  },
  success = function(response)
  print(response.body)
  end,
  error = function(status)
  print("Error: " .. status)
  end
})

for i=1,10 do
  print(i)
end 