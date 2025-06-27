-- Test script for the new get_all_env_vars function

print("Testing environment variable functions...")

-- Test getting a single environment variable
local home_dir = _PY.get_env_var("HOME", "/default/home")
print("Home directory:", home_dir)

-- Test setting an environment variable
_PY.set_env_var("TEST_VAR", "test_value")
print("Set TEST_VAR to: test_value")

-- Test getting all environment variables
local env_vars = _PY.get_all_env_vars()
print("Total environment variables:", #env_vars)

-- Check if our test variable is in the table
if env_vars.TEST_VAR then
    print("TEST_VAR found:", env_vars.TEST_VAR)
else
    print("TEST_VAR not found in environment table")
end

-- Check some common environment variables
if env_vars.PATH then
    print("PATH found (length):", #env_vars.PATH)
else
    print("PATH not found")
end

if env_vars.HOME then
    print("HOME found:", env_vars.HOME)
else
    print("HOME not found")
end

-- Pretty print a few environment variables for demonstration
local sample_vars = {}
for key, value in pairs(env_vars) do
    if #sample_vars < 5 then  -- Only show first 5
        sample_vars[key] = value
    end
end

print("\nSample environment variables:")
_PY.print_table(sample_vars)

print("\nTest completed successfully!") 