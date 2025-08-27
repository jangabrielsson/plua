
# 🚀 QuickApp Development Guide: From Code to Execution

*A comprehensive guide to developing Fibaro QuickApps in Lua using PLua*

---

## 📋 Table of Contents

1. [**Getting Started**](#1-getting-started)
   - [Installing PLua](#11-installing-plua)
   - [VS Code Setup & Scaffolding](#12-vs-code-setup--scaffolding)
   - [Development Environment](#13-development-environment)

2. [**Basic QuickApp Structure**](#2-basic-quickapp-structure)
   - [Minimal QuickApp](#21-minimal-quickapp)
   - [Essential Methods](#22-essential-methods)
   - [Code Organization](#23-code-organization)

3. [**PLua Header Configuration**](#3-plua-header-configuration)
   - [Header Syntax](#31-header-syntax)
   - [Device Configuration](#32-device-configuration)
   - [Development Headers](#33-development-headers)
   - [UI Definition Headers](#34-ui-definition-headers)

4. [**Complete Header Reference**](#4-complete-header-reference)
   - [Basic Headers](#41-basic-headers)
   - [Advanced Headers](#42-advanced-headers)
   - [Development & Debugging](#43-development--debugging)

5. [**Practical Examples**](#5-practical-examples)
   - [Simple Sensor QuickApp](#51-simple-sensor-quickapp)
   - [Interactive UI QuickApp](#52-interactive-ui-quickapp)
   - [Advanced Configuration](#53-advanced-configuration)

6. [**Best Practices**](#6-best-practices)
   - [Code Structure](#61-code-structure)
   - [Header Organization](#62-header-organization)
   - [Testing & Debugging](#63-testing--debugging)

---

## 1. Getting Started

### 1.1 Installing PLua

**Prerequisites:**
```bash
# Ensure Python 3.8+ is installed
python3 --version
```

**Standard Installation (Recommended):**
```bash
# Install PLua from PyPI
pip install plua

# Test installation
plua --help
```

**Alternative: Virtual Environment Installation:**
```bash
# Create and activate virtual environment (recommended for development)
python3 -m venv plua-env
source plua-env/bin/activate  # On Windows: plua-env\Scripts\activate

# Install PLua
pip install plua

# Test installation
plua --help
```

**Developer Installation (PLua Contributors Only):**
```bash
# Clone PLua repository for development
git clone https://github.com/jangabrielsson/plua.git
cd plua

# Set up development environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Test development installation
./run.sh --help
```

### 1.2 VS Code Setup & Scaffolding

**Recommended VS Code Extensions:**
- **Lua Language Server** - Lua syntax highlighting and IntelliSense
- **LuaMobDebug** - Lua debugging support (required for debugging)
- **PLua Extension** (if available) - PLua-specific features
- **GitLens** - Git integration for version control

**QuickApp Project Scaffolding:**
```bash
# Create new QuickApp project with scaffolding
mkdir my-quickapp-project
cd my-quickapp-project

# Initialize QuickApp structure
plua --init-qa

# This creates:
# - main.lua (basic QuickApp template)
# - .vscode/ (VS Code configuration)
# - examples/ (example files)
# - README.md (project documentation)
```

**VS Code Debugging Configuration** (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Plua: Current Fibaro File",
      "type": "luaMobDebug",
      "request": "launch",
      "workingDirectory": "${workspaceFolder}",
      "sourceBasePath": "${workspaceFolder}",
      "listenPort": 8172,
      "stopOnEntry": false,
      "sourceEncoding": "UTF-8",
      "interpreter": "plua",
      "arguments": [
        "--fibaro",
        "--run-for",
        "60",
        "${relativeFile}"
      ],
      "listenPublicly": true
    }
  ]
}
```

**Basic VS Code settings** (`.vscode/settings.json`):
```json
{
    "lua.workspace.library": ["./plua/src"],
    "files.associations": {
        "*.lua": "lua",
        "*.fqa": "lua"
    },
    "lua.diagnostics.globals": [
        "QuickApp",
        "fibaro",
        "setTimeout",
        "setInterval",
        "clearTimeout",
        "clearInterval",
        "api",
        "json"
    ]
}
```

**How to Debug:**
1. **Install LuaMobDebug extension** in VS Code
2. **Open your QuickApp file** in VS Code
3. **Set breakpoints** by clicking in the gutter
4. **Press F5** or select "Plua: Current Fibaro File" from the debug menu
5. **Your QuickApp runs with debugging enabled** - execution stops at breakpoints

**Manual Project Setup (alternative):**
```bash
# Create basic file structure manually
mkdir my-quickapp-project
cd my-quickapp-project
touch main.lua
mkdir examples
mkdir tests
```

### 1.3 Development Environment

**PLua execution modes:**
```bash
# Interactive mode (REPL)
plua -i

# Script execution
plua my-quickapp.lua

# Fibaro mode with QuickApp support
plua --fibaro my-quickapp.lua

# Desktop window support
plua --fibaro my-quickapp.lua
# (Desktop windows open automatically if --%%desktop:true header is present)

# Run without debugger (for production testing)
plua --fibaro my-quickapp.lua --nodebugger

# Control execution time
plua --fibaro my-quickapp.lua --run-for 60  # Run for 60 seconds
plua --fibaro my-quickapp.lua --run-for 0   # Run indefinitely
```

**Development with PLua repository (developers only):**
```bash
# If working from cloned repository
./run.sh -i
./run.sh --fibaro my-quickapp.lua
```

---

## 2. Basic QuickApp Structure

### 2.1 Minimal QuickApp

**Simplest working QuickApp:**
```lua
--%%name:My First QuickApp
--%%type:com.fibaro.deviceController

function QuickApp:onInit()
    self:debug("QuickApp initialized!")
end
```

**What this does:**
- ✅ Creates a QuickApp named "My First QuickApp"
- ✅ Uses generic device controller type
- ✅ Logs initialization message

### 2.2 Essential Methods

**Core QuickApp lifecycle methods:**

```lua
--%%name:Essential Methods Demo
--%%type:com.fibaro.binarySwitch

function QuickApp:onInit()
    -- Called when QuickApp starts
    self:debug("QuickApp starting...")
    
    -- Initialize your variables
    self.isOn = false
    
    -- Set up timers or intervals
    setInterval(function()
        self:updateStatus()
    end, 30000)  -- Update every 30 seconds
end

function QuickApp:turnOn()
    -- Called when device is turned on
    self:debug("Turning on")
    self.isOn = true
    self:updateProperty("value", true)
end

function QuickApp:turnOff()
    -- Called when device is turned off
    self:debug("Turning off")
    self.isOn = false
    self:updateProperty("value", false)
end

function QuickApp:updateStatus()
    -- Custom method for periodic updates
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    self:updateProperty("log", "Last update: " .. timestamp)
end
```

### 2.3 Code Organization

**Recommended file structure:**
```lua
--%%name:Well Organized QuickApp
--%%type:com.fibaro.binarySwitch

-- ==============================
-- CONFIGURATION & CONSTANTS
-- ==============================
local UPDATE_INTERVAL = 30 * 1000  -- 30 seconds
local API_ENDPOINT = "https://api.example.com"

-- ==============================
-- HELPER FUNCTIONS
-- ==============================
local function formatTimestamp(time)
    return os.date("%Y-%m-%d %H:%M:%S", time)
end

local function validateInput(value)
    return value and type(value) == "string" and #value > 0
end

-- ==============================
-- QUICKAPP IMPLEMENTATION
-- ==============================
function QuickApp:onInit()
    self:debug("Initializing QuickApp...")
    self:setupTimers()
    self:loadConfiguration()
end

function QuickApp:setupTimers()
    setInterval(function()
        self:periodicUpdate()
    end, UPDATE_INTERVAL)
end

function QuickApp:loadConfiguration()
    -- Load settings from variables or properties
    self.apiKey = self:getVariable("apiKey") or ""
    self.pollingEnabled = self:getVariable("pollingEnabled") == "true"
end

-- Continue with other methods...
```

---

## 3. PLua Header Configuration

### 3.1 Header Syntax

**Basic header format:**
```lua
--%%<header_name>:<value>
```

**Rules:**
- ✅ Must start with `--%%` (Lua comment with special prefix)
- ✅ Header name followed by colon `:`
- ✅ Value can be string, number, boolean, or complex structure
- ✅ Headers must be at the top of the file
- ✅ Headers are processed before code execution

### 3.2 Device Configuration

**Essential device headers:**

```lua
--%%name:My Smart Device
--%%type:com.fibaro.binarySwitch
--%%manufacturer:MyCompany
--%%model:SmartSwitch v1.0
--%%description:A smart switch that can be controlled remotely
```

**Device types (common ones):**
```lua
--%%type:com.fibaro.binarySwitch        -- On/Off switch
--%%type:com.fibaro.binarySensor        -- Binary sensor
--%%type:com.fibaro.multilevelSensor    -- Multi-level sensor
--%%type:com.fibaro.multilevelSwitch    -- Dimmer/multi-level switch
--%%type:com.fibaro.doorSensor          -- Door/window sensor
--%%type:com.fibaro.motionSensor        -- Motion detector
--%%type:com.fibaro.temperatureSensor   -- Temperature sensor
--%%type:com.fibaro.humiditySensor      -- Humidity sensor
--%%type:com.fibaro.deviceController    -- Generic controller
```

### 3.3 Development Headers

**Debugging and development:**
```lua
--%%debug:true                    -- Enable debug mode
--%%desktop:true                  -- Open desktop window
--%%offline:true                  -- Run without HC3 connection
--%%breakonload:true              -- Debugger breakpoint on load
--%%save:my-quickapp-state.json   -- Save state to file
```

### 3.4 UI Definition Headers

**Define UI elements:**
```lua
--%%u:{label="status",text="Device Status: Ready"}
--%%u:{button="toggleBtn",text="Toggle",onReleased="toggleDevice"}
--%%u:{slider="brightness",text="Brightness",min="0",max="100",value="50",onChanged="setBrightness"}
--%%u:{switch="autoMode",text="Auto Mode",value="false",onToggled="toggleAutoMode"}
```

**Complex UI layout:**
```lua
--%%u:{{button="btn1",text="Option 1",onReleased="option1"},{button="btn2",text="Option 2",onReleased="option2"}}
--%%u:{select="mode",text="Mode",options={{type='option',text='Manual',value='manual'},{type='option',text='Auto',value='auto'}},onToggled="setMode"}
```

---

## 4. Complete Header Reference

### 4.1 Basic Headers

| Header | Type | Description | Example |
|--------|------|-------------|---------|
| `name` | string | QuickApp display name | `--%%name:My Device` |
| `type` | string | Device type identifier | `--%%type:com.fibaro.binarySwitch` |
| `manufacturer` | string | Device manufacturer | `--%%manufacturer:ACME Corp` |
| `model` | string | Device model name | `--%%model:SmartDevice v2.0` |
| `description` | string | Device description | `--%%description:Smart home controller` |
| `uid` | string | Unique device identifier | `--%%uid:device-12345` |
| `role` | string | Device role/category | `--%%role:lighting` |

### 4.2 Advanced Headers

| Header | Type | Description | Example |
|--------|------|-------------|---------|
| `interfaces` | array | Device interfaces | `--%%interfaces:{"battery","energy"}` |
| `var` | key=value | QuickApp variables | `--%%var:apiKey=abc123` |
| `file` | path,name | Include external files | `--%%file:./lib/utils.lua,utils` |
| `proxy` | boolean | Enable proxy mode | `--%%proxy:true` |
| `proxy_port` | number | Proxy server port | `--%%proxy_port:8080` |
| `proxyupdate` | string | Proxy update endpoint | `--%%proxyupdate:/api/update` |
| `time` | string | Scheduled execution time | `--%%time:06:30` |
| `latitude` | string | Device location latitude | `--%%latitude:52.2297` |
| `longitude` | string | Device location longitude | `--%%longitude:21.0122` |

### 4.3 Development & Debugging

| Header | Type | Description | Example |
|--------|------|-------------|---------|
| `debug` | boolean | Enable debug logging | `--%%debug:true` |
| `desktop` | boolean | Open desktop window | `--%%desktop:true` |
| `offline` | boolean | Run without HC3 | `--%%offline:true` |
| `breakonload` | boolean | Debugger breakpoint | `--%%breakonload:true` |
| `save` | string | State persistence file | `--%%save:state.json` |
| `project` | number | Project identifier | `--%%project:1001` |
| `qacolor` | string | Background color of QA window | `--%%qacolor:lightblue` |

---

## 5. Practical Examples

### 5.1 Simple Sensor QuickApp

**Temperature sensor with basic functionality:**

```lua
--%%name:Temperature Sensor
--%%type:com.fibaro.temperatureSensor
--%%manufacturer:DIY Sensors
--%%model:TempSense v1.0
--%%description:A simple temperature sensor
--%%var:updateInterval=60
--%%var:temperatureOffset=0
--%%debug:true
--%%desktop:true

function QuickApp:onInit()
    self:debug("Temperature Sensor initializing...")
    
    -- Configuration
    self.updateInterval = tonumber(self:getVariable("updateInterval")) * 1000 or 60000
    self.temperatureOffset = tonumber(self:getVariable("temperatureOffset")) or 0
    
    -- Start monitoring
    self:startTemperatureMonitoring()
    
    self:debug("Temperature Sensor ready!")
end

function QuickApp:startTemperatureMonitoring()
    setInterval(function()
        self:readTemperature()
    end, self.updateInterval)
end

function QuickApp:readTemperature()
    -- Simulate temperature reading (replace with actual sensor code)
    local baseTemp = 20 + math.random(-5, 5) + (math.sin(os.time() / 3600) * 3)
    local temperature = baseTemp + self.temperatureOffset
    
    self:updateProperty("value", temperature)
    self:debug("Temperature:", temperature, "°C")
end
```

### 5.2 Interactive UI QuickApp

**Device with buttons, sliders, and status display:**

```lua
--%%name:Smart Controller
--%%type:com.fibaro.deviceController
--%%manufacturer:SmartHome Co
--%%model:Controller Pro
--%%description:Advanced device controller with interactive UI
--%%desktop:true
--%%debug:true

-- UI Definition
--%%u:{label="statusLabel",text="Status: Ready"}
--%%u:{{button="powerBtn",text="Power On",onReleased="togglePower"},{button="resetBtn",text="Reset",onReleased="resetDevice"}}
--%%u:{slider="intensitySlider",text="Intensity",min="0",max="100",value="50",onChanged="setIntensity"}
--%%u:{switch="autoSwitch",text="Auto Mode",value="false",onToggled="toggleAutoMode"}
--%%u:{select="modeSelect",text="Mode",value="1",onToggled="selectMode",options={{type='option',text='Economy',value='1'},{type='option',text='Comfort',value='2'},{type='option',text='Boost',value='3'}}}

function QuickApp:onInit()
    self:debug("Smart Controller initializing...")
    
    -- Initialize state
    self.isPowered = false
    self.intensity = 50
    self.autoMode = false
    self.currentMode = 1
    
    self:updateStatusDisplay()
    self:debug("Smart Controller ready!")
end

function QuickApp:togglePower()
    self.isPowered = not self.isPowered
    local status = self.isPowered and "ON" or "OFF"
    
    self:updateView("powerBtn", "text", self.isPowered and "Power Off" or "Power On")
    self:updateProperty("value", self.isPowered)
    
    self:updateStatusDisplay()
    self:debug("Power:", status)
end

function QuickApp:resetDevice()
    self.isPowered = false
    self.intensity = 50
    self.autoMode = false
    self.currentMode = 1
    
    self:updateView("powerBtn", "text", "Power On")
    self:updateView("intensitySlider", "value", "50")
    self:updateView("autoSwitch", "value", "false")
    self:updateView("modeSelect", "value", "1")
    
    self:updateStatusDisplay()
    self:debug("Device reset")
end

function QuickApp:setIntensity(event)
    self.intensity = tonumber(event.values[1])
    self:updateView("intensitySlider", "value", tostring(self.intensity))
    
    self:updateStatusDisplay()
    self:debug("Intensity set to:", self.intensity)
end

function QuickApp:toggleAutoMode(event)
    self.autoMode = event.values[1] == "true"
    
    self:updateStatusDisplay()
    self:debug("Auto mode:", self.autoMode and "ON" or "OFF")
end

function QuickApp:selectMode(event)
    self.currentMode = tonumber(event.values[1])
    local modes = {"Economy", "Comfort", "Boost"}
    
    self:updateStatusDisplay()
    self:debug("Mode selected:", modes[self.currentMode])
end

function QuickApp:updateStatusDisplay()
    local powerStatus = self.isPowered and "ON" or "OFF"
    local modeNames = {"Economy", "Comfort", "Boost"}
    local autoStatus = self.autoMode and " (Auto)" or ""
    
    local status = string.format("Power: %s | Mode: %s%s | Intensity: %d%%", 
        powerStatus, modeNames[self.currentMode], autoStatus, self.intensity)
    
    self:updateView("statusLabel", "text", status)
end
```

### 5.3 Advanced Configuration

**Production-ready QuickApp with comprehensive headers:**

```lua
--%%name:Advanced Home Automation Hub
--%%type:com.fibaro.deviceController
--%%manufacturer:HomeAuto Solutions
--%%model:Hub Pro Max v2.1
--%%description:Comprehensive home automation controller with advanced features
--%%uid:hub-pro-max-001
--%%role:controller
--%%latitude:52.2297
--%%longitude:21.0122

-- Configuration variables
--%%var:apiEndpoint=https://api.homeauto.com
--%%var:apiKey=your-secret-key-here
--%%var:updateInterval=30
--%%var:debugMode=true
--%%var:maxRetries=3

-- External dependencies
--%%file:./lib/http-client.lua,httpClient
--%%file:./lib/device-manager.lua,deviceManager

-- Development settings
--%%debug:true
--%%desktop:true
--%%save:hub-state.json
--%%project:2024

-- Interfaces
--%%interfaces:{"battery","energy","zwaveplus"}

-- Complex UI Layout
--%%u:{label="hubStatus",text="Hub Status: Initializing..."}
--%%u:{{button="syncBtn",text="Sync Devices",onReleased="syncDevices"},{button="configBtn",text="Configure",onReleased="openConfig"}}
--%%u:{slider="masterVolume",text="Master Volume",min="0",max="100",value="70",onChanged="setMasterVolume"}
--%%u:{select="homeMode",text="Home Mode",value="home",onToggled="setHomeMode",options={{type='option',text='Home',value='home'},{type='option',text='Away',value='away'},{type='option',text='Sleep',value='sleep'},{type='option',text='Vacation',value='vacation'}}}
--%%u:{switch="securityArmed",text="Security System",value="false",onToggled="toggleSecurity"}

function QuickApp:onInit()
    self:debug("Advanced Home Automation Hub initializing...")
    
    -- Load configuration
    self:loadConfiguration()
    
    -- Initialize subsystems
    self:initializeDeviceManager()
    self:initializeNetworking()
    self:startMonitoring()
    
    -- Update UI
    self:updateHubStatus("Ready")
    
    self:debug("Hub initialization complete!")
end

function QuickApp:loadConfiguration()
    self.config = {
        apiEndpoint = self:getVariable("apiEndpoint"),
        apiKey = self:getVariable("apiKey"),
        updateInterval = tonumber(self:getVariable("updateInterval")) * 1000 or 30000,
        debugMode = self:getVariable("debugMode") == "true",
        maxRetries = tonumber(self:getVariable("maxRetries")) or 3
    }
    
    if self.config.debugMode then
        self:debug("Configuration loaded:", json.encode(self.config))
    end
end

-- Additional methods would continue here...
```

---

## 6. Best Practices

### 6.1 Code Structure

**✅ Recommended patterns:**

```lua
-- Clear header section at top
--%%name:My Device
--%%type:com.fibaro.binarySwitch

-- Constants and configuration
local CONFIG = {
    UPDATE_INTERVAL = 30000,
    MAX_RETRIES = 3,
    API_BASE = "https://api.example.com"
}

-- Helper functions before QuickApp methods
local function validateInput(value)
    return value and type(value) == "string"
end

-- QuickApp methods in logical order
function QuickApp:onInit()
    -- Initialization logic
end

function QuickApp:customMethod()
    -- Custom functionality
end
```

**❌ Avoid:**
```lua
-- Mixed headers throughout file
function QuickApp:onInit()
--%%name:Bad Practice  -- Headers should be at top
    self:debug("This is confusing")
end
```

### 6.2 Header Organization

**✅ Logical header order:**
```lua
-- 1. Basic device information
--%%name:Device Name
--%%type:device.type
--%%manufacturer:Company
--%%model:Model Name

-- 2. Configuration variables
--%%var:setting1=value1
--%%var:setting2=value2

-- 3. UI definitions
--%%u:{label="status",text="Ready"}
--%%u:{button="action",text="Action",onReleased="doAction"}

-- 4. Development settings (at end)
--%%debug:true
--%%desktop:true
```

### 6.3 Testing & Debugging

**VS Code Debugging (Recommended):**
```bash
# 1. Install LuaMobDebug VS Code extension
# 2. Set breakpoints in your Lua code
# 3. Press F5 to start debugging
# 4. QuickApp runs with full debugging support
```

**Command Line Development:**
```bash
# 1. Development with debug output
plua --fibaro my-device.lua --debug

# 2. Desktop testing with UI (automatic if --%%desktop:true header present)
plua --fibaro my-device.lua

# 3. Offline testing without HC3
plua my-device.lua --offline

# 4. Production simulation
plua --fibaro my-device.lua --nodebugger

# 5. Time-controlled execution
plua --fibaro my-device.lua --run-for 30  # Run for 30 seconds

# 6. Interactive mode for testing
plua -i
```

**Debug best practices:**
```lua
function QuickApp:onInit()
    -- Use debug levels appropriately
    self:debug("Debug: Detailed troubleshooting info")
    self:trace("Trace: Very detailed execution flow")
    self:warning("Warning: Something unexpected happened")
    self:error("Error: Something went wrong")
end

-- Use breakpoint header for automatic debugging
--%%breakonload:true

function QuickApp:myMethod()
    -- Execution will pause here when debugging
    local value = self:calculateSomething()
    self:debug("Calculated value:", value)
end
```

---

## 🎯 Summary

This guide provides everything you need to develop QuickApps in Lua using PLua:

**Key Components:**
✅ **Header Configuration** - Properly configure device properties and behavior  
✅ **Code Structure** - Organize your Lua code for maintainability  
✅ **UI Definition** - Create interactive interfaces with header-defined UI elements  
✅ **Development Workflow** - Test and debug effectively with PLua tools  

**Next Steps:**
1. **Start Simple** - Begin with basic sensor or switch QuickApps
2. **Add UI Elements** - Enhance with buttons, sliders, and displays
3. **External Integration** - Connect to APIs and external services
4. **Advanced Features** - Implement child devices and complex logic

**Remember:** Headers control how PLua configures and runs your QuickApp, while the Lua code defines the behavior and logic.

*Happy QuickApp Development! 🚀*