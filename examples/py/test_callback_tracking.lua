-- Test callback tracking with HTTP requests
print("Starting HTTP request test...")

-- Register callback for HTTP request
local callback_id = _PY.registerCallback(function(err, response)
    if err then
        print("Error:", err)
    else
        print("Success! Status:", response.status)
        print("Response received, script should exit now")
    end
end)

print("Making HTTP request...")
_PY.call_http("http://www.google.com/", {}, callback_id)

print("Script finished, HTTP request is pending...")
print("CLI should wait for the HTTP response before exiting")
