



function IF(test, thenPart, elsePart)
  if test() then
    return thenPart()
  else
    return elsePart()
  end
end

IF(function() return 9==9 end,function() print("a is 9") end,function() print("a is not 9") end)