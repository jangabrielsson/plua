-- Test smart JSON encoding with helper functions
print("=== SMART JSON ENCODING TEST ===")

json = require("plua.json")

-- Test 1: Create empty array and object
print("\n1. Creating empty array and object:")
local empty_array = _PY.create_array()
local empty_object = _PY.create_object()

print("Empty array type:", type(empty_array))
print("Empty object type:", type(empty_object))

print("Empty array JSON (smart):", _PY.to_json_smart(empty_array))
print("Empty object JSON (smart):", _PY.to_json_smart(empty_object))

-- Test 2: Add data to array
print("\n2. Adding data to array:")
empty_array[1] = "first"
empty_array[2] = "second"
empty_array[3] = "third"

print("Array with data JSON (smart):", _PY.to_json_smart(empty_array))
print("Array with data JSON (regular):", json.encode(empty_array))

-- Test 3: Add data to object
print("\n3. Adding data to object:")
empty_object.a = 1
empty_object.b = 2
empty_object.c = 3

print("Object with data JSON (smart):", _PY.to_json_smart(empty_object))
print("Object with data JSON (regular):", json.encode(empty_object))

-- Test 4: Regular Lua table (should default to object)
print("\n4. Regular Lua table:")
local regular_table = {x = 1, y = 2, z = 3}
print("Regular table JSON (smart):", _PY.to_json_smart(regular_table))
print("Regular table JSON (regular):", json.encode(regular_table))

-- Test 5: Mixed table (should default to object)
print("\n5. Mixed table:")
local mixed_table = {1, 2, a = 3, b = 4}
print("Mixed table JSON (smart):", _PY.to_json_smart(mixed_table))
print("Mixed table JSON (regular):", json.encode(mixed_table))

print("\n=== TEST COMPLETE ===") 