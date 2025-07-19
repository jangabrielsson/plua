-- Test the new HTTP client implementation
require("net")

print("Testing HTTP client with callback system...")

local client = net.HTTPClient()

local options = {
    options = {
        method = "GET",
        headers = {
            ["User-Agent"] = "plua2-http-client/1.0"
        }
    },
    success = function(response)
        print("✓ HTTP request successful!")
        print("Status:", response.status)
        print("Body length:", string.len(response.data))
        print("Body preview:", string.sub(response.data, 1, 100) .. "...")
    end,
    error = function(status)
        print("✗ HTTP request failed with status:", status)
    end
}

print("Making HTTP request to httpbin.org...")
client:request("http://httpbin.org/get", options)

print("Request initiated, waiting for response...")
