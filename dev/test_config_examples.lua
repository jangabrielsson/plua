-- Test practical usage of _PY.config
print("=== Practical _PY.config Usage Examples ===")

local config = _PY.config

-- 1. Platform-specific behavior
print("\n--- Platform Detection ---")
print("Running on:", config.platform)
if config.platform == "darwin" then
    print("This is macOS")
elseif config.platform == "linux" then
    print("This is Linux")
elseif config.platform == "windows" then
    print("This is Windows")
end

-- 2. Cross-platform path building
print("\n--- Cross-Platform Paths ---")
local app_config_dir = config.homedir .. config.fileseparator .. ".myapp"
local log_file = app_config_dir .. config.fileseparator .. "app.log"
print("App config directory:", app_config_dir)
print("Log file path:", log_file)

-- 3. Environment detection
print("\n--- Environment Detection ---")
print("Debug mode:", config.debug)
print("Production mode:", config.production)
if config.debug then
    print("Development environment detected")
    print("Init script location:", config.init_script_path)
end

-- 4. System information
print("\n--- System Information ---")
print("User:", config.username)
print("Architecture:", config.architecture)
print("Python version:", config.python_version)
print("Lua version:", config.lua_version)
print("Plua version:", config.plua_version)

-- 5. Network and directories
print("\n--- Network & Directories ---")
print("Host IP:", config.host_ip)
print("Current directory:", config.cwd)
print("Home directory:", config.homedir)
print("Temp directory:", config.tempdir)

-- 6. Environment variables
print("\n--- Environment Variables ---")
print("Language:", config.lang)
print("PATH (first 100 chars):", string.sub(config.path, 1, 100) .. "...")

-- 7. Runtime configuration (if available)
print("\n--- Runtime Configuration ---")
if config.runtime_config then
    print("Runtime config type:", type(config.runtime_config))
    print("Runtime config available: true")
else
    print("No runtime config available")
end
