# plua

Python-Lua async runtime with timer support

## Overview

plua is a Python package that provides an async runtime environment for executing Lua scripts with JavaScript-like timer functionality. It bridges Python's asyncio with Lua's coroutines, allowing for sophisticated async programming patterns.

## Features

- **Interactive REPL**: Lua-like interactive prompt with plua features
- **JavaScript-like timers**: `setTimeout()`, `setInterval()`, `clearTimeout()`, `clearInterval()` in Lua
- **Async/await bridge**: Python asyncio integrated with Lua coroutines  
- **Context safety**: All Lua execution happens in the same Python context
- **Timer management**: Named asyncio tasks with cancellation support
- **Built-in REST API**: Automatic web server with REPL interface on port 8888
- **Network support**: HTTP client/server, WebSocket, TCP/UDP socket support
- **JSON support**: Built-in JSON encoding/decoding in Lua
- **Fibaro HC3 API**: Complete Home Center 3 API emulation with 267+ endpoints
- **MobDebug support**: Remote debugging with IDE integration
- **Coroutine support**: Full Lua coroutine functionality with yielding
- **Multi-platform executables**: Standalone binaries for Linux, Windows, macOS

## Installation

### For End Users (Recommended)

```bash
# Install plua globally (includes the 'plua' command)
pip install plua

# Verify installation
plua --version

# Start the interactive REPL
plua

# Run a Lua script
plua myscript.lua
```

After installation, the `plua` command will be available system-wide in your terminal/command prompt.

### Alternative: Standalone Executables

For users who prefer not to install Python dependencies, standalone executables are available:

```bash
# Download from GitHub Releases
# https://github.com/jangabrielsson/plua/releases

# Windows: plua-windows.exe
# macOS Intel: plua-macos-intel  
# macOS ARM: plua-macos-arm
# Linux: plua-linux

# Make executable and run (macOS/Linux)
chmod +x plua-linux
./plua-linux --version

# Windows: just run the .exe
plua-windows.exe --version
```

These executables include everything needed and don't require Python installation.

### For Developers

```bash
# Clone and install in development mode
git clone https://github.com/jangabrielsson/plua
cd plua
pip install -e .

# Install with development dependencies for testing/building
pip install -e ".[dev]"
```

### Troubleshooting Installation

#### Command Not Found (Windows)
If `plua` command is not recognized after installation on Windows:

1. **Check if pip installed to user directory:**
   ```cmd
   # Find where pip installed plua
   pip show -f plua
   
   # Check if Python Scripts directory is in PATH
   python -m site --user-base
   ```

2. **Add Python Scripts to PATH:**
   - Add `%APPDATA%\Python\Python3X\Scripts` to your PATH environment variable
   - Or use the full path: `python -m plua` instead of just `plua`

3. **Alternative installation methods:**
   ```cmd
   # Install system-wide (may require admin privileges)
   pip install --system plua
   
   # Force reinstall to ensure all dependencies are installed
   pip install --force-reinstall plua
   
   # Or use python -m to run without PATH issues
   python -m plua --version
   python -m plua script.lua
   ```

#### Missing Dependencies Error
If you get `ModuleNotFoundError` (e.g., "No module named 'aiomqtt'"):

```bash
# Force reinstall with all dependencies
pip install --force-reinstall plua

# Or install dependencies manually if needed
pip install aiomqtt>=2.0.0
```

#### FileNotFoundError on Windows
If you get `FileNotFoundError: [Errno 2] No such file or directory: 'src/plua/fibaro_api_models.py'`:

This was a bug in versions 1.0.57-1.0.59. Update to the latest version:

```bash
pip install --upgrade plua
```

#### Missing init.lua Error
If you get `FileNotFoundError: init.lua not found at: ...`:

This was a packaging issue in versions 1.0.57-1.0.68 where Lua files weren't included or couldn't be found properly. Update to the latest version:

```bash
pip install --upgrade plua
```

If you still get this error after updating to v1.0.69+, please run the command again to see detailed debug output and report the issue on GitHub.

