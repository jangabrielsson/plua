<p align="center">
    <img src="https://raw.githubusercontent.com/jangabrielsson/plua/main/docs/Plua.png" alt="PLua Logo" width="320"/>
</p>


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# PLua - Lua Runtime with Fibaro Home Automation Support

PLua is a powerful Lua interpreter built on Python that provides **native Fibaro Home Center 3 (HC3) QuickApp development and emulation**. Whether you're developing QuickApps for Fibaro home automation or just need a robust Lua runtime with async capabilities, PLua has you covered.

## 🏠 Why PLua for Fibaro Development?

- **🚀 QuickApp Development**: Full Fibaro SDK emulation with real QuickApp lifecycle
- **🖥️ Desktop UI**: Native desktop windows for QuickApp interfaces  
- **🔄 Live Development**: Hot reload, debugging, and instant testing
- **📡 Real-time APIs**: HTTP, WebSocket, TCP, UDP, and MQTT support
- **🎯 VS Code Integration**: Full debugging, tasks, and deployment tools
- **⚡ Fast Iteration**: No need to upload to HC3 for every test

## 🛠️ Installation

### Prerequisites
- Python 3.8+ 
- macOS, Linux, or Windows

### Quick Install (Recommended)
```bash
# Install PLua via pip
pip install plua

# Verify installation
plua --version
```

### Development Setup
If you want to contribute or work with the latest development version:
```bash
# Clone and set up for development
git clone https://github.com/jangabrielsson/plua.git
cd plua
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## 🚀 Quick Start

### 1. Create a New QuickApp Project
```bash
# Initialize a new QuickApp project with scaffolding
plua --init-qa

# Choose from 42 device templates:
# [1] Basic QuickApp - Simple starter template
# [2] Binary Switch - On/Off switch with actions  
# [3] Multilevel Switch - Dimmer/level control
# [4] Temperature Sensor - Temperature measurement
# ... and many more!
```

This creates a complete project structure:
```
my-quickapp/
├── .vscode/
│   ├── launch.json    # F5 debugging configuration
│   └── tasks.json     # HC3 upload/sync tasks
├── .project           # HC3 deployment config
└── main.lua          # Your QuickApp code
```

### 2. Develop and Test Locally
```bash
# Run your QuickApp with full Fibaro SDK
plua --fibaro main.lua

# With desktop UI window (if your QA has --%%desktop:true)
plua --fibaro main.lua

# Run for specific duration
plua --fibaro main.lua --run-for 30  # 30 seconds minimum
```

### 3. VS Code Integration
```bash
# Open project in VS Code
code .

# Press F5 to run/debug your QuickApp
# Use Ctrl+Shift+P -> "Tasks: Run Task" for HC3 operations:
# - "QA, upload current file as QA to HC3"
# - "QA, update QA (defined in .project)"
# - "QA, update single file (part of .project)"
```

## 📱 QuickApp Development

### Basic QuickApp Structure
```lua
--%%name:My Temperature Sensor
--%%type:com.fibaro.temperatureSensor  
--%%u:{label="temp", text="--°C"}

function QuickApp:onInit()
    self:debug("Temperature sensor started")
    self:updateView("temp", "text", "22.5°C")
    
    -- Simulate temperature readings
    fibaro.setInterval(5000, function()
        local temp = math.random(180, 250) / 10  -- 18.0-25.0°C
        self:updateView("temp", "text", temp .. "°C")
        self:updateProperty("value", temp)
    end)
end
```

### UI Elements
PLua supports all standard Fibaro UI elements:
```lua
--%%u:{button="btn1", text="Turn On", onReleased="turnOn"}
--%%u:{slider="level", min="0", max="100", onChanged="setLevel"}  
--%%u:{switch="toggle", text="Auto Mode", onToggled="setAuto"}
--%%u:{label="status", text="Ready"}
```

### Desktop Windows
Add `--%%desktop:true` to automatically open desktop UI windows:
```lua
--%%name:My Smart Light
--%%desktop:true
--%%u:{button="on", text="ON", onReleased="turnOn"}
```

## 🎛️ Interactive Development

### REPL (Read-Eval-Print Loop)
```bash
# Start interactive Lua session (recommended)
plua -i

# With Fibaro SDK loaded
plua -i --fibaro
```

In the REPL:
```lua
> print("Hello from PLua!")
Hello from PLua!

> fibaro.debug("Testing Fibaro API")
[DEBUG] Testing Fibaro API

