-- Simple async HTTP test to verify callback tracking
print("Starting async HTTP test...")

-- Test async HTTP request
_PY.http_request_async("https://httpbin.org/get", function(response)
  print("HTTP callback received!")
  print("Status code:", response.code)
  print("URL:", response.url)
  print("Body length:", #response.body)
  print("Error:", response.error or false)
  if response.error_message then
  print("Error message:", response.error_message)
  end
  print("Async HTTP test completed!")
end)

print("Async HTTP request initiated, waiting for callback...") 