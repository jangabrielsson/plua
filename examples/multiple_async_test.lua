-- Multiple async HTTP test to verify callback tracking
print("Starting multiple async HTTP test...")

local completed_requests = 0
local total_requests = 3

local function check_completion()
  completed_requests = completed_requests + 1
  print("Request", completed_requests, "completed!")
  
  if completed_requests >= total_requests then
  print("All requests completed! Exiting...")
  end
end

-- Test multiple async HTTP requests
_PY.http_request_async("https://httpbin.org/get", function(response)
  print("HTTP callback 1 received! Status:", response.code)
  check_completion()
end)

_PY.http_request_async("https://httpbin.org/status/200", function(response)
  print("HTTP callback 2 received! Status:", response.code)
  check_completion()
end)

_PY.http_request_async("https://httpbin.org/status/404", function(response)
  print("HTTP callback 3 received! Status:", response.code)
  check_completion()
end)

print("All async HTTP requests initiated, waiting for callbacks...") 