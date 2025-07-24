-- Updated test to show current _PY contents and new user-facing function categorization

print("=== Current _PY Functions ===")
local count = 0
local total = 0
for k,v in pairs(_PY) do
  total = total + 1
  -- Only show functions, not tables or booleans
  if type(v) == "function" then
    count = count + 1
    print(string.format("%2d: %s = %s", count, k, v))
  end
end
print(string.format("\nFound %d functions out of %d total _PY entries", count, total))

print("\n=== User-Facing Functions by Category ===")
local user_by_category = _PY.list_user_functions_by_category()
for category, functions in pairs(user_by_category) do
    print("\n" .. category .. ":")
    for i, func_name in ipairs(functions) do
        print("  " .. i .. ": " .. func_name)
    end
end

print("\n=== All Functions by user_facing status ===")
local by_status = _PY.list_functions_by_user_facing()
print("User-facing: " .. #by_status.user_facing .. " functions")
print("Internal: " .. #by_status.internal .. " functions")

print("\n=== Testing User Functions ===")
print("Current time: " .. _PY.millitime())
print("Working directory: " .. _PY.getcwd())

local test_data = {name = "test", value = 42, nested = {a = 1, b = 2}}
local json_str = _PY.json_encode(test_data)
print("JSON encoded: " .. json_str)

local test_string = "Hello World! 🌍"
local encoded = _PY.base64_encode(test_string)
print("Base64 encoded '" .. test_string .. "': " .. encoded)
local decoded_str = _PY.base64_decode(encoded)
print("Base64 decoded: " .. decoded_str)

print("\n=== File and Directory Functions ===")
local files = _PY.listdir(".")
print("Files in current directory: " .. #files .. " items")
for i, file in ipairs(files) do
    if i <= 3 then -- Show first 3 items
        print("  " .. i .. ": " .. file)
    end
end
if #files > 3 then
    print("  ... and " .. (#files - 3) .. " more")
end

print("\n=== Lua-defined functions ===")
print("readFile function: " .. type(_PY.readFile))
print("writeFile function: " .. type(_PY.writeFile))
print("fileExist function: " .. type(_PY.fileExist))

-- Test Lua file functions
local test_file = "test_output.txt"
local test_content = "This is a test file created at " .. os.date() .. "\nSecond line with UTF-8: 🚀"
_PY.writeFile(test_file, test_content)
print("Wrote test file: " .. test_file)

if _PY.fileExist(test_file) then
    local read_content = _PY.readFile(test_file)
    print("Read back content: " .. string.len(read_content) .. " characters")
    print("First line: " .. read_content:match("([^\n]+)"))
end
