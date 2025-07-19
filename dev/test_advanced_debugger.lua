-- Advanced test script for debugger testing
print("Advanced test script starting...")

-- Test variables of different types
local number_var = 42
local string_var = "Hello, World!"
local table_var = {a = 1, b = 2, c = "test"}
local boolean_var = true

print("Number:", number_var)
print("String:", string_var) 
print("Boolean:", boolean_var)

-- Test function calls and stack
local function helper_function(param)
    local local_var = param * 2
    print("In helper_function, local_var =", local_var)
    return local_var
end

local function main_function()
    print("In main_function")
    local result = helper_function(number_var)
    print("Result from helper:", result)
    
    -- Test loop with breakpoint potential
    for i = 1, 3 do
        local loop_var = i + result
        print("Loop", i, "loop_var =", loop_var)
        
        -- Nested condition
        if i == 2 then
            print("Special case: i == 2")
        end
    end
    
    return result
end

-- Call the main function
local final_result = main_function()
print("Final result:", final_result)

-- Test table access
print("Table contents:")
for k, v in pairs(table_var) do
    print("  " .. k .. " = " .. tostring(v))
end

print("Advanced test script ending...")
