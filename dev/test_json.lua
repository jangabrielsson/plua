-- Test JSON encode and decode functions
print("=== Testing JSON Functions ===")

-- Test 1: Simple table encoding
print("\n--- Test 1: Encode Simple Table ---")
local simple_table = {
    name = "John",
    age = 30,
    active = true
}

local json_str = _PY.json_encode(simple_table)
print("JSON string:", json_str)

-- Test 2: Decode JSON string
print("\n--- Test 2: Decode JSON String ---")
local test_json = '{"message": "Hello, World!", "number": 42, "array": [1, 2, 3]}'
local decoded_table = _PY.json_decode(test_json)

if decoded_table.error then
    print("✗ JSON decode failed:", decoded_table.error)
else
    print("✓ JSON decode successful!")
    print("Message:", decoded_table.message)
    print("Number:", decoded_table.number)
    print("Array length:", #decoded_table.array)
    print("Array[1]:", decoded_table.array[1])
    print("Array[2]:", decoded_table.array[2])
    print("Array[3]:", decoded_table.array[3])
end

-- Test 3: Array encoding
print("\n--- Test 3: Encode Array ---")
local array_table = {1, 2, 3, "hello", true}
local array_json = _PY.json_encode(array_table)
print("Array JSON:", array_json)

-- Test 4: Round-trip test
print("\n--- Test 4: Round-trip Test ---")
local original = {
    users = {
        {name = "Alice", id = 1},
        {name = "Bob", id = 2}
    },
    status = "active",
    count = 2
}

local encoded = _PY.json_encode(original)
print("Encoded:", encoded)

local decoded = _PY.json_decode(encoded)
if decoded.error then
    print("✗ Round-trip failed:", decoded.error)
else
    print("✓ Round-trip successful!")
    print("Status:", decoded.status)
    print("Count:", decoded.count)
    print("First user:", decoded.users[1].name, "ID:", decoded.users[1].id)
    print("Second user:", decoded.users[2].name, "ID:", decoded.users[2].id)
end

-- Test 5: Error handling
print("\n--- Test 5: Error Handling ---")
local invalid_json = '{"invalid": json syntax}'
local error_result = _PY.json_decode(invalid_json)
if error_result.error then
    print("✓ Error handling works:", error_result.error)
else
    print("✗ Error handling failed - should have detected invalid JSON")
end

print("\n=== JSON Testing Complete ===")
