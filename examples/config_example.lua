-- Configuration Example using .env file
-- This example shows how to use environment variables for configuration

require('mobdebug').on()

print("=== Configuration with .env Example ===")

-- Load configuration from .env file
print("\nLoading configuration...")

local config = {
    fibaro_host = _PY.getenv_dotenv("FIBARO_HOST", "192.168.1.1"),
    fibaro_user = _PY.getenv_dotenv("FIBARO_USER", "admin"),
    fibaro_pass = _PY.getenv_dotenv("FIBARO_PASS", "admin"),
    api_key = _PY.getenv_dotenv("API_KEY", ""),
    database_url = _PY.getenv_dotenv("DATABASE_URL", "sqlite:///app.db"),
    debug = _PY.getenv_dotenv("DEBUG", "false") == "true",
    timeout = tonumber(_PY.getenv_dotenv("TIMEOUT", "30")) or 30,
    log_level = _PY.getenv_dotenv("LOG_LEVEL", "INFO")
}

print("Configuration loaded:")
print("  Fibaro Host:", config.fibaro_host)
print("  Fibaro User:", config.fibaro_user)
print("  Fibaro Pass:", config.fibaro_pass and "***" or "not set")
print("  API Key:", config.api_key ~= "" and "***set***" or "not set")
print("  Database URL:", config.database_url)
print("  Debug Mode:", config.debug)
print("  Timeout:", config.timeout, "seconds")
print("  Log Level:", config.log_level)

-- Example of using configuration in HTTP requests
if config.api_key ~= "" then
    print("\nMaking authenticated API request...")
    
    local client = net.HTTPClient()
    client:request("https://httpbin.org/bearer", {
        options = {
            method = "GET",
            headers = {
                ["Authorization"] = "Bearer " .. config.api_key,
                ["User-Agent"] = "plua2-config-example/1.0"
            },
            timeout = config.timeout
        },
        success = function(response)
            print("✅ Authenticated request successful!")
            print("Status:", response.status)
            if config.debug then
                print("Response:", response.data)
            end
        end,
        error = function(status)
            if status == "timeout" then
                print("⏰ Request timed out after", config.timeout, "seconds")
            else
                print("❌ Request failed with status:", status)
            end
        end
    })
else
    print("\nNo API key configured, skipping authenticated request")
end

print("\n=== Configuration example complete ===")
