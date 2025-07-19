  local function foo()
    local function loop()
      print("PING")
      netWorkIO(function(data) print("Network callback", data) end)
      setTimeout(loop,5000)
    end
    setTimeout(loop,100)
  end
  foo()
  