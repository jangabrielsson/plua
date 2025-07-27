# VSCode Integration for plua

This guide covers how to set up and use Visual Studio Code with plua for an optimal development experience, including debugging, task automation, and QuickApp development workflows.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Debug Configuration](#debug-configuration)
- [Task Configuration](#task-configuration)
- [QuickApp Development Workflow](#quickapp-development-workflow)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before setting up VSCode integration, ensure you have:

1. **plua installed**: `pip install plua`
2. **VSCode**: Latest version of Visual Studio Code
3. **Lua extension**: Install a Lua language extension (e.g., "Lua" by sumneko)
4. **MobDebug extension** (optional): For advanced debugging features

## Initial Setup

### 1. Create VSCode Configuration Directory

In your plua project root, create a `.vscode` directory if it doesn't exist:

```bash
mkdir -p .vscode
```

### 2. Configure Workspace Settings

Create `.vscode/settings.json` with plua-specific settings:

```json
{
    "files.associations": {
        "*.lua": "lua",
        "*.fqa": "lua"
    },
    "lua.workspace.checkThirdParty": false,
    "terminal.integrated.shell.windows": "cmd.exe"
}
```

## Debug Configuration

### Launch Configuration

Create `.vscode/launch.json` with the following debug configurations:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "plua: Run Current Lua File with Debugger", 
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

### Debug Configuration Explained

- **plua: Run Current Lua File with Debugger**: Runs the currently open Lua file with debugging support
- **plua: Run Current Fibaro File with Debugger**: Runs the file with Fibaro HC3 emulation and debugging

### Using the Debugger

1. Open a Lua file in VSCode
2. Set breakpoints by clicking in the gutter
3. Press `F5` or go to Run > Start Debugging
4. Select the appropriate debug configuration
5. The debugger will stop at breakpoints and allow inspection of variables

## Task Configuration

### Core Tasks Setup

Create `.vscode/tasks.json` with automation tasks for plua development:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Plua: Close All QuickApp Windows",
      "type": "shell",
      "group": "build",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "presentation": {
        "echo": false,
        "close": false,
        "reveal": "silent",
        "revealProblems": "never",
        "focus": false,
        "panel": "shared",
        "clear": false,
        "showReuseMessage": false
      },
      "problemMatcher": [],
      "windows": {
        "command": "cmd",
        "args": [
          "/c",
          "if exist \"${workspaceFolder}\\.venv\\Scripts\\python.exe\" (\"${workspaceFolder}\\.venv\\Scripts\\python.exe\" -m plua --close-windows) else (python -m plua --close-windows)"
        ]
      },
      "osx": {
        "command": "bash",
        "args": [
          "-c",
          "if [ -f '${workspaceFolder}/.venv/bin/python' ]; then '${workspaceFolder}/.venv/bin/python' -m plua --close-windows; else python -m plua --close-windows; fi"
        ]
      },
      "linux": {
        "command": "bash",
        "args": [
          "-c",
          "if [ -f '${workspaceFolder}/.venv/bin/python' ]; then '${workspaceFolder}/.venv/bin/python' -m plua --close-windows; else python -m plua --close-windows; fi"
        ]
      }
    },
    {
      "label": "Plua, upload current file as QA to HC3",
      "type": "shell",
      "command": "plua",
      "args": [
        "--fibaro",
        "-a",
        "uploadQA",
        "${relativeFile}"
      ],
      "group": "build"
    },
    {
      "label": "Plua, update single file (part of .project)",
      "type": "shell",
      "command": "plua",
      "args": [
        "--fibaro",
        "-a",
        "updateFile",
        "${relativeFile}"
      ],
      "group": "build"
    },
    {
      "label": "Plua, update QA (defined in .project)",
      "type": "shell",
      "command": "plua",
      "args": [
        "--fibaro",
        "updateQA",
        "-a",
        "${relativeFile}"
      ],
      "group": "build"
    },
    {
      "label": "Plua, Download and unpack from HC3",
      "type": "shell",
      "command": "plua",
      "args": [
        "--fibaro",
        "-a",
        "downloadQA ${input:QA_id:${input:path_id}",
        "dummy.lua"
      ],
      "group": "build"
    }
  ],
  "inputs": [
    {
      "type": "promptString",
      "id": "QA_id",
      "description": "deviceId of QA from HC3 you want to download?",
      "default": "-"
    },
    {
      "type": "promptString",
      "id": "path_id",
      "description": "path where to store the QA",
      "default": "dev"
    },
    {
      "type": "promptString",
      "id": "QA_name",
      "description": "'.' for open file, or QA path name",
      "default": "."
    },
    {
      "id": "pickEnvFile",
      "type": "command",
      "command": "launch-file-picker.pick",
      "args": {
        "options": {
          "title": "pick env file",
          "path": ".",
          "filterExt": ".env"
        },
        "output": {
          "defaultPath": "client/env/dev.env"
        }
      }
    },
    {
      "type": "pickString",
      "id": "versionBumpType",
      "description": "Select version bump type",
      "options": [
        "patch",
        "minor",
        "major"
      ],
      "default": "patch"
    },
    {
      "type": "promptString",
      "id": "customVersion",
      "description": "Enter custom version (e.g., 1.2.3) or leave empty for auto-bump"
    },
    {
      "type": "promptString",
      "id": "releaseNotes",
      "description": "Enter release notes for this version"
    }
  ]
}
```

### Task Descriptions

#### Window Management
- **Plua: Close All QuickApp Windows**: Closes all open QuickApp desktop windows. Useful for cleaning up development sessions.

#### Fibaro HC3 Integration
- **Plua, upload current file as QA to HC3**: Uploads the currently open file as a new QuickApp to your HC3 system
- **Plua, update single file (part of .project)**: Updates a single file that's part of a multi-file QuickApp project
- **Plua, update QA (defined in .project)**: Updates an entire QuickApp based on project configuration
- **Plua, Download and unpack from HC3**: Downloads a QuickApp from HC3 and unpacks it to your local filesystem

### Running Tasks

1. **Command Palette**: Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
2. Type "Tasks: Run Task"
3. Select the desired task from the list
4. For HC3 tasks, you'll be prompted for required parameters

**Keyboard Shortcuts**: You can also use `Ctrl+Shift+P` then type the task name directly.

## QuickApp Development Workflow

### 1. Setting Up a QuickApp Project

```bash
# Create project directory
mkdir my-quickapp
cd my-quickapp

