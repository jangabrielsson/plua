


local function trans(str)
    local escTab = {["\""]="\\\"",["\'"]="\\'",["\\"]="\\\\",['"']='\\"',["\n"]="\\n",["\r"]="\\r",["\t"]="\\t"}
    local str1 = '"'..str:gsub(".",escTab)..'"'
    local str2 = json.encode2(str)
    print(str1) 
    print(str2) 
    local b = json.decode(str2)
    print(b)
end

trans("Hello\nWorld")
trans("Hello\'World")

-- local str = json.encode("Hello\nWorld")
-- print(str)
-- print(json.decode(str))