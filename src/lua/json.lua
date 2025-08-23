local json = {}
json.encode = _PY.to_json
json.decode = _PY.parse_json
json.encodeFormated = _PY.to_json_formatted

local fmt = string.format
local escTab = {["\\"]="\\\\",['"']='\\"'}
local sortKeys = {"type","device","deviceID","id","name","properties","value","oldValue","val","key","arg","event","events","msg","res"}
local sortOrder={}
for i,s in ipairs(sortKeys) do sortOrder[s]="\n"..string.char(i+64).." "..s end
local function keyCompare(a,b)
  local av,bv = sortOrder[a] or a, sortOrder[b] or b
  return av < bv
end

--gsub("[\\\"]",{["\\"]="\\\\",['"']='\\"'})
-- our own json encode, as we don't have 'pure' json structs, and sorts keys in order (i.e. "stable" output)

local function quote(s)
  local t = type(s)
  if t == 'string' then return s end
  return "["..tostring(s).."]"
end

local function prettyJsonFlat(e0) 
  local res,seen = {},{}
  local function pretty(e)
    local t = type(e)
    if t == 'string' then res[#res+1] = '"' res[#res+1] = e:gsub("[\\\"]",escTab) res[#res+1] = '"'
    elseif t == 'number' then res[#res+1] = e
    elseif t == 'boolean' or t == 'function' or t=='thread' or t=='userdata' then
      if e == json.null then res[#res+1]='null'
      else res[#res+1] = tostring(e) end
    elseif t == 'table' then
      if next(e)==nil then 
        local mt = getmetatable(e)
        if mt and mt.__isArray then
          res[#res+1]='[]'
        else
          res[#res+1]='{}'
        end
      elseif seen[e] then res[#res+1]="..rec.."
      elseif e[1] or #e>0 then
        seen[e]=true
        res[#res+1] = "[" pretty(e[1])
        for i=2,#e do res[#res+1] = "," pretty(e[i]) end
        res[#res+1] = "]"
        seen[e]=nil
      else
        seen[e]=true
        if e._var_  then res[#res+1] = fmt('"%s"',e._str) return end
        local k,kmap = {},{} for key,_ in pairs(e) do local ks = tostring(key) k[#k+1] = ks; kmap[ks]=key end
        table.sort(k,keyCompare)
        if #k == 0 then res[#res+1] = "[]" return end
        res[#res+1] = '{'; res[#res+1] = '"' t = k[1] res[#res+1] = t; res[#res+1] = '":' pretty(e[kmap[t]])
        for i=2,#k do
          res[#res+1] = ',"' t = k[i] res[#res+1] = t; res[#res+1] = '":' pretty(e[kmap[t]])
        end
        res[#res+1] = '}'
        seen[e]=nil
      end
    elseif e == nil then res[#res+1]='null'
    else error("bad json expr:"..tostring(e)) end
  end
  pretty(e0)
  return table.concat(res)
end

local function prettyLuaFlat(e0) 
  local res,seen = {},{}
  local function pretty(e)
    local t = type(e)
    if t == 'string' then res[#res+1] = '"' res[#res+1] = e:gsub("[\\\"]",escTab) res[#res+1] = '"'
    elseif t == 'number' then res[#res+1] = tostring(e)
    elseif t == 'boolean' or t == 'function' or t=='thread' or t=='userdata' then
      if e == json.null then res[#res+1]='null'
      else res[#res+1] = tostring(e) end
    elseif t == 'table' then
      if next(e)==nil then 
        res[#res+1]='{}'
      elseif seen[e] then res[#res+1]="..rec.."
      elseif e[1] or #e>0 then
        seen[e]=true
        res[#res+1] = "{" pretty(e[1])
        for i=2,#e do res[#res+1] = "," pretty(e[i]) end
        res[#res+1] = "}"
        seen[e]=nil
      else
        seen[e]=true
        if e._var_  then res[#res+1] = fmt('"%s"',e._str) return end
        local k,kmap = {},{} for key,_ in pairs(e) do 
          ks = tostring(key)
          k[#k+1] = ks kmap[ks] = key
        end
        --print("keys",json.encode(k))
        table.sort(k,keyCompare)
        if #k == 0 then res[#res+1] = "{}" return end
        res[#res+1] = '{';  t = k[1]  res[#res+1] = quote(kmap[t]); res[#res+1] = '=' pretty(e[kmap[t]])
        for i=2,#k do
          res[#res+1] = ','  t = k[i] res[#res+1] = quote(kmap[t]); res[#res+1] = '=' pretty(e[kmap[t]])
        end
        res[#res+1] = '}'
        seen[e]=nil
      end
    elseif e == nil then res[#res+1]='null'
    else error("bad json expr:"..tostring(e)) end
  end
  pretty(e0)
  return table.concat(res)
end

json.encodeFast = prettyJsonFlat

function json.initArray(e) 
  return setmetatable(e,{__isArray=true})
end

json.encodeLua = prettyLuaFlat

json.util = {}
function json.util.InitArray(e) 
  return setmetatable(e,{__isArray=true})
end


return json