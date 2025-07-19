-- Simple JSON debug test
print("=== JSON Debug Test ===")

-- Test JSON functions availability
if _PY.json_encode then
    print("✓ json_encode is available")
else
    print("✗ json_encode not found")
end

if _PY.json_decode then
    print("✓ json_decode is available")
else
    print("✗ json_decode not found")
end

-- Test simple encoding
local test_table = {hello = "world"}
local encoded = _PY.json_encode(test_table)
print("Encoded:", encoded)

-- Test simple decoding  
local simple_json = '{"test": "value"}'
print("Decoding:", simple_json)
local decoded = _PY.json_decode(simple_json)
print("Decoded type:", type(decoded))

if decoded then
    print("Decoded test field:", decoded.test)
else
    print("Decoded is nil!")
end
