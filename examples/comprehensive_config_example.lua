-- Comprehensive Environment and Configuration Example
-- This example demonstrates both .env file loading and system configuration access

print("=== Environment and Configuration Example ===")

-- 1. System Configuration (always available)
print("\n1. System Configuration (_PY.config):")
print("   Platform:", _PY.config.platform)
print("   Architecture:", _PY.config.architecture)
print("   Home Directory:", _PY.config.homedir)
print("   File Separator:", "'" .. _PY.config.fileseparator .. "'")
print("   Debug Mode:", _PY.config.debug)
print("   Username:", _PY.config.username)

-- 2. Environment Variables (from .env file or system)
print("\n2. Environment Variables (.env file + system):")
local db_url = _PY.getenv_dotenv("DATABASE_URL", "sqlite:///default.db")
local api_key = _PY.getenv_dotenv("API_KEY", "")
local fibaro_host = _PY.getenv_dotenv("FIBARO_HOST", "192.168.1.1")
local timeout = tonumber(_PY.getenv_dotenv("TIMEOUT", "30")) or 30

print("   Database URL:", db_url)
print("   API Key:", api_key ~= "" and "***configured***" or "not set")
print("   Fibaro Host:", fibaro_host)
print("   Timeout:", timeout, "seconds")

-- 3. Practical Configuration Object
local app_config = {
    -- System info
    platform = _PY.config.platform,
    debug = _PY.config.debug,
    home_dir = _PY.config.homedir,
    file_sep = _PY.config.fileseparator,
    
    -- Application settings from .env
    database_url = _PY.getenv_dotenv("DATABASE_URL", "sqlite:///app.db"),
    api_key = _PY.getenv_dotenv("API_KEY", ""),
    timeout = tonumber(_PY.getenv_dotenv("TIMEOUT", "30")) or 30,
    
    -- Fibaro specific
    fibaro_host = _PY.getenv_dotenv("FIBARO_HOST", "192.168.1.1"),
    fibaro_user = _PY.getenv_dotenv("FIBARO_USER", "admin"),
    fibaro_pass = _PY.getenv_dotenv("FIBARO_PASS", ""),
    
    -- HTTP settings
    http_timeout = tonumber(_PY.getenv_dotenv("HTTP_TIMEOUT", "30")) or 30,
    user_agent = _PY.getenv_dotenv("USER_AGENT", "plua2/" .. _PY.config.plua2_version),
}

print("\n3. Application Configuration Object:")
for key, value in pairs(app_config) do
    if key:match("pass") or key:match("key") then
        print("   " .. key .. ":", value ~= "" and "***set***" or "not set")
    else
        print("   " .. key .. ":", value)
    end
end

-- 4. Cross-platform path building
print("\n4. Cross-platform Paths:")
local config_dir = app_config.home_dir .. app_config.file_sep .. ".plua2"
local log_file = config_dir .. app_config.file_sep .. "app.log"
local temp_dir = _PY.config.tempdir .. app_config.file_sep .. "plua2_temp"

print("   Config directory:", config_dir)
print("   Log file:", log_file)
print("   Temp directory:", temp_dir)

-- 5. Platform-specific behavior
print("\n5. Platform-specific Logic:")
local path_example
if app_config.platform == "windows" then
    path_example = "C:\\Users\\" .. _PY.config.username .. "\\Documents\\plua2"
    print("   Windows path example:", path_example)
elseif app_config.platform == "darwin" then
    path_example = "/Users/" .. _PY.config.username .. "/Documents/plua2"
    print("   macOS path example:", path_example)
else
    path_example = "/home/" .. _PY.config.username .. "/plua2"
    print("   Linux path example:", path_example)
end

-- 6. Debug information (only if debug mode is enabled)
if app_config.debug then
    print("\n6. Debug Information:")
    print("   Python version:", _PY.config.python_version)
    print("   Lua version:", _PY.config.lua_version)
    print("   Plua2 version:", _PY.config.plua2_version)
    print("   Current working directory:", _PY.config.cwd)
    print("   System language:", _PY.config.lang)
    print("   PATH length:", string.len(_PY.config.path), "characters")
end

print("\n=== Configuration example complete ===")

-- 7. Example function that uses configuration
local function make_api_request()
    if app_config.api_key == "" then
        print("\nSkipping API request - no API key configured")
        return
    end
    
    print("\nMaking API request with configuration...")
    local client = net.HTTPClient()
    
    client:request("https://httpbin.org/bearer", {
        options = {
            method = "GET",
            headers = {
                ["Authorization"] = "Bearer " .. app_config.api_key,
                ["User-Agent"] = app_config.user_agent
            },
            timeout = app_config.http_timeout
        },
        success = function(response)
            print("✅ API request successful! Status:", response.status)
            if app_config.debug then
                print("Response:", response.data)
            end
        end,
        error = function(status)
            if status == "timeout" then
                print("⏰ API request timed out after", app_config.http_timeout, "seconds")
            else
                print("❌ API request failed:", status)
            end
        end
    })
end

-- Call the example function
make_api_request()
