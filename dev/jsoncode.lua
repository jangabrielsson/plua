--%%name:jsoncode
--%%save:jsoncode.fqa

if "H" == 'fibaro' then print("OK") end

local f = io.open("jsoncode.fqa","r")
local str = f:read("*a")
f:close()
--str = str:gsub("\\\'","'")
print(str)
local d = json.decode(str)
local files = d["files"]
for i=1,#files do
  print(files[i])
end
print(d["name"])