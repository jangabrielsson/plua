local mobdebug = require("mobdebug")
mobdebug.start('0.0.0.0', 8818)

_PLUA_VERSION = "1.0.0"
_print("PLua version: " .. _PLUA_VERSION)
_print("Lua version: " .. _VERSION)
_print("Python version: " .. _PY.get_python_version())

json = { encode = _PY.to_json, decode = _PY.parse_json }

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