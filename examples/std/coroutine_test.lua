


local function asyncFun(a, b)
  local co = coroutine.running()
  setTimeout(function() coroutine.resume(co, a + b) end, 2000)  -- Simulate async delay
  return coroutine.yield()  -- Yield until the async operation completes
end

local res = asyncFun(8,9)
print("Result from asyncFun:", res)



local function syncRequest(url)
  local co = coroutine.running()
  local client = net.HTTPClient()
  
  print("Making a GET request to",url)
  
  client:request("https://httpbin.org/get", {        
    success = function(response)
      print("✅ Request successful!")
      print("Status:", response.status)
      coroutine.resume(co, response.data)  -- Resume the coroutine with the response body_data
    end,
    error = function(status)
      print("❌ Request failed with status:", status)
      coroutine.resume(co, nil)  -- Resume the coroutine with nil on error
    end
  })
  return coroutine.yield()  -- Yield until the request completes
end

local data = syncRequest("https://httpbin.org/get")
print("Data from syncRequest:", data)