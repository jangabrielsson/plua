


local token = "YWRtaW46QWRtaW4xNDc3IQ=="
local url = "http://192.168.1.57/api/devices"

-- Declare variables outside pcall so they're accessible after
local success, status_code, response_body, error_message

local stat, err = pcall(function()
  success, status_code, response_body, error_message = _PY.http_call_sync(
    "GET", 
    url, 
    {
      ["User-Agent"] = "plua/0.1.0",
      ["Content-Type"] = "application/json",
      ["Authorization"] = "Basic " .. token,
    },
    nil
  )
end)

if not stat then
  print("Error:", err)
else
  print("HTTP call completed successfully")
end

print("Success:", success)
print("Status Code:", status_code)
print("Response Body:", response_body)
print("Error Message:", error_message)
