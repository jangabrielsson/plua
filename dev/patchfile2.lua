--%%name:Patch

if plugin.mainDeviceId == 5555 then
    local f = io.open("dev/patchfile.fqa")
    local fqa = f:read("*a")
    f:close()
    local file = fibaro.plua.config.scripts[1]
    fqa = json.decode(fqa)
    fqa.files[#fqa.files+1] = { 
      name = "foo", path = file
    }
    fibaro.plua.lib.loadFQA(fqa)
    return
end

print("YES")