#### Command Not Found (macOS/Linux)
```bash
# Check installation location
pip show plua

# Add pip's bin directory to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or use python -m
python -m plua --version
```

## Quick Start

### Command Line Usage

```bash
# Interactive REPL (no file specified)
plua

# Run a Lua file directly (API server starts automatically on port 8888)
plua script.lua

# Run without API server
plua --noapi script.lua

# Run with time limit
plua --duration 10 script.lua

# Custom API server settings
plua --api-port 9000 script.lua              # Custom port
plua --api-host 127.0.0.1 script.lua         # Custom host
plua --api-port 9000 --api-host 0.0.0.0 script.lua  # Custom host and port

# Run inline Lua code
plua -e 'print("Hello from Lua")'
plua -e 'print("start")' -e 'x=42' -e 'print(x)'     # Multiple -e fragments
plua -e 'print("setup")' script.lua                  # Combine -e and file

# Fibaro HC3 API support
plua --fibaro script.lua

# Debugging support
plua --debugger script.lua                           # Enable MobDebug
plua --debugger --debug script.lua                   # Verbose debug logging
plua --debugger --debugger-host 192.168.1.100 script.lua  # Remote debugger

# Utility commands
plua --cleanup-port                                   # Clean up stuck API port
plua --version                                        # Show version
```

### Interactive REPL

plua provides an interactive REPL (Read-Eval-Print Loop) when no Lua file is specified:

```bash
$ plua
Plua v1.0.54 Interactive REPL
Running Lua 5.4 with async runtime support

Quick start:
  help()                           - Show available commands
  print('Hello, plua!')           - Basic Lua
  json.encode({name='test'})       - JSON encoding
  setTimeout(function() print('Hi!') end, 2000) - Async timer

Type 'exit()' or press Ctrl+D to quit

plua> print("Hello, world!")
Hello, world!
plua> x = 42
plua> x + 10
52
plua> client = net.HTTPClient()
plua> setTimeout(function() print("Timer fired!") end, 2000)
plua> -- Timer fires after 2 seconds
Timer fired!
plua> exit()
Goodbye!
```

The REPL supports:
- All plua features (timers, JSON, networking)
- Built-in `json` and `net` modules (no require needed)
- Persistent variables and functions
- Background async operations
- Built-in help and state inspection
- Error recovery

### Python API Usage

```python
import asyncio
from plua import LuaAsyncRuntime

async def main():
    runtime = LuaAsyncRuntime()
    
    script = """
    print("Starting...")
    setTimeout(function() 
        print("Timer 1 fired!")
        setTimeout(function() print("Timer 2 fired!") end, 500)
    end, 1000)
    """
    
    await runtime.start(script=script, duration=5)

asyncio.run(main())
```

### REST API Server

plua includes a built-in REST API server that **starts automatically by default** on port 8888:

```bash
# API server starts automatically
plua script.lua

# Disable API server  
plua --noapi script.lua

# Custom API server settings
plua --api-port 9000 script.lua
plua --api-host 127.0.0.1 --api-port 8877 script.lua

# Access the web REPL interface
# Open browser to: http://localhost:8888/static/plua_main_page.html
```

#### API Endpoints

- `GET /` - API information and available endpoints
- `GET /static/plua_main_page.html` - Web-based REPL interface  
- `POST /plua/execute` - Execute Lua code remotely
- `GET /plua/status` - Get runtime status
- `GET /plua/info` - Get API and runtime information
- `GET /docs` - Swagger/OpenAPI documentation (if Fibaro API enabled)

#### Web REPL

The web REPL provides a modern browser-based interface for plua:

- **HTML Rendering**: Supports HTML tags in output for colored and formatted text
- **Real-time Execution**: Share interpreter state with local REPL
- **Timer Support**: Background timers work seamlessly
- **Modern UI**: Responsive design with syntax highlighting

Example HTML output in web REPL:
```lua
print("<font color='red'>Red text</font>")
print("<b>Bold text</b> | <i>Italic text</i>")
print("<span style='background-color: yellow;'>Highlighted</span>")
```

