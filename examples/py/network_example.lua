-- Network module example demonstrating HTTP calls

local requests_pending = 0

local function mark_request_start()
    requests_pending = requests_pending + 1
    print("Request started, pending:", requests_pending)
end

local function mark_request_done()
    requests_pending = requests_pending - 1
    print("Request completed, pending:", requests_pending)
end

-- Test a simple GET request
print("Testing GET request...")
mark_request_start()
local get_callback_id = _PY.registerCallback(function(err, response)
    if err then
        print("Error in GET request:", err)
    else
        print("GET Response status:", response.status)
        print("Response type:", type(response.text))
        if response.text then
            print("Text length:", string.len(tostring(response.text)))
        end
    end
    mark_request_done()
end)
--_PY.call_http("https://httpbin.org/get", {}, get_callback_id)
_PY.call_http("http://www.google.com/", {}, get_callback_id)

-- Test a POST request with data
print("Testing POST request...")
mark_request_start()
local post_callback_id = _PY.registerCallback(function(err, response)
    if err then
        print("Error in POST request:", err)
    else
        print("POST Response status:", response.status)
        print("Response type:", type(response.text))
        if response.text then
            print("Text length:", string.len(tostring(response.text)))
        end
    end
    mark_request_done()
end)
_PY.call_http("https://httpbin.org/post", {
    method = "POST",
    headers = {
        ["Content-Type"] = "application/json"
    },
    data = '{"test": "data", "number": 42}'
}, post_callback_id)

-- Test with custom headers
print("Testing request with custom headers...")
mark_request_start()
local headers_callback_id = _PY.registerCallback(function(err, response)
    if err then
        print("Error in headers request:", err)
    else
        print("Headers Response status:", response.status)
        if response.text then
            print("Text length:", string.len(tostring(response.text)))
        end
    end
    mark_request_done()
end)
_PY.call_http("https://httpbin.org/headers", {
    headers = {
        ["User-Agent"] = "EPLua/1.0",
        ["X-Custom-Header"] = "test-value"
    }
}, headers_callback_id)

-- Test convenience functions (using call_http with different options)
print("Testing convenience patterns...")

-- Lua convenience function for GET requests
local function http_get(url, callback_id)
    _PY.call_http(url, {}, callback_id)
end

-- Lua convenience function for POST requests
local function http_post(url, data, callback_id)
    _PY.call_http(url, {
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json"
        },
        data = data
    }, callback_id)
end

mark_request_start()
local get_convenience_callback_id = _PY.registerCallback(function(err, response)
    if err then
        print("Error in Lua http_get:", err)
    else
        print("Lua http_get status:", response.status)
        if response.text then
            print("Text length:", string.len(tostring(response.text)))
        end
    end
    mark_request_done()
end)
http_get("https://httpbin.org/json", get_convenience_callback_id)

mark_request_start()
local post_convenience_callback_id = _PY.registerCallback(function(err, response)
    if err then
        print("Error in Lua http_post:", err)
    else
        print("Lua http_post status:", response.status)
        if response.text then
            print("Text length:", string.len(tostring(response.text)))
        end
    end
    mark_request_done()
end)
http_post("https://httpbin.org/post", '{"from": "lua_http_post"}', post_convenience_callback_id)

-- Check periodically for completion
local check_interval
check_interval = _PY.setInterval(function()
    print("Checking requests... pending:", requests_pending)
    if requests_pending == 0 then
        print("All network tests completed successfully!")
        _PY.clearInterval(check_interval)
    end
end, 1000)

-- Safety timeout
_PY.setTimeout(function()
    print("Network test timeout - some requests may not have completed")
    _PY.clearInterval(check_interval)
end, 10000)
