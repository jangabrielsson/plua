# _PY Module Documentation

The `_PY` module provides a collection of utility functions that bridge Lua with the underlying Python runtime. These functions offer file operations, system utilities, browser integration, JSON handling, and more.

## Available Functions by Category

### Browser Functions

#### _PY.list_browsers()
List available browsers on the system

#### _PY.open_browser()
Open URL in default browser

#### _PY.open_browser_specific()
Open URL in specific browser

#### _PY.open_web_interface_browser()
Open plua web interface in default browser

### File Functions

#### _PY.fileExist()
Check if a file or directory exists

#### _PY.getcwd()
Get the current working directory

#### _PY.listdir()
List directory contents

#### _PY.readFile()
Read the entire contents of a file

#### _PY.writeFile()
Write content to a file

### Html Functions

#### _PY.get_available_colors()
Get available color names for HTML conversion

#### _PY.html2console()
Convert HTML tags to console-friendly text with ANSI colors

### Introspection Functions

#### _PY.get_function_info()
Get metadata for all _PY functions

#### _PY.list_user_functions()
List all user-facing functions in _PY table

#### _PY.list_user_functions_by_category()
List user-facing functions grouped by category

### Json Functions

#### _PY.json_decode()
Decode JSON string to Lua table

#### _PY.json_encode()
Encode a Lua table to JSON string

#### _PY.json_encode_formated()
Encode a Lua table to JSON string formated

### Network Functions

#### _PY.http_call_sync()
Make a synchronous HTTP call from Lua

### System Functions

#### _PY.getenv()
Get an environment variable value

### Time Functions

#### _PY.millitime()
Get current epoch time with milliseconds as float

### Coroutine Functions

#### _PY.sleep(ms)
Sleeps current coroutime milliseconds.

### Utility Functions

#### _PY.base64_decode()
Base64 decode a string

#### _PY.base64_encode()
Base64 encode a string

### Vscode Functions

#### _PY.open_in_vscode_browser()
Open URL in VS Code Simple Browser

#### _PY.open_web_interface()
Open plua web interface in VS Code

### Debugging
#### _PY.mobdebug
Constains 
mobdebug.on()
mobdebug.stop()
mobdebug.coro()
If debugging is not enabled, the functions are defined as ID functions.

### Config data
#### _PY.config
System configuration and environment information table.

**Available Fields:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `architecture` | string | System architecture | `arm64`, `x86_64` |
| `cwd` | string | Current working directory | `/Users/user/Documents/dev/plua` |
| `debug` | boolean | Debug mode enabled | `true` or `false` |
| `fileseparator` | string | File path separator for OS | `/` (Unix) or `\` (Windows) |
| `homedir` | string | User's home directory | `/Users/username` |
| `host_ip` | string | Host machine IP address | `192.168.1.33` |
| `init_script_path` | string | Path to Lua initialization script | `/path/to/src/lua/init.lua` |
| `lang` | string | System language setting | `en_US.UTF-8` |
| `lua_version` | string | Lua version | `5.4` |
| `path` | string | System PATH environment variable | `/usr/bin:/bin:/usr/sbin...` |
| `pathseparator` | string | Path environment separator | `:` (Unix) or `;` (Windows) |
| `platform` | string | Operating system platform | `darwin`, `linux`, `windows` |
| `plua_version` | string | Plua runtime version | `1.0.54` |
| `production` | boolean | Production mode enabled | `true` or `false` |
| `python_version` | string | Python version running plua | `3.12.11` |
| `runtime_config` | table | Runtime-specific configuration | Lua table with runtime settings |
| `tempdir` | string | Temporary directory path | `/Users/username/tmp` |
| `username` | string | Current user name | `jangabrielsson` |

**Usage Examples:**

```lua
-- Get system information
local config = _PY.config
print("Platform:", config.platform)
print("Architecture:", config.architecture)
print("Python version:", config.python_version)
print("Lua version:", config.lua_version)

-- File operations using config
local app_config_path = config.homedir .. config.fileseparator .. ".myapp"
print("App config path:", app_config_path)

