-- Debug HTTP callback functionality
print("Starting HTTP callback debug test...")

-- Test direct _PY.http_request_async call
print("Calling _PY.http_request_async directly...")

_PY.http_request_async("https://httpbin.org/get", function(response)
  print("SUCCESS CALLBACK CALLED!")
  print("Response code:", response.code)
  print("Response body length:", #response.body)
  print("Response URL:", response.url)
  if response.error then
  print("Response error:", response.error)
  print("Response error_message:", response.error_message)
  end
end)

print("HTTP request initiated, waiting for callback...") 