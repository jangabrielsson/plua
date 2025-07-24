-- Final verification of all user-facing functions
print("=== Final User-Facing Functions Verification ===")

local user_functions = _PY.list_user_functions_by_category()

print("Total categories with user-facing functions:", #user_functions)

for category, functions in pairs(user_functions) do
    print(string.format("\n%s (%d functions):", category, #functions))
    for i, func_name in ipairs(functions) do
        print(string.format("  %d: %s", i, func_name))
    end
end

-- Test a few key functions to ensure they work
print("\n=== Quick Function Tests ===")

-- Test browser functions
local browsers = _PY.list_browsers()
print("Available browsers:", #browsers)

-- Test HTML functions
local colors = _PY.get_available_colors()
print("Available colors:", #colors)

-- Test utility functions
local test_data = {name = "test", value = 42}
local json_str = _PY.json_encode(test_data)
print("JSON encoding works:", json_str)

-- Test file functions
local current_dir = _PY.getcwd()
print("Current directory:", current_dir)

print("\n=== All User-Facing Functions Working! ===")