#### Remote Code Execution

```bash
# Execute Lua code via API
curl -X POST http://localhost:8888/plua/execute \
  -H 'Content-Type: application/json' \
  -d '{"code":"return 2 + 2", "timeout": 10.0}'
```

Response:
```json
{
  "success": true,
  "result": 4,
  "output": "",
  "error": null,
  "execution_time_ms": 0.123,
  "request_id": "uuid-here"
}
```

The API server and local REPL share the same Lua interpreter instance, so:
- Variables persist between API calls and REPL commands
- Timers set via API continue running in the background
- State is shared seamlessly between web and terminal interfaces

## VSCode launch
Setup launch tasks in .vscode/launch.json
The executable is either `plua` if installed and accesible globally,
or if running from the plua repo, `${workspaceFolder}/run.sh`

Running current lua file, with or without Fibaro support loaded.
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "plua: Run Current Lua file with Debugger", 
            "type": "luaMobDebug",
            "request": "launch",
            "workingDirectory": "${workspaceFolder}",
            "sourceBasePath": "${workspaceFolder}",
            "listenPort": 8172,
            "listenPublicly": false,
            "stopOnEntry": false,
            "sourceEncoding": "UTF-8",
            "executable": "plua",
            "arguments": [
                "--debugger",
                "--debugger-host",
                "localhost",
                "--debugger-port",
                "8172",
                "${file}"
            ]
        },
        {
            "name": "plua: Run Current Fibaro file with Debugger", 
            "type": "luaMobDebug",
            "request": "launch",
            "workingDirectory": "${workspaceFolder}",
            "sourceBasePath": "${workspaceFolder}",
            "listenPort": 8172,
            "listenPublicly": false,
            "stopOnEntry": false,
            "sourceEncoding": "UTF-8",
            "executable": "plua",
            "arguments": [
                "--debugger",
                "--debugger-host",
                "localhost",
                "--debugger-port",
                "8172",
                "--fibaro",
                "${file}"
            ]
        }
    ]
}
```

## Lua API

### Timer Functions

```lua
-- Set a timer (JavaScript-like)
local timer_id = setTimeout(function() 
    print("This runs after 1 second") 
end, 1000)

-- Set an interval timer
local interval_id = setInterval(function()
    print("This repeats every 2 seconds")
end, 2000)

-- Cancel timers
clearTimeout(timer_id)
clearInterval(interval_id)

-- Sleep (yields current coroutine)
sleep(500)  -- Sleep for 500ms
```

### Built-in Modules

```lua
-- JSON support (no require needed)
local data = {name = "test", value = 42}
local json_str = json.encode(data)
local parsed = json.decode(json_str)

-- HTTP client
local client = net.HTTPClient()
client:get("https://api.github.com/users/octocat", function(response)
    print("Status:", response.status)
    print("Body:", response.body)
end)

-- WebSocket client
local ws = net.WebSocketClient()
ws:connect("wss://echo.websocket.org/", {
    on_message = function(message)
        print("Received:", message)
    end
})
```

### Fibaro HC3 API Integration

```lua
-- Enable Fibaro API support
-- Run with: plua --fibaro script.lua

-- Use standard Fibaro API functions
fibaro.call(123, "turnOn")
local value = fibaro.getValue(456, "value") 
fibaro.sleep(1000)

-- QuickApp development
function QuickApp:onInit()
    self:debug("QuickApp started")
    self:updateProperty("value", 42)
end
```

### Coroutines

```lua
local function asyncFunction()
    print("Start")
    local co = coroutine.running()
    
    setTimeout(function() 
        coroutine.resume(co, "result") 
    end, 1000)
    
    local result = coroutine.yield()
    print("Got result:", result)
end

coroutine.wrap(asyncFunction)()
```

## Examples

### Example 1: HTTP Client with Timers

```lua
local client = net.HTTPClient()

-- Make HTTP request with timer fallback
local timer_id = setTimeout(function()
    print("Request timeout!")
end, 5000)

