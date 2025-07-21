-- Test query parameters parsing

print("Testing query parameters...")

-- Test with query parameters
local result = _PY.http_call_internal(
    "GET", 
    "/api/devices?type=binarySwitch&roomID=219",
    nil,
    {
      ["User-Agent"] = "plua2/0.1.0"
    }
)

print("Query params test result:")
print("Success:", result.success)
print("Status Code:", result.status_code)

-- Test with POST data
local result2 = _PY.http_call_internal(
    "POST", 
    "/api/scenes",
    {name = "Test Scene", roomID = 219},
    {
      ["Content-Type"] = "application/json"
    }
)

print("\nPOST data test result:")
print("Success:", result2.success)
print("Status Code:", result2.status_code)
