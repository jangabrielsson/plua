
local LT = ...

LT.add({
  name = "QuickApp",
  func = function(done)
    fibaro.plua.lib.loadQAString(
[[
      function QuickApp:onInit()
        done()
      end
]],{env = { done = done }}
    )
  end,
  isAsync = true
})