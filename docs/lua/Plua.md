# PLUA Module Documentation

The `PLUA` module provides a collection of utility functions that bridge Lua with the underlying Python runtime. These functions offer file operations, system utilities, browser integration, and runtime state access.

## File Operations

### PLUA.readFile(path)
Reads the entire contents of a file.

**Parameters:**
- `path` (string): The file path to read

**Returns:**
- `string`: The file contents

**Example:**
```lua
-- Read a configuration file
local config_content = PLUA.readFile("config.json")
local config = json.decode(config_content)
print("Loaded config:", json.encode(config))
```

### PLUA.writeFile(path, content)
Writes content to a file, creating or overwriting it.

**Parameters:**
- `path` (string): The file path to write to
- `content` (string): The content to write

**Example:**
```lua
-- Write a log entry
local log_entry = os.date("[%Y-%m-%d %H:%M:%S] ") .. "Application started\n"
PLUA.writeFile("app.log", log_entry)

-- Save JSON data
local data = {name = "test", value = 42}
PLUA.writeFile("data.json", json.encode(data))
```

## Directory and Path Operations

### PLUA.getcwd()
Gets the current working directory.

**Returns:**
- `string`: The current working directory path

**Example:**
```lua
local current_dir = PLUA.getcwd()
print("Current directory:", current_dir)
```

### PLUA.listdir(path)
Lists the contents of a directory.

**Parameters:**
- `path` (string): The directory path to list

**Returns:**
- `table`: Array of filenames in the directory

**Example:**
```lua
-- List files in current directory
local files = PLUA.listdir(".")
print("Files in current directory:")
for i, filename in ipairs(files) do
    print("  " .. filename)
end

-- List files in a specific directory
local dev_files = PLUA.listdir("dev")
print("Found " .. #dev_files .. " files in dev/ directory")
```

### PLUA.pathInfo(path)
Gets detailed information about a path.

**Parameters:**
- `path` (string): The path to inspect

**Returns:**
- `table`: Table with path information (size, type, permissions, etc.)

**Example:**
```lua
local info = PLUA.pathInfo("README.md")
print("File info:", json.encode(info))

-- Check if it's a directory or file
if info.is_dir then
    print("It's a directory")
else
    print("It's a file, size:", info.size, "bytes")
end
```

### PLUA.fileExist(path)
Checks if a file or directory exists.

**Parameters:**
- `path` (string): The path to check

**Returns:**
- `boolean`: True if the path exists, false otherwise

**Example:**
```lua
if PLUA.fileExist("config.json") then
    local config = json.decode(PLUA.readFile("config.json"))
    print("Config loaded")
else
    print("Config file not found, using defaults")
end

-- Check multiple possible config locations
local config_paths = {"config.json", "conf/config.json", "../config.json"}
for _, path in ipairs(config_paths) do
    if PLUA.fileExist(path) then
        print("Found config at:", path)
        break
    end
end
```

## Encoding and Decoding

### PLUA.base64Encode(string)
Encodes a string to Base64.

**Parameters:**
- `string` (string): The string to encode

**Returns:**
- `string`: Base64 encoded string

**Example:**
```lua
local original = "Hello, World!"
local encoded = PLUA.base64Encode(original)
print("Encoded:", encoded)

-- Encode JSON data for transmission
local data = {user = "john", password = "secret123"}
local json_data = json.encode(data)
local encoded_data = PLUA.base64Encode(json_data)
print("Encoded data for API:", encoded_data)
```

### PLUA.base64Decode(string)
Decodes a Base64 string.

**Parameters:**
- `string` (string): The Base64 string to decode

**Returns:**
- `string`: Decoded string

**Example:**
```lua
local encoded = "SGVsbG8sIFdvcmxkIQ=="
local decoded = PLUA.base64Decode(encoded)
print("Decoded:", decoded)

-- Decode received data
local received_data = PLUA.base64Decode(encoded_data)
local data = json.decode(received_data)
print("Received user:", data.user)
```

## Browser and Web Interface

### PLUA.openInVSCodeBrowser(url)
Opens a URL in VS Code's integrated browser.

**Parameters:**
- `url` (string): The URL to open

**Returns:**
- `boolean`: True if successful, false otherwise

**Example:**
```lua
-- Open documentation
local success = PLUA.openInVSCodeBrowser("https://docs.python.org/3/")
if success then
    print("Documentation opened in VS Code browser")
end

-- Open local development server
PLUA.openInVSCodeBrowser("http://localhost:8888")
```

### PLUA.openWebInterface()
Opens the plua web interface.

**Returns:**
- `boolean`: True if successful, false otherwise

**Example:**
```lua
-- Open the web REPL interface
if PLUA.openWebInterface() then
    print("Web interface opened")
else
    print("Failed to open web interface")
end
```

### PLUA.openBrowser(url)
Opens a URL in the system's default browser.

**Parameters:**
- `url` (string): The URL to open

**Returns:**
- `boolean`: True if successful, false otherwise

**Example:**
```lua
-- Open external website
PLUA.openBrowser("https://github.com/jangabrielsson/plua")

-- Open local file
PLUA.openBrowser("file://" .. PLUA.getcwd() .. "/docs/README.md")
```

### PLUA.openBrowserSpecific(url, name)
Opens a URL in a specific browser.

**Parameters:**
- `url` (string): The URL to open
- `name` (string): The browser name

**Returns:**
- `boolean`: True if successful, false otherwise