# Initialize with plua
plua --init-quickapp

# Open in VSCode
code .
```
It will prompt for QuickApp type and provide a template for that type.

### 2. Project Structure

```
my-quickapp/
├── .vscode/
│   ├── launch.json
│   └── tasks.json
├── .project          # QuickApp configuration
└── myquickapp.lua    # Main QuickApp code
```

### 3. Development Cycle

1. **Write Code**: Edit your Lua files with syntax highlighting and IntelliSense
2. **Test Locally**: Use `F5` to run with debugging
3. **Upload to HC3**: Use "Plua, upload current file as QA to HC3" task (or updateFile/updateQA)
4. **Iterate**: Make changes and use "Plua, update QA" task for quick updates
5. **Clean Up**: Use "Plua: Close All QuickApp Windows" when done

### 4. Desktop Window Development

QuickApps that have defined --%%desktop:true will automatically open a window with the QuickApp UI when running. The window will be left open after the run terminates and re-used when re-running.
Keeping the windows opened between runs is for efficiency and minimizing the startup time.

Use the "Close All QuickApp Windows" task to clean up during development.

### 5. Fibaro HC3 Configuration

Create a `.env` file for HC3 connection settings:

```bash
HC3_IP=192.168.1.100
HC3_USER=admin
HC3_PASSWORD=your_password
```

## Troubleshooting

### Common Issues

#### 1. Tasks Not Working
- **Issue**: Tasks fail to run or can't find `plua`
- **Solution**: Ensure `plua` is in your PATH or use absolute paths in task configuration
- **Virtual Environment**: The tasks automatically detect and use virtual environments

#### 2. Debugger Not Connecting
- **Issue**: Debug session starts but doesn't stop at breakpoints
- **Solution**: 
  - Ensure the MobDebug extension is installed
  - Check that port 8172 is not blocked by firewall
  - Verify the source path mappings in launch.json

#### 3. QuickApp Windows Not Closing
- **Issue**: Desktop windows remain open after development
- **Solution**: 
  - Run the "Close All QuickApp Windows" task
  - Manually close via command: `plua --close-windows`
  - Windows should automatically reuse across VSCode sessions

#### 4. HC3 Connection Issues
- **Issue**: Cannot upload/download QuickApps
- **Solution**:
  - Verify HC3 IP address and credentials in `.env`
  - Ensure network connectivity to HC3
  - Check HC3 API is enabled

### Environment Variables

You can set these in your `.env` file:

```bash
# HC3 Connection
HC3_IP=192.168.1.100
HC3_USER=admin
HC3_PASSWORD=password

# Development Settings
PLUA_DEBUG=1
PLUA_API_PORT=8888

# Desktop Window Settings
PLUA_WINDOW_PERSIST=1
```

### Performance Tips

1. **Use Virtual Environments**: Speeds up task execution
2. **Close Unused Windows**: Use the close task regularly
3. **Enable Window Reuse**: Desktop windows automatically reuse across sessions
4. **Batch Updates**: Use project-based updates for multi-file QuickApps

## Advanced Configuration

### Custom Task Example

Add custom tasks for your specific workflow:

```json
{
  "label": "My Custom Plua Task",
  "type": "shell",
  "command": "plua",
  "args": [
    "--fibaro",
    "--api-port", "9000",
    "${file}"
  ],
  "group": "build",
  "presentation": {
    "echo": true,
    "reveal": "always",
    "focus": false,
    "panel": "shared"
  }
}
```

### Keybinding Setup

Add to `.vscode/keybindings.json`:

```json
[
  {
    "key": "ctrl+f5",
    "command": "workbench.action.tasks.runTask",
    "args": "Plua: Close All QuickApp Windows"
  },
  {
    "key": "ctrl+shift+u",
    "command": "workbench.action.tasks.runTask", 
    "args": "Plua, upload current file as QA to HC3"
  }
]
```

---

This comprehensive setup provides a seamless development experience for plua and Fibaro QuickApp development within Visual Studio Code. The configuration handles cross-platform compatibility and automatically detects virtual environments for optimal performance.
