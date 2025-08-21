-- Test script to verify system info detection on Windows
local sysinfo = _PY.get_system_info()

print("=== System Information Test ===")
print("Platform: " .. tostring(sysinfo.platform.system))
print("User: " .. tostring(sysinfo.environment.user))
print("Home: " .. tostring(sysinfo.environment.home))
print("CWD: " .. tostring(sysinfo.environment.cwd))
print("Path separator: " .. tostring(sysinfo.environment.path_separator))

-- Verify the values are not "unknown"
if sysinfo.environment.user == "unknown" then
    print("❌ ERROR: User detection failed!")
else
    print("✅ User detected successfully: " .. sysinfo.environment.user)
end

if sysinfo.environment.home == "unknown" then
    print("❌ ERROR: Home directory detection failed!")
else
    print("✅ Home directory detected successfully: " .. sysinfo.environment.home)
end
