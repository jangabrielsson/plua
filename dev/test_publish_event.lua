

function QuickApp:onInit()
  local f = coroutine.create(function()
    local a,b = pcall(function()
      local a,b = api.hc3.restricted.post("/plugins/publishEvent",{
        -- type = "centralSceneEvent",
        -- source = 46,
        -- data = { keyId = 1, keyAttribute = "Pressed" }
        type="ceneActivationEvent",
        source = 741,
        data = { sceneId = 16 }
      })
    end)
    print(a,b)
    print("OK",tostring(b),tostring(a))
  end)
  setTimeout(function() print("A") coroutine.resume(f) print("B") end,2000)
end

setInterval(function() end,10000)