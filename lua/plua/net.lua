
local net = {}
-- Creates a new HTTP client object.
-- @return A table representing the HTTP client.
function net.HTTPClient()
  local self = {}
  -- url is string
  -- options = { options = { method = "get", headers = {}, data = "...", timeout = 10000 }, success = function(response) end, error = function(status) end }
  function self:request(url, options)
    -- Create the request table for http_request_async
    local request_table = {
      url = url,
      method = options.options and options.options.method or "GET",
      headers = options.options and options.options.headers or {},
      body = options.options and options.options.data or nil
    }
    
    -- Create a callback function that will handle the response
    local callback = function(response)
      if response.error then
        -- Call error callback if provided
        if options.error then
          options.error(response.code or 0)
        end
      else
        -- Call success callback if provided
        if options.success then
          options.success(response)
        end
      end
    end
    
    -- Make the async HTTP request
    _PY.http_request_async(request_table, callback)
  end
  return self
end

return net