> local qa = fibaro.createQuickApp(555)
> qa:debug("QuickApp created!")
```

### Telnet Server (for remote access)
PLua includes a multi-session telnet server for remote development:
```bash
# Start with telnet server (port 8023)
plua --telnet script.lua

# Or start just the telnet server
plua --telnet

# Connect from another terminal
telnet localhost 8023
```

## 🌐 Network & API Support

PLua provides comprehensive networking capabilities:

```lua
-- HTTP requests (async)
http.request("https://api.example.com/data", {
    method = "GET",
    success = function(response)
        print("Response:", response.data)
    end
})

-- WebSocket connections
local ws = websocket.connect("ws://localhost:8080")
ws:send("Hello WebSocket!")

-- MQTT client
local mqtt = require("mqtt")
mqtt.connect("broker.hivemq.com", 1883)

-- TCP/UDP sockets
local tcp = require("tcp")
local client = tcp.connect("127.0.0.1", 8080)
```

## 🔧 Command Line Options

```bash
plua [script.lua] [options]

Positional Arguments:
  script              Lua script file to run (optional)

Options:
  -h, --help          Show help message and exit
  -v, --version       Show version information
  --init-qa           Initialize a new QuickApp project
  -e, --eval EVAL     Execute Lua code fragments
  -i, --interactive   Start interactive Lua REPL (stdin/stdout with prompt_toolkit)
  --telnet            Start telnet server for remote REPL access
  --loglevel LEVEL    Set logging level (debug, info, warning, error)
  -o, --offline       Run in offline mode (disable HC3 connections)
  --desktop [BOOL]    Override desktop UI mode for QuickApp windows (true/false)
  -t, --tool          Run tool, [help, downloadQA, uploadQA, updateFile, updateQA]
  --nodebugger        Disable Lua debugger support
  --fibaro            Enable Fibaro HC3 emulation mode
  -l                  Ignored, for Lua CLI compatibility
  --header HEADER     Add header string (can be used multiple times)
  -a, --args ARGS     Add argument string to pass to the script
  --api-port PORT     Port for FastAPI server (default: 8080)
  --api-host HOST     Host for FastAPI server (default: localhost)
  --telnet-port PORT  Port for telnet server (default: 8023)
  --no-api            Disable FastAPI server
  --run-for N         Run script for specified seconds then terminate:
                      N > 0: Run at least N seconds or until no callbacks
                      N = 0: Run indefinitely (until killed)
                      N < 0: Run exactly |N| seconds
```

## 📂 Project Examples

Check out the `examples/` directory:
```bash
# Fibaro QuickApp examples
ls examples/fibaro/

# Basic Lua examples  
ls examples/lua/

# Python integration examples
ls examples/python/
```

## 🔍 Debugging & Development

### VS Code Debugging
1. Set breakpoints in your Lua code
2. Press F5 to start debugging
3. Use watch variables, call stack, and step through code

### Logging and Debug Output
```lua
-- Different log levels
self:debug("Debug message")
self:trace("Trace message") 
fibaro.debug("Global debug")
print("Console output")
```

### Live UI Updates
```lua
-- Update UI elements in real-time
self:updateView("label1", "text", "New text")
self:updateView("slider1", "value", 75)

-- Updates immediately appear in desktop windows
```

## 🏗️ Advanced Features

### Multiple QuickApps
Run several QuickApps simultaneously:
```bash
plua --fibaro qa1.lua qa2.lua qa3.lua
```

### Custom Device Types
PLua supports all Fibaro device types and interfaces:
- Binary switches, multilevel switches
- Sensors (temperature, humidity, motion, etc.)  
- HVAC systems and thermostats
- Security devices and detectors
- Media players and controllers

## 📚 Documentation
- [docs/QuickApp.md](docs/QuickApp.md) - QuickApp coding quickstart
- [docs/VSCode.md](docs/VSCode.md) - VSCode setup
- [docs/Zerobrane.md](docs/Zerobrane.md) - Zerobrane setup
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture and internals
- [QuickApp internals](docs/tutorials/README.md) - Some QuickApp implementation deep dives
- [docs/](docs/) - Detailed documentation and guides
- [examples/](examples/) - Code examples and templates
- [CHANGELOG.md](CHANGELOG.md) - Release notes and version history

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/jangabrielsson/plua/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jangabrielsson/plua/discussions)
- **Documentation**: [docs/](docs/) directory

---

**Happy QuickApp Development! 🏠✨**
