-- HTTP Client Module for EPLua
-- Demonstrates how to create a Lua module that dynamically loads Python backend
-- Similar to how lfs.lua works with filesystem.py

local http = {}

-- Dynamic module loading
local http_module = nil

local function ensure_http_loaded()
  if not http_module then
    print("Loading HTTP client module dynamically...")
    http_module = _PY.loadPythonModule("http_client")
    if http_module.error then
      error("Failed to load HTTP client module: " .. http_module.error)
    end
    print("HTTP client module loaded successfully!")
  end
  return http_module
end

-- High-level HTTP GET function
function http.get(url, headers)
  local client = ensure_http_loaded()
  
  -- Prepare request parameters
  local request = {
    url = url,
    method = "GET",
    headers = headers or {}
  }
  
  -- Make the HTTP call using the loaded Python function
  return client.http_request_sync(request)
end

-- High-level HTTP POST function
function http.post(url, data, headers)
  local client = ensure_http_loaded()
  
  -- Prepare request parameters
  local request = {
    url = url,
    method = "POST",
    data = data,
    headers = headers or {}
  }
  
  -- Make the HTTP call using the loaded Python function
  return client.http_request_sync(request)
end

-- Generic HTTP request function
function http.request(options)
  local client = ensure_http_loaded()
  
  -- Validate required options
  if not options.url then
    error("URL is required for HTTP request")
  end
  
  -- Set defaults
  options.method = options.method or "GET"
  options.headers = options.headers or {}
  
  -- Make the HTTP call using the loaded Python function
  return client.http_request_sync(options)
end

-- List available HTTP functions (for debugging)
function http.list_functions()
  local client = ensure_http_loaded()
  local functions = {}
  for name, func in pairs(client) do
    table.insert(functions, name)
  end
  table.sort(functions)
  return functions
end

return http
