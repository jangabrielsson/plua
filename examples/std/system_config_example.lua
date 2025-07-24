-- System Configuration Example
-- This example shows how to access system configuration information

print("=== System Configuration Example ===")

-- Display all configuration information
print("\nSystem Configuration (_PY.config):")
print("  Home Directory:", _PY.config.homedir)
print("  Current Directory:", _PY.config.cwd)
print("  Temp Directory:", _PY.config.tempdir)
print("  File Separator:", "'" .. _PY.config.fileseparator .. "'")
print("  Path Separator:", "'" .. _PY.config.pathseparator .. "'")
print("  Platform:", _PY.config.platform)
print("  Architecture:", _PY.config.architecture)
print("  Python Version:", _PY.config.python_version)
print("  Lua Version:", _PY.config.lua_version)
print("  Plua Version:", _PY.config.plua_version)
print("  Username:", _PY.config.username)
print("  Language:", _PY.config.lang)
print("  Debug Mode:", _PY.config.debug)
print("  Production Mode:", _PY.config.production)

-- Example of using configuration for cross-platform paths
print("\nCross-platform path examples:")
local home_config = _PY.config.homedir .. _PY.config.fileseparator .. "config"
print("  Config directory:", home_config)

local temp_file = _PY.config.tempdir .. _PY.config.fileseparator .. "plua_temp.txt"
print("  Temp file path:", temp_file)

-- Example of platform-specific logic
print("\nPlatform-specific behavior:")
if _PY.config.platform == "windows" then
    print("  Running on Windows - using Windows-specific settings")
elseif _PY.config.platform == "darwin" then
    print("  Running on macOS - using macOS-specific settings")
elseif _PY.config.platform == "linux" then
    print("  Running on Linux - using Linux-specific settings")
else
    print("  Running on unknown platform:", _PY.config.platform)
end

-- Example of debug mode usage
if _PY.config.debug then
    print("\nDebug mode is enabled!")
    print("  Extra debugging information will be shown")
    print("  Current PATH length:", string.len(_PY.config.path), "characters")
else
    print("\nDebug mode is disabled")
end

print("\n=== Configuration example complete ===")
