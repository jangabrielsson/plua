-- Comprehensive test of net.HTTPClient() features
require("net")

print("Testing HTTP client comprehensive features...")

local client = net.HTTPClient()

-- Test 1: Simple GET request
print("\n=== Test 1: Simple GET request ===")
client:request("http://httpbin.org/get", {
    success = function(response)
        print("✓ GET request successful!")
        print("Status:", response.status)
        print("Body length:", string.len(response.data))
    end,
    error = function(status)
        print("✗ GET request failed with status:", status)
    end
})

-- Test 2: POST request with data
setTimeout(function()
    print("\n=== Test 2: POST request with data ===")
    client:request("http://httpbin.org/post", {
        options = {
            method = "POST",
            headers = {
                ["Content-Type"] = "application/json",
                ["User-Agent"] = "plua2-http-client/1.0"
            },
            data = '{"message": "Hello from plua2!", "timestamp": "' .. os.date("%Y-%m-%d %H:%M:%S") .. '"}'
        },
        success = function(response)
            print("✓ POST request successful!")
            print("Status:", response.status)
            print("Response preview:", string.sub(response.data, 1, 200) .. "...")
        end,
        error = function(status)
            print("✗ POST request failed with status:", status)
        end
    })
end, 2000)

-- Test 3: Custom headers
setTimeout(function()
    print("\n=== Test 3: Custom headers ===")
    client:request("http://httpbin.org/headers", {
        options = {
            headers = {
                ["X-Custom-Header"] = "plua2-test",
                ["Authorization"] = "Bearer test-token"
            }
        },
        success = function(response)
            print("✓ Headers request successful!")
            print("Status:", response.status)
            -- Extract just the headers part from response
            local start_pos = string.find(response.data, '"headers"')
            if start_pos then
                local headers_part = string.sub(response.data, start_pos, start_pos + 300)
                print("Headers section:", headers_part .. "...")
            end
        end,
        error = function(status)
            print("✗ Headers request failed with status:", status)
        end
    })
end, 4000)

-- Test 4: Error handling (non-existent domain)
setTimeout(function()
    print("\n=== Test 4: Error handling test ===")
    client:request("http://non-existent-domain-12345.com", {
        success = function(response)
            print("✗ Unexpected success for invalid domain")
        end,
        error = function(status)
            print("✓ Error handling working - failed as expected with status:", status)
        end
    })
end, 6000)

print("\nAll tests initiated. Waiting for responses...")

-- Keep the runtime alive for a while to see all responses
setTimeout(function()
    print("\n=== All HTTP tests completed ===")
end, 10000)
