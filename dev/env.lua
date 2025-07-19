for k,v in pairs(_G) do
  if v ~= _G then 
    print(k,"=",tostring(v))
  end
end