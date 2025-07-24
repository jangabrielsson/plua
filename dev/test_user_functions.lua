-- Test script to check the new user_facing function tagging system

print("=== All User-Facing Functions ===")
local user_functions = _PY.list_user_functions()
for i, func_name in ipairs(user_functions) do
    print(i .. ": " .. func_name)
end

print("\n=== User-Facing Functions by Category ===")
local user_by_category = _PY.list_user_functions_by_category()
for category, functions in pairs(user_by_category) do
    print("\n" .. category .. ":")
    for i, func_name in ipairs(functions) do
        print("  " .. i .. ": " .. func_name)
    end
end

print("\n=== Functions split by user_facing status ===")
local by_status = _PY.list_functions_by_user_facing()
print("User-facing: " .. #by_status.user_facing .. " functions")
print("Internal: " .. #by_status.internal .. " functions")

print("\n=== Function Metadata Sample ===")
local function_info = _PY.get_function_info()
local count = 0
for func_name, metadata in pairs(function_info) do
    if metadata.user_facing then
        print(func_name .. " (" .. metadata.category .. "): " .. metadata.description)
        count = count + 1
        if count >= 5 then break end  -- Show first 5 user functions
    end
end

print("\n=== Testing some user functions ===")
print("Current time: " .. _PY.millitime())
print("Working directory: " .. _PY.getcwd())

local test_data = {name = "test", value = 42}
local json_str = _PY.json_encode(test_data)
print("JSON encoded: " .. json_str)

local decoded = _PY.json_decode(json_str)
print("JSON decoded name: " .. decoded.name)
print("JSON decoded value: " .. decoded.value)

local test_string = "Hello World"
local encoded = _PY.base64_encode(test_string)
print("Base64 encoded '" .. test_string .. "': " .. encoded)

local decoded_str = _PY.base64_decode(encoded)
print("Base64 decoded: " .. decoded_str)