client:get("https://httpbin.org/delay/2", function(response)
    clearTimeout(timer_id)
    print("Response status:", response.status)
    print("Response time was acceptable")
end)
```

### Example 2: Interval Timer with Cancellation

```lua
local count = 0
local interval_id = setInterval(function()
    count = count + 1
    print("Ping", count)
    
    if count >= 5 then
        print("Stopping interval")
        clearInterval(interval_id)
    end
end, 1000)
```

### Example 3: Coroutine with Async Operations

```lua
local function asyncTask()
    print("Task starting...")
    
    -- Simulate async work
    local co = coroutine.running()
    setTimeout(function() 
        coroutine.resume(co, "async result") 
    end, 2000)
    
    local result = coroutine.yield()
    print("Task completed with:", result)
end

coroutine.wrap(asyncTask)()
```

## Architecture

### Components

- **`LuaInterpreter`**: Manages Lua runtime and script execution
- **`LuaAsyncRuntime`**: Handles asyncio integration and timer management
- **Timer System**: Maps Lua timer calls to Python asyncio tasks
- **Callback Loop**: Executes Lua callbacks in the correct context

### Flow

1. Lua calls `setTimeout(callback, delay)`
2. Python creates an asyncio task that waits for `delay`
3. When timer fires, Python queues the callback ID
4. Callback loop executes the Lua callback in the same context
5. Lua coroutines can yield and be resumed by timers

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Documentation Index](docs/README.md)** - Complete documentation overview
- **[Web REPL HTML Examples](docs/WEB_REPL_HTML_EXAMPLES.md)** - HTML rendering guide for web interface
- **[REST API Documentation](docs/api/README.md)** - Complete API reference and examples
- **[Developer Documentation](docs/dev/README.md)** - Implementation details and development guides

### Lua API Documentation

Detailed Lua API documentation is available in `docs/lua/`:

- **[Lua API Overview](docs/lua/README.md)** - Complete Lua API reference
- **[plua Core API](docs/lua/Plua.md)** - Timer functions and core plua features
- **[Timer System](docs/lua/Timers.md)** - setTimeout, setInterval, and timer management
- **[HTTP Client](docs/lua/HTTPClient.md)** - HTTP requests and client functionality
- **[WebSocket Client](docs/lua/WebSocket.md)** - WebSocket connections and messaging
- **[TCP Socket](docs/lua/TCPSocket.md)** - TCP client/server functionality
- **[UDP Socket](docs/lua/UDPSocket.md)** - UDP client/server functionality

### Fibaro HC3 Integration

- **[Fibaro API Overview](docs/lua/Fibaro.md)** - Fibaro HC3 API integration and functions
- **[QuickApp Development](docs/lua/QuickApp.md)** - QuickApp class and development patterns
- **[QuickApp Emulator](docs/lua/EmulatorQA.md)** - Local QuickApp development with header directives
- **[VS Code Integration](docs/lua/VSCodeintegration.md)** - IDE setup and debugging

### Quick Links
- 🚀 **Getting Started**: This README
- 🌐 **Web Interface**: [Web REPL Examples](docs/WEB_REPL_HTML_EXAMPLES.md)
- 📡 **API Integration**: [REST API Docs](docs/api/README.md)
- 🔧 **Contributing**: [Developer Docs](docs/dev/README.md)
- 📖 **Lua API**: [Lua Documentation](docs/lua/README.md)

## Fibaro HC3 API Integration

plua includes a comprehensive Fibaro Home Center 3 API emulator with full type safety and documentation:

### Generated API Endpoints

The Fibaro API endpoints are auto-generated from official Swagger/OpenAPI specifications:

```bash
# Regenerate Fibaro API endpoints and models
python src/plua/generate_typed_fibaro_api.py

