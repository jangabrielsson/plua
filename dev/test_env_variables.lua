-- Example: Using HC3 environment variables from .env file
-- plua searches for .env files in this order:
-- 1. Current directory: ./.env (project-specific)
-- 2. Home directory: ~/.env (user-global)  
-- 3. Config directory: ~/.config/plua/.env (Linux/macOS) or %APPDATA%\plua\.env (Windows)

print("=== HC3 Environment Variables Example ===")
print("plua searches for .env files in the following order:")
print("  1. Current directory: ./.env")
print("  2. Home directory: ~/.env")
print("  3. Config directory: ~/.config/plua/.env (or %APPDATA%\\plua\\.env on Windows)")
print("")

-- Check if HC3 credentials are available
local hc3_url = os.getenv("HC3_URL")
local hc3_user = os.getenv("HC3_USER") 
local hc3_password = os.getenv("HC3_PASSWORD")

if hc3_url then
    print("✅ HC3_URL found:", hc3_url)
else
    print("❌ HC3_URL not set in environment")
end

if hc3_user then
    print("✅ HC3_USER found:", hc3_user)
else
    print("❌ HC3_USER not set in environment")
end

if hc3_password then
    print("✅ HC3_PASSWORD found: " .. string.rep("*", #hc3_password))
else
    print("❌ HC3_PASSWORD not set in environment")
end

-- Example of conditional behavior based on environment
local debug_mode = os.getenv("DEBUG") == "true"
print("Debug mode:", debug_mode and "enabled" or "disabled")

-- Show how to use .env variables in your scripts
if hc3_url and hc3_user and hc3_password then
    print("\n📋 HC3 credentials are configured!")
    print("   To test Fibaro integration, run:")
    print("   plua --fibaro your_fibaro_script.lua")
    
    -- Example: You could make API calls here using the credentials
    -- This is just for demonstration - actual API calls would be in fibaro.lua
    print("\n💡 Example usage in your scripts:")
    print("   local api_base = os.getenv('HC3_URL') .. '/api'")
    print("   -- Make authenticated requests to HC3...")
else
    print("\n⚠️  HC3 credentials not fully configured.")
    print("   Create a .env file or set environment variables:")
    print("   export HC3_URL=https://your-hc3-ip")
    print("   export HC3_USER=admin")
    print("   export HC3_PASSWORD=your_password")
end

-- Other environment variables you might use
local log_level = os.getenv("LOG_LEVEL") or "info"
print("\nLog level:", log_level)
