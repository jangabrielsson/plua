-- Test HTTP call sync functionality
print("Testing _PY.http_call_sync...")

-- Test 1: Simple GET request
print("\n1. Testing GET request to httpbin.org/get")
local success, status_code, response_body, error_message = _PY.http_call_sync(
    "GET", 
    "https://httpbin.org/get",
    {["User-Agent"] = "plua2-test/0.1.0"},
    nil
)

if success then
    print("✅ GET request successful!")
    print("Status code:", status_code)
    print("Response length:", #response_body)
    
    -- Try to parse JSON response
    local response_data = json.decode(response_body)
    if response_data and response_data.url then
        print("URL from response:", response_data.url)
        print("User-Agent from response:", response_data.headers["User-Agent"])
    end
else
    print("❌ GET request failed!")
    print("Status code:", status_code)
    print("Error:", error_message)
end

-- Test 2: POST request with JSON payload
print("\n2. Testing POST request with JSON payload")
local test_data = {
    name = "plua2 test",
    timestamp = os.time(),
    data = {1, 2, 3, "hello"}
}

local success2, status_code2, response_body2, error_message2 = _PY.http_call_sync(
    "POST",
    "https://httpbin.org/post",
    {
        ["Content-Type"] = "application/json",
        ["User-Agent"] = "plua2-test/0.1.0"
    },
    json.encode(test_data)
)

if success2 then
    print("✅ POST request successful!")
    print("Status code:", status_code2)
    print("Response length:", #response_body2)
    
    -- Parse response and check if our data was echoed back
    local response_data2 = json.decode(response_body2)
    if response_data2 and response_data2.json then
        print("Echoed data name:", response_data2.json.name)
        print("Echoed data timestamp:", response_data2.json.timestamp)
    end
else
    print("❌ POST request failed!")
    print("Status code:", status_code2)
    print("Error:", error_message2)
end

-- Test 3: Test with base64 encoding (simulating Basic Auth)
print("\n3. Testing with Base64 encoding for auth header")
local username = "testuser"
local password = "testpass"
local credentials = username .. ":" .. password
local encoded_creds = _PY.base64_encode(credentials)
print("Encoded credentials:", encoded_creds)

local success3, status_code3, response_body3, error_message3 = _PY.http_call_sync(
    "GET",
    "https://httpbin.org/basic-auth/" .. username .. "/" .. password,
    {
        ["Authorization"] = "Basic " .. encoded_creds,
        ["User-Agent"] = "plua2-test/0.1.0"
    },
    nil
)

if success3 then
    print("✅ Basic Auth request successful!")
    print("Status code:", status_code3)
    
    local response_data3 = json.decode(response_body3)
    if response_data3 and response_data3.authenticated then
        print("Authentication status:", response_data3.authenticated)
        print("User from response:", response_data3.user)
    end
else
    print("❌ Basic Auth request failed!")
    print("Status code:", status_code3)
    print("Error:", error_message3)
end

-- Test 4: Test error handling with invalid URL
print("\n4. Testing error handling with invalid URL")
local success4, status_code4, response_body4, error_message4 = _PY.http_call_sync(
    "GET",
    "https://invalid-domain-that-should-not-exist.com/test",
    {},
    nil
)

if success4 then
    print("❌ Unexpected success with invalid URL!")
    print("Status code:", status_code4)
else
    print("✅ Correctly failed with invalid URL")
    print("Status code:", status_code4)
    print("Error message:", error_message4)
end

print("\n=== HTTP call sync tests completed ===")
