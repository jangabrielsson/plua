-- Test external HTTP call to verify endpoints are working
print("Testing external HTTP call to our own server...")

local success, status_code, response_body, error_message = _PY.http_call_sync(
    "GET", 
    "http://localhost:8888/api/devices",
    {
      ["User-Agent"] = "plua/0.1.0",
      ["Content-Type"] = "application/json"
    },
    nil
)

print("External call success:", success)
print("External call status code:", status_code)
print("External call response body:", response_body)
print("External call error:", error_message)

print("Script completed successfully")
