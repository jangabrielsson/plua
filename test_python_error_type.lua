print("Testing Python function error result types")
print("==========================================")

-- Test 1: Call a Python function with correct arguments
print("Test 1: Correct arguments")
local result1 = _PY.http_request_sync("https://httpbin.org/get")
print("Result type:", type(result1))
print("Success:", result1.code == 200)
print()

-- Test 2: Call a Python function with too many arguments
print("Test 2: Too many arguments")
local success, error = pcall(function()
    _PY.http_request_sync("https://httpbin.org/get", "extra", "arguments")
end)
print("Caught error:", not success)
if not success then
    print("Error type:", type(error))
    print("Error message:", error)
    print("Error tostring:", tostring(error))
end
print()

-- Test 3: Call a Python function with wrong argument types
print("Test 3: Wrong argument types")
local success2, error2 = pcall(function()
    _PY.http_request_sync(123)  -- Passing number instead of string
end)
print("Caught error:", not success2)
if not success2 then
    print("Error type:", type(error2))
    print("Error message:", error2)
end
print()

-- Test 4: Call a non-existent Python function
print("Test 4: Non-existent function")
local success3, error3 = pcall(function()
    _PY.non_existent_function("test")
end)
print("Caught error:", not success3)
if not success3 then
    print("Error type:", type(error3))
    print("Error message:", error3)
end
print()

-- Test 5: Call a Python function that raises a specific exception
print("Test 5: Python function that raises exception")
local success4, error4 = pcall(function()
    _PY.http_request_sync({
        url = "https://httpbin.org/post",
        method = "POST",
        body = {not_a_string = true}  -- This should cause a TypeError
    })
end)
print("Caught error:", not success4)
if not success4 then
    print("Error type:", type(error4))
    print("Error message:", error4)
end
print()

print("Error type test completed!") 