print("Testing Fibaro API after restart...")

-- Test calling the API server's devices endpoint
local http = require("socket.http")
local ltn12 = require("ltn12")

local response_body = {}
local res, code, response_headers = http.request{
    url = "http://127.0.0.1:8000/api/devices",
    sink = ltn12.sink.table(response_body)
}

if res then
    print("API call successful!")
    print("Response code:", code)
    print("Response body:", table.concat(response_body))
else
    print("API call failed!")
end

print("Test completed.") 