-- Build cross-platform paths
local data_file = config.cwd .. config.fileseparator .. "data" .. config.fileseparator .. "config.json"
print("Data file path:", data_file)

-- Check environment modes
if config.debug then
    print("Debug mode is enabled")
    print("Init script:", config.init_script_path)
end

if config.production then
    print("Running in production mode")
else
    print("Running in development mode")
end

-- Network and system info
print("Host IP:", config.host_ip)
print("Current user:", config.username)
print("Working directory:", config.cwd)
print("Temp directory:", config.tempdir)
print("System language:", config.lang)

-- Runtime configuration (if available)
if config.runtime_config then
    print("Runtime config available")
    -- Access runtime-specific settings
end
```

## Usage Examples

### Configuration and System Information
```lua
-- Access system configuration
local config = _PY.config

-- Platform-specific behavior
if config.platform == "windows" then
    print("Running on Windows")
elseif config.platform == "darwin" then
    print("Running on macOS")
else
    print("Running on Linux")
end

-- Build cross-platform file paths
local config_file = config.homedir .. config.fileseparator .. ".myapp" .. config.fileseparator .. "config.json"
print("Config file path:", config_file)

-- Check environment and adjust behavior
if config.debug then
    print("Debug mode: detailed logging enabled")
    print("Init script:", config.init_script_path)
end
```

### File Operations
```lua
-- Read a file
local content = _PY.readFile('config.txt')

-- Write a file
_PY.writeFile('output.txt', 'Hello World!')

-- Check if file exists
if _PY.fileExist('data.json') then
    local data = _PY.readFile('data.json')
    print('File found:', data)
end
```

### JSON Operations
```lua
-- Encode Lua table to JSON
local data = {name = 'test', value = 42}
local json_str = _PY.json_encode(data)

-- Decode JSON to Lua table
local decoded = _PY.json_decode(json_str)
print('Name:', decoded.name)
```

### Browser Integration
```lua
-- Open URL in default browser
_PY.open_browser('https://example.com')

-- Open in VS Code browser
_PY.open_in_vscode_browser('https://docs.lua.org')

-- List available browsers
local browsers = _PY.list_browsers()
for i, browser in ipairs(browsers) do
    print('Browser:', browser)
end
```

### HTML Console Output
```lua
-- Convert HTML to colored console output
local html = '<font color="red">Error:</font> Something went wrong'
local console_text = _PY.html2console(html)
print(console_text) -- Will show colored text in terminal

-- Get available colors
local colors = _PY.get_available_colors()
print('Available colors:', #colors)
```

### Utility Functions
```lua
-- Base64 encoding/decoding
local text = 'Hello World! 🌍'
local encoded = _PY.base64_encode(text)
local decoded = _PY.base64_decode(encoded)

-- Get current time in milliseconds
local timestamp = _PY.millitime()

-- Get current working directory
local cwd = _PY.getcwd()
print('Working directory:', cwd)

-- List directory contents
local files = _PY.listdir('.')
for i, file in ipairs(files) do
    print('File:', file)
end
```

## Function Discovery

The _PY module includes introspection functions to help discover available functionality:

```lua
-- List all user-facing functions by category
local by_category = _PY.list_user_functions_by_category()
for category, functions in pairs(by_category) do
    print('Category:', category)
    for i, func_name in ipairs(functions) do
        print('  Function:', func_name)
    end
end

-- Get information about a specific function
local info = _PY.get_function_info('readFile')
print('Description:', info.description)
print('Category:', info.category)
```

## Network Operations

```lua
-- Make synchronous HTTP requests
local response = _PY.http_call_sync('GET', 'https://api.example.com/data')
if response.success then
    print('Status:', response.status_code)
    print('Data:', response.data)
else
    print('Error:', response.error)
end
```

## System Functions

```lua
-- Get environment variables
local home_dir = _PY.getenv('HOME')
print('Home directory:', home_dir)

-- Get environment variable with default
local debug_mode = _PY.getenv('DEBUG', 'false')
print('Debug mode:', debug_mode)
```
