-- Test HC3 connectivity directly
print("=== HC3 CONNECTIVITY TEST ===")

json = require("plua.json")

-- Test 1: Test basic connectivity to HC3
print("\n1. Testing basic HC3 connectivity...")
local test_url = "http://192.168.1.57:80/api/refreshStates?last=0"
local headers = {Authorization = "Basic YWRtaW46QWRtaW4xNDc3IQ=="}

print("URL:", test_url)
print("Headers:", json.encode(headers))

-- Make a direct HTTP request
local request_data = {
    url = test_url,
    method = "GET",
    headers = headers
}

print("Making HTTP request...")
local http_result = _PY.http_request_sync(request_data)
print("HTTP status code:", http_result.code)
print("HTTP response body length:", #(http_result.body or ""))
print("HTTP response body (first 500 chars):", string.sub(http_result.body or "", 1, 500))

-- Test 2: Test a different endpoint to verify credentials
print("\n2. Testing different HC3 endpoint...")
local test_url2 = "http://192.168.1.57:80/api/devices"
local request_data2 = {
    url = test_url2,
    method = "GET",
    headers = headers
}

print("URL:", test_url2)
local http_result2 = _PY.http_request_sync(request_data2)
print("HTTP status code:", http_result2.code)
print("HTTP response body length:", #(http_result2.body or ""))
print("HTTP response body (first 500 chars):", string.sub(http_result2.body or "", 1, 500))

print("\n=== CONNECTIVITY TEST COMPLETE ===") 