**Example:**
```lua
-- Open in Chrome specifically
PLUA.openBrowserSpecific("https://example.com", "chrome")

-- Open in Firefox
PLUA.openBrowserSpecific("https://example.com", "firefox")
```

### PLUA.openWebInterfaceBrowser()
Opens the plua web interface in the system browser.

**Returns:**
- `boolean`: True if successful, false otherwise

**Example:**
```lua
-- Open web interface in external browser
PLUA.openWebInterfaceBrowser()
```

### PLUA.listBrowsers()
Lists available browsers on the system.

**Returns:**
- `table`: Array of browser names

**Example:**
```lua
local browsers = PLUA.listBrowsers()
print("Available browsers:")
for i, browser in ipairs(browsers) do
    print("  " .. browser)
end

-- Use the first available browser
if #browsers > 0 then
    PLUA.openBrowserSpecific("https://example.com", browsers[1])
end
```

## Console and Display

### PLUA.html2Console(string)
Converts HTML to console-friendly text.

**Parameters:**
- `string` (string): HTML string to convert

**Returns:**
- `string`: Console-friendly text

**Example:**
```lua
local html = "<h1>Hello</h1><p>This is <strong>bold</strong> text.</p>"
local console_text = PLUA.html2Console(html)
print("Console version:", console_text)

-- Process HTML from web content
local response_html = "<div class='status'>Status: <span class='ok'>OK</span></div>"
print("Status:", PLUA.html2Console(response_html))
```

### PLUA.getAvailableColors()
Gets the list of available color names for console output.

**Returns:**
- `table`: Array of color names

**Example:**
```lua
local colors = PLUA.getAvailableColors()
print("Available colors:")
for i, color in ipairs(colors) do
    print("  " .. color)
end

-- Use colors in output (assuming a color function exists)
-- print("<font color='" .. colors[1] .. "'>Colored text</font>")
```

## Runtime and System

### PLUA.getRuntimeState()
Gets the current runtime state including timer information.

**Returns:**
- `table`: Table with `active_timers` and `pending_timers` counts

**Example:**
```lua
-- Monitor runtime state
local state = PLUA.getRuntimeState()
print("Active timers:", state.active_timers)
print("Pending timers:", state.pending_timers)

-- Debug timer usage
setTimeout(function()
    local new_state = PLUA.getRuntimeState()
    print("Timer executed, new state:", json.encode(new_state))
end, 1000)
```

### PLUA.isRunning()
Checks if the runtime is still active.

**Returns:**
- `boolean`: True if running, false if shutting down

**Example:**
```lua
-- Graceful shutdown check
setInterval(function()
    if not PLUA.isRunning() then
        print("Runtime is shutting down, cleaning up...")
        -- Perform cleanup
        return
    end
    -- Continue normal operation
    print("Heartbeat:", os.date())
end, 5000)
```

### PLUA.getConfig()
Gets the current plua configuration.

**Returns:**
- `table`: Configuration table

**Example:**
```lua
local config = PLUA.getConfig()
print("Configuration:", json.encode(config))

-- Check specific config values
if config.debug then
    print("Debug mode is enabled")
end

if config.api_port then
    print("API server running on port:", config.api_port)
end
```

## Complete Example: File Processing with Web Output

Here's a complete example that demonstrates several PLUA functions working together:

```lua
function processLogFiles()
    local log_dir = "logs"
    
    -- Check if log directory exists
    if not PLUA.fileExist(log_dir) then
        print("Log directory not found")
        return
    end
    
    -- List all files in the log directory
    local files = PLUA.listdir(log_dir)
    local log_files = {}
    
    -- Filter for .log files
    for _, filename in ipairs(files) do
        if filename:match("%.log$") then
            table.insert(log_files, filename)
        end
    end
    
    print("Found " .. #log_files .. " log files")
    
    -- Process each log file
    local summary = {
        total_lines = 0,
        error_count = 0,
        files_processed = 0
    }
    
    for _, log_file in ipairs(log_files) do
        local file_path = log_dir .. "/" .. log_file
        local info = PLUA.pathInfo(file_path)
        
        print("Processing:", log_file, "(", info.size, "bytes)")
        
        local content = PLUA.readFile(file_path)
        local lines = {}
        for line in content:gmatch("[^\r\n]+") do
            table.insert(lines, line)
            if line:match("ERROR") then
                summary.error_count = summary.error_count + 1
            end
        end
        
        summary.total_lines = summary.total_lines + #lines
        summary.files_processed = summary.files_processed + 1
    end
    
    -- Create summary report
    local report = string.format([[
Log Processing Summary
====================
Files processed: %d
Total lines: %d
Errors found: %d
Processed at: %s
]], 
        summary.files_processed,
        summary.total_lines, 
        summary.error_count,
        os.date()
    )
    
    -- Save summary to file
    PLUA.writeFile("log_summary.txt", report)
    print("Summary saved to log_summary.txt")
    
    -- Open web interface to view results
    if PLUA.openWebInterface() then
        print("Web interface opened for viewing results")
    end
    
    return summary
end

-- Run the processing
local result = processLogFiles()
print("Processing complete:", json.encode(result))
```

This example demonstrates:
- File existence checking with `PLUA.fileExist()`
- Directory listing with `PLUA.listdir()`
- File information with `PLUA.pathInfo()`
- Reading files with `PLUA.readFile()`
- Writing results with `PLUA.writeFile()`
- Opening the web interface with `PLUA.openWebInterface()`
