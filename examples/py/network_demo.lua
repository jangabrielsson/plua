-- Comprehensive network example for EPLua
-- This demonstrates the HTTP functionality using callback registration

print("=== EPLua Network Module Demo ===")
print()

-- Test 1: Simple GET request
print("1. Testing simple GET request...")
local get_callback = _PY.registerCallback(function(err, response)
    if err then
        print("   ERROR:", err)
    else
        print("   Status:", response.status, response.status_text)
        print("   Success:", response.ok)
        print("   Response length:", string.len(response.text))
    end
end)
_PY.call_http("https://httpbin.org/get", {}, get_callback)

-- Test 2: POST request with JSON data
print()
print("2. Testing POST request with JSON...")
local post_callback = _PY.registerCallback(function(err, response)
    if err then
        print("   ERROR:", err)
    else
        print("   Status:", response.status, response.status_text)
        print("   Success:", response.ok)
        print("   Response length:", string.len(response.text))
    end
end)
_PY.call_http("https://httpbin.org/post", {
    method = "POST",
    headers = {
        ["Content-Type"] = "application/json"
    },
    data = '{"message": "Hello from EPLua!", "timestamp": "2025-01-01"}'
}, post_callback)

-- Test 3: Request with custom headers
print()
print("3. Testing request with custom headers...")
local headers_callback = _PY.registerCallback(function(err, response)
    if err then
        print("   ERROR:", err)
    else
        print("   Status:", response.status, response.status_text)
        print("   Success:", response.ok)
        -- Try to parse and display headers that were sent
        if response.text and string.find(response.text, '"User%-Agent"') then
            print("   Custom User-Agent header was sent successfully")
        end
    end
end)
_PY.call_http("https://httpbin.org/headers", {
    headers = {
        ["User-Agent"] = "EPLua/1.0 Network Demo",
        ["X-Custom-Header"] = "EPLua-Demo",
        ["X-Test-Number"] = "42"
    }
}, headers_callback)

-- Test 4: Using convenience functions
print()
print("4. Testing convenience functions...")

-- HTTP GET convenience
local convenience_get_callback = _PY.registerCallback(function(err, response)
    if err then
        print("   http_get ERROR:", err)
    else
        print("   http_get Status:", response.status)
        print("   http_get Success:", response.ok)
    end
end)
_PY.http_get("https://httpbin.org/json", convenience_get_callback)

-- HTTP POST convenience
local convenience_post_callback = _PY.registerCallback(function(err, response)
    if err then
        print("   http_post ERROR:", err)
    else
        print("   http_post Status:", response.status)
        print("   http_post Success:", response.ok)
    end
end)
_PY.http_post("https://httpbin.org/post", '{"source": "http_post convenience function"}', convenience_post_callback)

print()
print("All requests initiated. Waiting for responses...")

-- Give time for all requests to complete
_PY.setTimeout(function()
    print()
    print("=== Demo Complete ===")
    print("The EPLua network module provides:")
    print("- call_http(url, options, callback_id) for flexible HTTP requests")
    print("- Convenience functions: http_get, http_post, http_put, http_delete")
    print("- Callback registration with _PY.registerCallback(function)")
    print("- Automatic Lua table conversion for response data")
    print("- Support for custom headers, POST data, and different HTTP methods")
end, 5000)
