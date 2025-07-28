# QuickApp Development Quick Start Guide

This guide covers everything you need to know to quickly start developing Fibaro HC3 QuickApps with plua.

## Table of Contents

- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Project Scaffolding](#project-scaffolding)
- [VS Code Integration](#vs-code-integration)
- [QuickApp Headers](#quickapp-headers)
- [Desktop UI Development](#desktop-ui-development)
- [HC3 Proxy Development](#hc3-proxy-development)
- [Saving and Managing Versions](#saving-and-managing-versions)
- [HC3 Integration Tasks](#hc3-integration-tasks)
- [Quick Reference](#quick-reference)

## Installation

Install plua globally to get the `plua` command:

```bash
# Install plua
pip install plua

# Verify installation
plua --version
```

For troubleshooting installation issues, see the [main README installation section](../../README.md#installation).

## Environment Setup

### Create .env File for HC3 Connection

Create a `.env` file in your home directory for global HC3 access:

```bash
# Create global .env file
cat > ~/.env << EOF
HC3_URL=https://192.168.1.100
HC3_USER=admin
HC3_PASSWORD=your_password_here
EOF
```

**Alternative:** Create project-specific `.env` files in your project directories.

Example `.env` contents:
```env
# Fibaro HC3 Connection Settings
HC3_URL=https://192.168.1.100
HC3_USER=admin
HC3_PASSWORD=mySecretPassword123

# Optional: Development settings
DEBUG=true
LOG_LEVEL=info
```

## Project Scaffolding

### Initialize a New QuickApp Project

```bash
# Create and navigate to your project directory
mkdir my-quickapp && cd my-quickapp

# Initialize QuickApp project with scaffolding
plua --init-quickapp
```

This command:
- Creates `.vscode/launch.json` with debugging configurations
- Creates `.vscode/tasks.json` with HC3 upload/download tasks
- Creates `.project` file for HC3 project metadata
- Creates `main.lua` with a starter QuickApp template
- Offers 40+ specialized templates (sensors, switches, thermostats, etc.)

### Template Selection

Choose from available templates:
- **Basic QuickApp** - Simple starter with button callback
- **Binary Switch** - On/Off switch with turnOn/turnOff actions
- **Multilevel Switch** - Dimmer with setValue action
- **Temperature Sensor** - Temperature measurement device
- **Motion Sensor** - PIR motion detector
- **And 35+ more specialized device types**

## VS Code Integration

### Launch Configurations

The scaffolding creates a launch configurations in `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "plua: Run Current Fibaro File with Debugger", 
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
                "--fibaro",
                "${file}"
            ]
        }
    ]
}
```

### Running Your QuickApp

1. **Open project in VS Code**: `code .`
2. **Open main.lua**
3. **Press F5** to run with debugger
4. **Or use Ctrl+F5** to run without debugger

The launch config automatically:
- Loads Fibaro API support (`--fibaro`)
- Runs your current file
- Enters interactive mode (`-i`) for testing

## QuickApp Headers

QuickApp files use special header comments to control behavior and HC3 integration:

### Essential Headers

```lua
--%%name:My QuickApp
--%%type:com.fibaro.binarySwitch
```

### UI and Development Headers

```lua
--%%desktop:true                     -- Enable desktop UI window
--%%proxy:true                       -- Start HC3 proxy on device
--%%save:MyQuickApp_v1.0             -- Save .fqa version
--%%interfaces:["battery","energy"]  -- Device capabilities
--%%var:counter=0.                   -- QuickApp variables
--%%u:....
```

## Desktop UI Development

### Enable Desktop UI

Add the desktop header to your QuickApp:

```lua
--%%desktop:true

function QuickApp:onInit()
    self:debug("QuickApp with desktop UI started")
    self:updateView("labal1","text","Hello")
end
```

### Running with Desktop UI

```bash
# Run QuickApp with desktop UI
plua --fibaro main.lua

# Or force desktop UI via command line
plua --desktop --fibaro main.lua
```

This opens a native desktop window showing your QuickApp's UI for rapid development and testing.

### Closing Desktop Windows

VSCode will leave QA UI windows open when the run terminates and reuse them on next run. To close all QA UI windows, run plua --close-windows.
```bash
# Close all QuickApp windows
plua --close-windows

# Close specific QuickApp window
plua --close-qa-window 812

# Clean up window registry
plua --cleanup-registry
```

## HC3 Proxy Development

### Enable HC3 Proxy

The proxy allows real-time development against your actual HC3 device:

```lua
--%%proxy:true

function QuickApp:onInit()
    self:debug("Proxy QuickApp started")
    -- This runs a proxy , on the HC3
end

function QuickApp:turnOn()
    self:debug("Turning on via proxy")
    self:updateProperty("value", true)
    -- Property updates are sent to real HC3 too
end
```

### Proxy Benefits

- **Real-time sync**: Property changes sync with actual HC3 device
- **Live debugging**: Debug running QuickApp on HC3
- **Device interactions**: Control real Z-Wave/Zigbee devices
- **Scene integration**: Trigger real scenes and automations

## Saving and Managing Versions

### Save QuickApp Versions

Use the save header to create versioned `.fqa` files:

```lua
--%%save:MyQuickApp_v1.0
--%%name:My QuickApp
--%%type:com.fibaro.binarySwitch

function QuickApp:onInit()
    self:debug("QuickApp v1.0 started")
end
```

When you run this QuickApp, plua automatically saves a complete `.fqa` file that can be uploaded directly to HC3.

The `.fqa` files contain:
- Complete QuickApp code
- UI layout definitions
- Device properties and interfaces
- QuickApp variables
- Ready for HC3 upload

## HC3 Integration Tasks

### VS Code Tasks

The scaffolding creates tasks in `.vscode/tasks.json` for HC3 integration:
To use the update QA and update single file, you need to set --%%project:ID
where the ID is the device on the HC3 that should be updated.

#### Upload Current File as New QuickApp

```bash
# Use Ctrl+Shift+P -> "Tasks: Run Task" -> "Plua, upload current file as QA to HC3"
# Or use terminal:
plua --fibaro -a uploadQA main.lua
```

#### Update Single File (Part of Project)

```bash
# Use task: "Plua, update single file (part of .project)"
plua --fibaro -a updateFile main.lua
```

#### Update Existing QuickApp

```bash
# Use task: "Plua, update QA (defined in .project)"
plua --fibaro updateQA -a main.lua
```

#### Download QuickApp from HC3

```bash
# Use task: "Plua, Download and unpack from HC3"
# This will prompt for device ID and path
plua --fibaro -a "downloadQA ${deviceId}:${path}" dummy.lua
```

#### Close All QuickApp Windows

```bash
# Use task: "Plua: Close All QuickApp Windows"
plua --close-windows
```

### Task Prerequisites

These tasks are built into plua and require:
- Valid `.env` file with HC3 credentials
- Network access to your HC3 device
- Proper authentication credentials

## Quick Reference

### Essential Commands

```bash
# Create new project
plua --init-quickapp

# Run QuickApp with Fibaro API
plua --fibaro main.lua

# Run with desktop UI
plua --desktop --fibaro main.lua

# Run in interactive mode
plua --fibaro -i main.lua

# Close all desktop windows
plua --close-windows
```

### Key Headers

```lua
--%%name:Device Name              -- Required: Device name
--%%type:com.fibaro.quickApp      -- Required: Device type
--%%desktop:true                  -- Enable desktop UI
--%%proxy:true                    -- Enable HC3 proxy
--%%save:FileName                 -- Save .fqa version
--%%id:123                        -- Specific device ID
```

### Development Workflow

1. **Setup**: Install plua, create `.env`, run `--init-quickapp`
2. **Develop**: Edit `main.lua`, add headers, implement QuickApp methods
3. **Test**: Press F5 in VS Code or use `plua --fibaro main.lua`
4. **Debug**: Use `--desktop:true` for UI testing
5. **Deploy**: Use VS Code tasks to upload to HC3

### File Structure

```
my-quickapp/
├── .vscode/
│   ├── launch.json          # VS Code debugging config
│   └── tasks.json           # HC3 integration tasks
├── .project                 # HC3 project metadata
├── main.lua                 # Your QuickApp code
└── .env                     # HC3 credentials (optional)
```

### Next Steps

- **Learn QuickApp API**: See [QuickApp Documentation](QuickApp.md)
- **Explore Fibaro API**: See [Fibaro API Documentation](Fibaro.md)
- **Advanced UI**: See [QuickApp Emulator Documentation](EmulatorQA.md)
- **VS Code Integration**: See [VS Code Integration Guide](VSCodeintegration.md)

## Common Issues

### Command Not Found
```bash
# If plua command not found
python -m plua --version
```

### Connection Issues
```bash
# Test HC3 connection
plua --fibaro -e "print(api.get('/info'))"
```

### UI Not Opening
```bash
# Install required dependencies
pip install pywebview
```

### Task Failures
```bash
# Ensure hc3emu2 is installed
luarocks install hc3emu2
```

This guide provides everything needed to start developing QuickApps with plua efficiently. For detailed API documentation, refer to the comprehensive guides linked above.
