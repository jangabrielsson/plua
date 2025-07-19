-- Test to verify network module is working and ready for expansion
require("net")

print("Testing network module structure...")

-- Test HTTP client (existing functionality)
local http_client = net.HTTPClient()
print("✓ net.HTTPClient() is available")

-- Test the exported function directly
if _PY.http_request_async then
    print("✓ _PY.http_request_async is available")
else
    print("✗ _PY.http_request_async not found")
end

print("Network module is ready for additional functions!")

-- Make a simple HTTP request to verify everything works
http_client:request("http://httpbin.org/get", {
    success = function(response)
        print("✓ HTTP functionality verified - Status:", response.status)
    end,
    error = function(status)
        print("✗ HTTP test failed with status:", status)
    end
})
