
local LT = ...

LT.add("fibaro table type",'assertType',fibaro,'table')
LT.add("fibaro.plua type",'assertType',fibaro.plua,'userdata')
LT.add("fibaro.debug type",'assertType',fibaro.debug,'function')

LT.add({
  name = "async test",
  func = function(done)
    setTimeout(function()
      done()
    end,2000)
  end,
  isAsync = true
})