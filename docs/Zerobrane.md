# ZeroBrane Studio Setup Guide for PLua

ZeroBrane Studio is a lightweight Lua IDE that provides excellent support for PLua development, including debugging, project management, and QuickApp development. This guide shows how to integrate PLua with ZeroBrane Studio for an optimal Lua development experience.

## 📋 Prerequisites

Before setting up ZeroBrane Studio with PLua:
- **ZeroBrane Studio** installed ([download here](https://studio.zerobrane.com/))
- **PLua** installed (`pip install plua`) or development setup

## 🔧 Initial Setup

### 1. Install ZeroBrane Studio

Download and install ZeroBrane Studio from [studio.zerobrane.com](https://studio.zerobrane.com/). ZeroBrane Studio includes the MobDebug library needed for debugging PLua scripts.

### 2. Configure PLua Path

Open ZeroBrane Studio and go to **Edit → Preferences → Settings: User**. Add PLua configuration:

```lua
--[[--
  PLua configuration for ZeroBrane Studio
  Use this file to specify PLua interpreter paths.
--]]--

-- For development setup (using ./run.sh)
path.lua54 = "/path/to/plua/run.sh"

-- For global PLua installation (uncomment to use)
-- path.lua54 = "/usr/local/bin/plua"  -- macOS/Linux
-- path.lua54 = "plua"                 -- Windows or if plua is in PATH
```

**Example configurations:**

```lua
-- Development setup example
path.lua54 = "/Users/jangabrielsson/Documents/dev/plua/run.sh"

-- Global installation example  
-- path.lua54 = "plua"
```

## 🚀 Running PLua Scripts

### Basic Lua Scripts

1. **Open** your `.lua` file in ZeroBrane Studio
2. **Press F5** to run the script
3. **Output** appears in the Output panel

Example script:
```lua
print("Hello from PLua!")
local timer = require("timer")
timer.setTimeout(1000, function()
    print("Timer executed!")
end)
```

### QuickApp Development

ZeroBrane Studio automatically detects QuickApp patterns and runs with Fibaro SDK:

```lua
--%%name:Temperature Sensor
--%%type:com.fibaro.temperatureSensor
--%%u:{label="temp", text="--°C"}

function QuickApp:onInit()
    self:debug("Temperature sensor started")
    self:updateView("temp", "text", "22.5°C")
    
    -- Set up temperature simulation
    fibaro.setInterval(5000, function()
        local temp = math.random(180, 250) / 10
        self:updateView("temp", "text", temp .. "°C")
        self:updateProperty("value", temp)
    end)
end
```

## 🐛 Debugging

### Enable Debugging

ZeroBrane Studio provides excellent debugging support for PLua:

1. **Set Breakpoints**: Click in the margin next to line numbers
2. **Start Debugging**: Press **F5** 
3. **Debug Controls**:
   - **F10**: Step Over
   - **F11**: Step Into  
   - **Shift+F11**: Step Out
   - **F5**: Continue

### Debug Features

- **Variable Watch**: Inspect variables in the Watch panel
- **Call Stack**: View function call hierarchy
- **Local Variables**: See local scope variables
- **Immediate Window**: Execute Lua commands during debugging

## 📱 Project Setup

### Create PLua Project

```bash
# Create project directory
mkdir my-quickapp
cd my-quickapp

# Initialize QuickApp
# Development setup:
/path/to/plua/run.sh --init-qa

# Global installation:
plua --init-qa
```

### Open in ZeroBrane Studio

1. **File → Open Directory** and select your project folder
2. **Project → Project Directory → Set From Current File**
3. Files appear in the Project panel for easy navigation

### Project Structure

```
my-quickapp/
├── .zbstudio/           # ZeroBrane Studio settings
├── .project            # HC3 deployment config  
├── main.lua            # QuickApp main file
├── utils.lua           # Utility functions
└── README.md           # Documentation
```

## 🎯 Development Workflow

### 1. Edit and Test Cycle

1. **Edit** your Lua/QuickApp code in ZeroBrane Studio
2. **Run/Debug** with F5 (automatically uses PLua + Fibaro SDK for QuickApps)
3. **Check Output** in the Output panel
4. **Iterate** quickly with syntax highlighting and code completion

### 2. QuickApp Features

- **Auto-detection**: ZeroBrane detects QuickApp headers (`--%%`) automatically
- **Desktop UI**: QuickApp windows open automatically (if `--%%desktop:true`)
- **Real-time Updates**: UI updates work during debugging sessions
- **Fibaro API**: Full access to fibaro.* functions

### 3. Advanced Debugging

```lua
-- Add breakpoint debugging to your QuickApp
function QuickApp:onInit()
    self:debug("Starting temperature sensor")  -- Set breakpoint here
    
    local initialTemp = 20.0  -- Inspect this variable
    self:updateView("temp", "text", initialTemp .. "°C")
    
    -- Debug timer callbacks
    fibaro.setInterval(5000, function()
        local temp = self:calculateTemperature()  -- Step into this function
        self:updateTemperatureDisplay(temp)
    end)
end

function QuickApp:calculateTemperature()
    return math.random(180, 250) / 10  -- Set breakpoint to inspect math.random
end
```

## 🔧 Advanced Configuration

### Code Completion Setup

To enable better code completion for PLua/Fibaro APIs, create a custom API file:

1. Go to ZeroBrane Studio installation directory
2. Navigate to `api/` folder
3. Create `plua.lua`:

```lua
-- PLua API definitions for code completion
return {
  fibaro = {
    type = "lib",
    description = "Fibaro Home Center API",
    childs = {
      debug = {
        type = "function",
        description = "Print debug message", 
        args = "(message)",
        returns = "nil"
      },
      call = {
        type = "function",
        description = "Call device action",
        args = "(deviceId, actionName, ...)",
        returns = "result"
      },
      getValue = {
        type = "function",
        description = "Get device property value",
        args = "(deviceId, propertyName)",
        returns = "value"
      },
      setInterval = {
        type = "function",
        description = "Set recurring timer",
        args = "(interval, callback)",
        returns = "timerId"
      },
      setTimeout = {
        type = "function", 
        description = "Set one-time timer",
        args = "(delay, callback)",
        returns = "timerId"
      }
    }
  },
  QuickApp = {
    type = "class",
    description = "Fibaro QuickApp base class",
    childs = {
      onInit = {
        type = "method",
        description = "QuickApp initialization",
        args = "(self)",
        returns = "nil"
      },
      debug = {
        type = "method",
        description = "Print debug message",
        args = "(self, message)",
        returns = "nil"
      },
      updateView = {
        type = "method",
        description = "Update UI element", 
        args = "(self, elementId, property, value)",
        returns = "nil"
      }
    }
  }
}
```

### Custom Interpreter (Advanced)

For more control, create a custom interpreter in ZeroBrane's `interpreters/` folder:

```lua
-- interpreters/plua.lua
local plua = {
  name = "PLua",
  description = "PLua interpreter with Fibaro support",
  api = {"baselib", "plua", "fibaro"},
  frun = function(self,wfilename,rundebug)
    local filepath = wfilename:GetFullPath()
    local cmd = self.path
    
    -- Auto-detect QuickApp and add --fibaro flag
    local file = io.open(filepath, "r")
    if file then
      local content = file:read("*all")
      file:close()
      if content:match("QuickApp") or content:match("fibaro") or content:match("--%%") then
        cmd = cmd .. " --fibaro"
      end
    end
    
    cmd = cmd .. " " .. filepath
    return CommandLineRun(cmd, self:fworkdir(wfilename), true, false)
  end,
  hasdebugger = true,
  fattachdebug = function(self) require('mobdebug').start() end,
}
return plua
```

## 🔍 Troubleshooting

### Common Issues

**1. PLua not found**
```bash
# Check installation
which plua  # For global install
ls -la /path/to/plua/run.sh  # For development setup

# Update ZeroBrane configuration
path.lua54 = "/correct/path/to/plua"
```

**2. Debugging not working**
- Ensure MobDebug is installed with ZeroBrane Studio
- Check that PLua supports debugging
- Verify interpreter path is correct

**3. QuickApp features not working**
- Ensure QuickApp headers are present (`--%%name:`, etc.)
- Check that PLua detects QuickApp patterns
- Verify Fibaro SDK is loaded (look for fibaro API in output)

**4. File associations**
```lua
-- In ZeroBrane preferences, associate .fqa files with Lua
fileformats = {
  fqa = "lua",  -- Fibaro QuickApp files
  hc3 = "lua",  -- Home Center 3 files
}
```

## 📚 Quick Reference

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **F5** | Run/Debug current file |
| **F9** | Toggle breakpoint |
| **F10** | Step over |
| **F11** | Step into |
| **Shift+F11** | Step out |
| **Ctrl+F5** | Run without debugging |
| **Ctrl+Shift+F** | Find in project |
| **Ctrl+G** | Go to line |

### PLua Commands

```bash
# Development setup
./run.sh script.lua                    # Basic script
./run.sh --fibaro quickapp.lua         # QuickApp
./run.sh -i                           # Interactive REPL

# Global installation  
plua script.lua                       # Basic script
plua --fibaro quickapp.lua            # QuickApp
plua -i                              # Interactive REPL
```

### ZeroBrane Features for PLua

- **Syntax Highlighting**: Full Lua syntax support
- **Code Folding**: Collapse functions and blocks
- **Auto-completion**: PLua and Fibaro API suggestions
- **Project Management**: File tree and project-wide search
- **Integrated Debugging**: Breakpoints, watches, call stack
- **Output Panel**: See PLua output and error messages

## 🎮 Tips and Best Practices

### 1. Project Organization
- Keep QuickApps in separate folders
- Use descriptive file names (`temperature-sensor.lua`, `motion-detector.lua`)
- Document your QuickApp headers clearly

### 2. Debugging Workflow
- Set breakpoints at key functions (`onInit`, button handlers)
- Use variable watches for device IDs and states
- Step through timer callbacks to debug timing issues

### 3. Code Quality
- Use ZeroBrane's syntax checking
- Leverage code completion for Fibaro APIs
- Keep functions small and testable

### 4. Development Speed
- Use code templates for common patterns
- Keep multiple QuickApp files open in tabs
- Use project-wide search for finding API usage

---

**Happy PLua development with ZeroBrane Studio! 🚀**