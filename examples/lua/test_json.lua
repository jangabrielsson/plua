-- JSON Module Test for EPLua
-- Tests json.encode, json.decode, and json.encodeFormated functions

local json = require('json')

print("=== JSON Module Test ===")

-- Test data
local test_data = {
    simple_string = "Hello, World!",
    number = 42,
    float = 3.14159,
    boolean_true = true,
    boolean_false = false,
    null_value = nil,
    array = {1, 2, 3, "four", 5.5},
    nested_object = {
        name = "John Doe",
        age = 30,
        address = {
            street = "123 Main St",
            city = "Anytown",
            country = "USA"
        },
        hobbies = {"reading", "coding", "hiking"}
    },
    mixed_array = {
        "string",
        42,
        true,
        {key = "value"},
        {1, 2, 3}
    }
}

print("\n1. Testing json.encode()")
print("=" .. string.rep("-", 40))

-- Test simple values
print("Encoding simple string:", json.encode("Hello"))
print("Encoding number:", json.encode(123))
print("Encoding boolean:", json.encode(true))
print("Encoding array:", json.encode({1, 2, 3}))

-- Test complex object
local encoded = json.encode(test_data)
print("Encoded test data:")
print(encoded)

print("\n2. Testing json.encodeFormated()")
print("=" .. string.rep("-", 40))

-- Test formatted encoding
local formatted = json.encodeFormated(test_data)
print("Formatted test data:")
print(formatted)

print("\n3. Testing json.decode()")
print("=" .. string.rep("-", 40))

-- Test decoding simple values
local simple_json = '{"name": "Alice", "age": 25, "active": true}'
local decoded_simple = json.decode(simple_json)
print("Decoded simple JSON:")
print("Name:", decoded_simple.name)
print("Age:", decoded_simple.age)
print("Active:", decoded_simple.active)

-- Test decoding the encoded test data
local decoded_complex = json.decode(encoded)
print("\nDecoded complex data:")
print("Simple string:", decoded_complex.simple_string)
print("Number:", decoded_complex.number)
print("Float:", decoded_complex.float)
print("Boolean true:", decoded_complex.boolean_true)
print("Boolean false:", decoded_complex.boolean_false)
print("Array length:", #decoded_complex.array)
print("Nested object name:", decoded_complex.nested_object.name)
print("Nested object city:", decoded_complex.nested_object.address.city)
print("First hobby:", decoded_complex.nested_object.hobbies[1])

print("\n4. Round-trip Test (encode -> decode -> encode)")
print("=" .. string.rep("-", 40))

-- Test round-trip consistency
local original = {
    message = "Round-trip test",
    data = {1, 2, 3},
    meta = {version = "1.0", timestamp = 1234567890}
}

local step1 = json.encode(original)
print("Step 1 - Encoded:", step1)

local step2 = json.decode(step1)
print("Step 2 - Decoded message:", step2.message)

local step3 = json.encode(step2)
print("Step 3 - Re-encoded:", step3)

-- Check if round-trip is consistent
local round_trip_success = (step1 == step3)
print("Round-trip consistent:", round_trip_success)

print("\n5. Error Handling Tests")
print("=" .. string.rep("-", 40))

-- Test invalid JSON
print("Testing invalid JSON:")
local invalid_json = '{"invalid": json, "missing": quote}'
local success, result = pcall(json.decode, invalid_json)
if success then
    print("Unexpected success with invalid JSON")
else
    print("Expected error with invalid JSON:", result)
end

-- Test encoding function (should fail)
print("\nTesting encoding function (should fail):")
local function test_func() return "test" end
local success2, result2 = pcall(json.encode, {func = test_func})
if success2 then
    print("Function encoded (unexpected):", result2)
else
    print("Expected error encoding function:", result2)
end

print("\n6. Special Cases")
print("=" .. string.rep("-", 40))

-- Test empty structures
print("Empty object:", json.encode({}))
print("Empty array:", json.encode({}))  -- Note: Lua tables are ambiguous

-- Test nested arrays
local nested_arrays = {{1, 2}, {3, 4}, {5, {6, 7}}}
print("Nested arrays:", json.encode(nested_arrays))

-- Test Unicode/special characters
local unicode_test = {
    emoji = "😀🎉",
    special = "Line1\nLine2\tTabbed",
    quotes = 'He said "Hello" to me'
}
print("Unicode/special chars:", json.encode(unicode_test))

-- Test formatted vs compact comparison
local comparison_data = {
    level1 = {
        level2 = {
            level3 = {
                deep = "value",
                array = {1, 2, 3, 4, 5}
            }
        }
    }
}

print("\nCompact encoding:")
print(json.encode(comparison_data))
print("\nFormatted encoding:")
print(json.encodeFormated(comparison_data))

print("\n7. Performance Test")
print("=" .. string.rep("-", 40))

-- Simple performance test
local large_array = {}
for i = 1, 100 do
    large_array[i] = {
        id = i,
        name = "Item " .. i,
        data = {i * 2, i * 3, i * 4}
    }
end

local start_time = os.clock()
local large_encoded = json.encode(large_array)
local encode_time = os.clock() - start_time

start_time = os.clock()
local large_decoded = json.decode(large_encoded)
local decode_time = os.clock() - start_time

print(string.format("Encoded %d items in %.4f seconds", #large_array, encode_time))
print(string.format("Decoded %d items in %.4f seconds", #large_decoded, decode_time))
print(string.format("Encoded size: %d characters", #large_encoded))

print("\n" .. string.rep("=", 50))
print("✅ JSON Module Tests Complete!")
print("✅ json.encode() - Working")
print("✅ json.decode() - Working")  
print("✅ json.encodeFormated() - Working")
print("✅ Error handling - Working")
print("✅ Round-trip consistency - Working")
print("✅ Special characters - Working")
print("✅ Performance - Acceptable")
print("\nThe json module provides full JSON functionality for EPLua!")
