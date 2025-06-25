-- utils.lua - A simple utility module
local utils = {}

-- Function to format a string with a prefix
function utils.format_with_prefix(prefix, text)
  return prefix .. ": " .. text
end

-- Function to check if a string is empty
function utils.is_empty(str)
  return str == nil or str == ""
end

-- Function to capitalize the first letter of a string
function utils.capitalize(str)
  if utils.is_empty(str) then
  return str
  end
  return string.upper(string.sub(str, 1, 1)) .. string.sub(str, 2)
end

-- Function to create a simple table with key-value pairs
function utils.create_table(...)
  local t = {}
  local args = {...}
  for i = 1, #args, 2 do
  if args[i + 1] then
  t[args[i]] = args[i + 1]
  end
  end
  return t
end

-- Return the module
return utils 