# Generate with custom paths
python src/plua/generate_typed_fibaro_api.py --docs-dir fibaro_api_docs --output-dir src/plua
```

This generates:
- **`fibaro_api_models.py`**: 305+ Pydantic models with full type validation
- **`fibaro_api_endpoints.py`**: 267+ FastAPI endpoints with proper documentation

### Fibaro API Features

- **Complete Coverage**: All major Fibaro HC3 API endpoints
- **Type Safety**: Full Pydantic validation for request/response data
- **Swagger Documentation**: Auto-generated API docs at `/docs`
- **Lua Integration**: All calls delegate to `_PY.fibaro_api_hook(method, path, data)`
- **Easy Testing**: Use web interface or curl to test endpoints

```bash
# Start server with Fibaro API
plua --api-port 8888 --fibaro

# Test an endpoint
curl -X GET "http://localhost:8888/devices" -H "accept: application/json"
```

### HC3 Configuration with .env File

To connect plua to a real Fibaro Home Center 3 device, create a `.env` file with your HC3 credentials. plua searches for `.env` files in the following order:

1. **Current directory** (project-specific): `./.env`
2. **Home directory** (user-global): `~/.env` 
3. **Config directory** (platform-specific):
   - Linux/macOS: `~/.config/plua/.env`
   - Windows: `%APPDATA%\plua\.env`

```bash
# Option 1: Project-specific .env (recommended for development)
cd /path/to/your/fibaro/project
cat > .env << EOF
HC3_URL=https://192.168.1.100
HC3_USER=admin
HC3_PASSWORD=your_password_here
EOF

# Option 2: User-global .env (works from any directory)
cat > ~/.env << EOF
HC3_URL=https://192.168.1.100
HC3_USER=admin
HC3_PASSWORD=your_password_here
EOF
```

The `.env` file should contain:
- **`HC3_URL`**: Your Home Center 3 IP address or hostname (without trailing slash)
- **`HC3_USER`**: HC3 username (usually 'admin')  
- **`HC3_PASSWORD`**: HC3 password

Example `.env` file:
```env
# Fibaro HC3 Connection Settings
HC3_URL=https://192.168.1.100
HC3_USER=admin
HC3_PASSWORD=mySecretPassword123

# Optional: Add other environment variables your scripts might need
DEBUG=true
LOG_LEVEL=info
```

**Security Notes:**
- Project-specific `.env` files: Add `.env` to your `.gitignore` file to prevent committing credentials
- User-global `~/.env` file: Set appropriate file permissions (`chmod 600 ~/.env` on Unix systems)
- Use HTTPS URLs when possible
- Consider using environment variables directly in production environments

**Usage Examples:**
```bash
# Works from any directory if you have ~/.env configured
cd /any/directory
plua --fibaro my_script.lua

# Works from project directory with local .env
cd /my/fibaro/project
plua --fibaro script.lua   # Uses ./env (takes precedence over ~/.env)
```

**Usage in Lua Scripts:**
```lua
-- Access environment variables in your Lua code
local hc3_url = os.getenv("HC3_URL")
local debug_mode = os.getenv("DEBUG") == "true"

-- Environment variables are automatically loaded by the Fibaro emulator
-- when you use --fibaro flag
```

When you run plua with the `--fibaro` flag, it automatically reads these environment variables and configures the HC3 connection for API calls.

## Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/jangabrielsson/plua
cd plua
pip install -e ".[dev]"

# Setup HC3 credentials (optional, for Fibaro integration)
cp .env.example .env
# Edit .env with your HC3 credentials

# Install GitHub CLI for releases
brew install gh
gh auth login
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
```

### Type Checking

```bash
mypy src/
```

### Creating Releases

The project uses automated GitHub Releases with PyPI publishing and executable building:

```bash
# Quick patch release (1.0.54 → 1.0.55)
./scripts/create-release.sh patch

# Interactive release (choose patch/minor/major)  
./scripts/create-release.sh

# Custom version
./scripts/create-release.sh "2.0.0" "Major release with breaking changes"
```

Each release automatically:
- Publishes to PyPI
- Builds executables for Linux, Windows, macOS (Intel + ARM)
- Attaches binaries to GitHub release
- Updates documentation

## License

MIT License

## Requirements

- Python 3.8+
- lupa (Python-Lua bridge)
- asyncio (built-in)
