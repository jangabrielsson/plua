print("Simple HTTP Test\n================\n")

-- Test 1: Simple GET request
print("Test 1: Simple GET request")
local response1 = _PY.http_request_sync("https://httpbin.org/get")
print("Status:", response1.code)
print("Body length:", #response1.body)
print("Response URL:", response1.url)
print()

-- Test 2: POST request with JSON body
print("Test 2: POST request with JSON body")
-- Create JSON string from Lua table
local post_data = {name = "John", age = 30, city = "New York"}
local json_body = _PY.to_json(post_data)
local response2 = _PY.http_request_sync{
  url = "https://httpbin.org/post",
  method = "POST",
  headers = {["Content-Type"] = "application/json"},
  body = json_body
}
print("Status:", response2.code)
print("Body length:", #response2.body)
print()

-- Test 3: Error handling
print("Test 3: Error handling (404)")
local response3 = _PY.http_request_sync("https://httpbin.org/status/404")
print("Status:", response3.code)
print("Error:", response3.error)
print()

print("Simple test completed successfully!") 