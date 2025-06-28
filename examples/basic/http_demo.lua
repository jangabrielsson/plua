print("HTTP Request Demo")
print("================")
print()

-- Test 1: Simple GET request
print("Test 1: Simple GET request")
local response1 = _PY.http_request_sync("https://httpbin.org/get")
print("Status:", response1.code)
print("Response URL:", response1.url)
print("Body type:", type(response1.body))
print("Body exists:", response1.body ~= nil)
print()

-- Test 2: POST request with JSON body
print("Test 2: POST request with JSON body")
-- Test with simple string first
print("Testing POST with simple string body...")
local simple_post_args = {
  url = "https://httpbin.org/post",
  method = "POST",
  headers = { ["Content-Type"] = "text/plain" },
  body = "Hello World"
}
local simple_response = _PY.http_request_sync(simple_post_args)
print("Simple POST Status:", simple_response.code)
print("Simple POST Body type:", type(simple_response.body))
print("Simple POST Body exists:", simple_response.body ~= nil)

-- Now test with JSON
print("Testing POST with JSON body...")
-- Create JSON string separately
local post_data = {name = "John", age = 30, city = "New York"}
local json_body = _PY.to_json(post_data)
print("Created JSON body:", json_body)

local post_args = {
  url = "https://httpbin.org/post",
  method = "POST",
  headers = { ["Content-Type"] = "application/json" },
  body = json_body
}
local response2 = _PY.http_request_sync(post_args)
print("Status:", response2.code)
print("Body type:", type(response2.body))
print("Body exists:", response2.body ~= nil)
print()

-- Test 3: Async request
print("Test 3: Async request")
_PY.http_request_async("https://httpbin.org/status/200", function(response)
  print("Async response received:")
  print("  Status:", response.code)
  print("  Body type:", type(response.body))
  print("  Body exists:", response.body ~= nil)
end)

-- Test 4: Error handling
print("Test 4: Error handling (404)")
local response4 = _PY.http_request_sync("https://httpbin.org/status/404")
print("Status:", response4.code)
print("Error:", response4.error)
print()

-- Test 5: Redirect following
print("Test 5: Redirect following")
local redirect_args = {
  url = "https://httpbin.org/redirect/2",
  redirect = true,
  maxredirects = 5
}
local response5 = _PY.http_request_sync(redirect_args)
print("Status:", response5.code)
print("Final URL:", response5.url)
print()

print("Demo completed. Async request will complete shortly...") 