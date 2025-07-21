local function class(name)
  local cls = setmetatable({__USERDATA=true}, {
    __call = function(t,...)
      assert(rawget(t,'__init'),"No constructor")
      local obj = {__USERDATA=true}
      setmetatable(obj,{__index=t, __tostring = t.__tostring or function() return "object "..name end})
      obj:__init(...)
      return obj
    end,
    __tostring = function() return "class "..name end,
  })
  cls.__org = cls
  _G[name] = cls
  return function(p) getmetatable(cls).__index = p end
end

return class
