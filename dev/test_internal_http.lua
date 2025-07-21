-- Test internal HTTP call functionality
print("Testing _PY.http_call_internal...")

-- Test 1: Call the FastAPI server internally for devices
print("\n1. Testing internal call to /api/devices")
local success, status_code, response_body, error_message = _PY.http_call_internal(
    "GET",
    "/api/devices",
    {["User-Agent"] = "plua2-internal-test/0.1.0"},
    nil
)

if success then
    print("✅ Internal call successful!")
    print("Status code:", status_code)
    print("Response length:", #response_body)
    
    -- Try to parse JSON response
    local response_data = json.decode(response_body)
    if response_data then
        print("Number of devices:", #response_data)
        if #response_data > 0 then
            print("First device name:", response_data[1].name)
            print("First device type:", response_data[1].type)
        end
    end
else
    print("❌ Internal call failed!")
    print("Status code:", status_code)
    print("Error:", error_message)
end

-- Test 2: Call a specific device endpoint
print("\n2. Testing internal call to /api/devices/123")
local success2, status_code2, response_body2, error_message2 = _PY.http_call_internal(
    "GET",
    "/api/devices/123",
    {},
    nil
)

if success2 then
    print("✅ Device call successful!")
    print("Status code:", status_code2)
    
    local device_data = json.decode(response_body2)
    if device_data then
        print("Device ID:", device_data.id)
        print("Device name:", device_data.name)
    end
else
    print("❌ Device call failed!")
    print("Status code:", status_code2)
    print("Error:", error_message2)
end

-- Test 3: Call rooms endpoint
print("\n3. Testing internal call to /api/rooms")
local success3, status_code3, response_body3, error_message3 = _PY.http_call_internal(
    "GET",
    "/api/rooms", 
    {},
    nil
)

if success3 then
    print("✅ Rooms call successful!")
    print("Status code:", status_code3)
    
    local rooms_data = json.decode(response_body3)
    if rooms_data and #rooms_data > 0 then
        print("First room name:", rooms_data[1].name)
        print("First room ID:", rooms_data[1].id)
    end
else
    print("❌ Rooms call failed!")
    print("Status code:", status_code3)
    print("Error:", error_message3)
end

-- Test 4: Call non-existent endpoint to test error handling
print("\n4. Testing internal call to non-existent endpoint")
local success4, status_code4, response_body4, error_message4 = _PY.http_call_internal(
    "GET",
    "/api/nonexistent",
    {},
    nil
)

if success4 then
    print("Response for non-existent endpoint:")
    print("Status code:", status_code4)
    print("Response:", response_body4)
else
    print("❌ Non-existent endpoint call failed:")
    print("Error:", error_message4)
end

print("\n=== Internal HTTP call tests completed ===")
