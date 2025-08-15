# VS Code Setup Guide for PLua

This guide will help you set up VS Code for optimal PLua development, including debugging, tasks, and Fibaro QuickApp development workflow.

## 📋 Prerequisites

Before setting up VS Code, ensure you have:
- **VS Code** installed ([download here](https://code.visualstudio.com/))
- **PLua** installed (`pip install plua`)
- **Python 3.8+** with pip
- **Git** (for version control)

## 🔧 Initial Setup

### 1. Install Required Extensions

Install these VS Code extensions for the best PLua development experience:

```**3. Debugging Problems**
- Use `luaMobDebug` type for Lua debugging
- Ensure Lua MobDebug adapter extension is installed and active
- Check that port 8172 is available
- Restart VS Code if debugger connection fails
# Essential extensions for Lua development
code --install-extension sumneko.lua
code --install-extension ms-python.python
code --install-extension alexeymelnichuk.lua-mobdebug

# Optional but recommended
code --install-extension ms-vscode.live-server  # For QuickApp UI preview
code --install-extension ms-vscode.hexeditor    # For binary file inspection
```

Or install via VS Code Extensions panel:
- **Lua** (sumneko.lua) - Lua language server with IntelliSense
- **Python** (ms-python.python) - Python support for PLua internals
- **Lua MobDebug adapter** (alexeymelnichuk.lua-mobdebug) - Lua debugging with luaMobDebug by Alexey Melnichuk
- **Live Server** (ms-vscode.live-server) - For QuickApp UI development

### 2. Configure Workspace Settings

Create or update `.vscode/settings.json` in your project:

```json
{
    "lua.diagnostics.globals": [
        "fibaro", "QuickApp", "plugin", "api", "json", "net", "setTimeout", "clearTimeout",
        "setInterval", "clearInterval", "class", "hc3_emulator", "__TAG", "DEBUG"
    ],
    "lua.workspace.library": ["./lua"],
    "lua.completion.callSnippet": "Replace",
    "lua.completion.keywordSnippet": "Replace",
    "files.associations": {
        "*.fqa": "lua",
        "*.hc3": "lua"
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/.git": true,
        "**/.DS_Store": true,
        "**/node_modules": true
    }
}
```

## 🚀 Launch Configuration (launch.json)

The launch configuration enables F5 debugging in VS Code using luaMobDebug for proper Lua debugging support.

### Complete Launch Configuration

Create or update `.vscode/launch.json` in your project:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "PLua: Current File",
            "type": "luaMobDebug",
            "request": "launch",
            "workingDirectory": "${workspaceFolder}",
            "sourceBasePath": "${workspaceFolder}",
            "listenPort": 8172,
            "stopOnEntry": false,
            "sourceEncoding": "UTF-8",
            "interpreter": "plua",
            "arguments": [
                "${relativeFile}"
            ],
            "listenPublicly": true
        },
        {
            "name": "PLua: Current File with Fibaro SDK",
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

### Development Environment Configuration

If you're working with the PLua source code (using `./run.sh`):

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "PLua Dev: Current File",
            "type": "luaMobDebug",
            "request": "launch",
            "workingDirectory": "${workspaceFolder}",
            "sourceBasePath": "${workspaceFolder}",
            "listenPort": 8172,
            "stopOnEntry": false,
            "sourceEncoding": "UTF-8",
            "interpreter": "./run.sh",
            "arguments": [
                "${relativeFile}"
            ],
            "listenPublicly": true
        },
        {
            "name": "PLua Dev: Current Fibaro File",
            "type": "luaMobDebug",
            "request": "launch",
            "workingDirectory": "${workspaceFolder}",
            "sourceBasePath": "${workspaceFolder}",
            "listenPort": 8172,
            "stopOnEntry": false,
            "sourceEncoding": "UTF-8",
            "interpreter": "./run.sh",
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

### 🔧 Troubleshooting Launch Issues

**Common Problems:**

1. **"luaMobDebug extension not found"**
   ```bash
   # Install the Lua MobDebug adapter extension
   code --install-extension alexeymelnichuk.lua-mobdebug
   ```

2. **"Debugger connection failed"**
   - Ensure port 8172 is not in use by another process
   - Check that `listenPublicly: true` is set in launch config
   - Try restarting VS Code

3. **"plua command not found"**
   ```bash
   # Check PLua installation
   pip list | grep plua
   which plua
   
   # Use full path if needed
   "interpreter": "/usr/local/bin/plua"
   ```

4. **Breakpoints not working**
   - Ensure you're using `luaMobDebug` type (not `debugpy`)
   - Check that the Lua MobDebug adapter extension is active
   - Verify source paths match your project structure

5. **Path issues in development mode**
   - Use `./run.sh` for development setups
   - Use `plua` for pip-installed versions
   - Ensure working directory is correct

## 📋 Tasks Configuration (tasks.json)

Tasks enable easy HC3 QuickApp management. Create `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
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
                "downloadQA ${input:QA_id}:${input:path_id}",
                "dummy.lua"
            ],
            "group": "build"
        },
        {
            "label": "PLua: Run Current File",
            "type": "shell",
            "command": "plua",
            "args": ["${relativeFile}"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "PLua: Run with Fibaro SDK",
            "type": "shell",
            "command": "plua", 
            "args": ["${relativeFile}", "--fibaro"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "PLua: Start Interactive REPL",
            "type": "shell",
            "command": "plua",
            "args": ["-i"],
            "group": "build", 
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": true,
                "panel": "shared"
            },
            "problemMatcher": []
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
        }
    ]
}
```

## 🎯 Usage Workflow

### 1. Running Scripts

**Method 1: F5 Debugging**
1. Open your `.lua` file
2. Press `F5` 
3. Select appropriate launch configuration
4. Script runs with debugging support

**Method 2: Command Palette Tasks**
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type "Tasks: Run Task"
3. Select a PLua task (e.g., "PLua: Run with Fibaro SDK")

**Method 3: Terminal**
```bash
# Use integrated terminal (Ctrl+` or Cmd+`)
plua script.lua --fibaro
```

### 2. QuickApp Development Workflow

**Development Cycle:**
1. **Create/Edit** your QuickApp Lua file
2. **Test Locally** with F5 → "PLua: Current File with Fibaro SDK" 
3. **Upload to HC3** with Task → "Plua, upload current file as QA to HC3"
4. **Iterate** - repeat steps 1-3

**Project Structure:**
```
my-quickapp/
├── .vscode/
│   ├── launch.json
│   ├── tasks.json  
│   └── settings.json
├── .project          # HC3 deployment config
├── main.lua          # QuickApp main file
├── utils.lua         # Optional utility functions
└── README.md         # Project documentation
```

### 3. Debugging Tips

**Breakpoints:**
- Set breakpoints by clicking in the gutter next to line numbers
- Use conditional breakpoints (right-click breakpoint → Edit Breakpoint)
- Inspect variables in the Debug Console

**Watch Variables:**
- Add variables to the Watch panel during debugging
- Use Debug Console for immediate evaluation: `fibaro.debug("test")`

**Call Stack:**
- View the call stack in the Debug panel
- Navigate between stack frames to inspect different scopes

## 🔍 Advanced Configuration

### Custom Snippets

Create Lua snippets for common PLua patterns. In VS Code:
1. `Ctrl+Shift+P` → "Preferences: Configure User Snippets"
2. Select "lua.json"
3. Add PLua-specific snippets:

```json
{
    "QuickApp onInit": {
        "prefix": "qainit",
        "body": [
            "function QuickApp:onInit()",
            "    self:debug(\"${1:QuickApp} started\")",
            "    $0",
            "end"
        ],
        "description": "QuickApp onInit method"
    },
    "Fibaro setTimeout": {
        "prefix": "timeout", 
        "body": [
            "setTimeout(${1:5000}, function()",
            "    $0",
            "end)"
        ],
        "description": "Fibaro setTimeout"
    },
    "Update View": {
        "prefix": "updateview",
        "body": [
            "self:updateView(\"${1:elementId}\", \"${2:property}\", \"${3:value}\")"
        ],
        "description": "Update QuickApp UI element"
    }
}
```

### Workspace Templates

Create a workspace template for new PLua projects:

**File: `.vscode/plua-project.code-workspace`**
```json
{
    "folders": [
        {
            "path": "."
        }
    ],
    "settings": {
        "lua.diagnostics.globals": [
            "fibaro", "QuickApp", "plugin", "api", "json", "net", 
            "setTimeout", "clearTimeout", "setInterval", "clearInterval"
        ],
        "files.associations": {
            "*.fqa": "lua"
        }
    },
    "extensions": {
        "recommendations": [
            "sumneko.lua",
            "ms-python.python"
        ]
    }
}
```

### Git Integration

Configure `.gitignore` for PLua projects:

```gitignore
# Python
__pycache__/
*.pyc
.venv/

# PLua
*.log
.project

# VS Code
.vscode/settings.json

# OS
.DS_Store
Thumbs.db
```

## 🚀 Quick Start Checklist

For a new PLua project in VS Code:

- [ ] Install PLua: `pip install plua`
- [ ] Install VS Code extensions (Lua, Python)
- [ ] Create project folder and open in VS Code
- [ ] Initialize QuickApp: `plua --init-qa`
- [ ] Copy appropriate `launch.json` configuration
- [ ] Copy `tasks.json` for HC3 integration
- [ ] Configure `settings.json` for Lua globals
- [ ] Test with F5 debugging
- [ ] Set up `.project` file for HC3 deployment

## 🆘 Troubleshooting

### Common Issues

**1. "plua command not found"**
```bash
# Check installation
pip list | grep plua
which plua

# Reinstall if needed
pip install --upgrade plua
```

**2. Lua Language Server Issues**
- Ensure Lua extension is installed and enabled
- Check that `lua.diagnostics.globals` includes Fibaro globals
- Restart VS Code if IntelliSense stops working

**3. Tasks Not Working**
- Ensure `hc3emu2` is available in your Lua environment
- Check that `.project` file exists for HC3 tasks
- Verify HC3 connection settings

**4. Debugging Problems**
- Always use `--nodebugger` in launch configurations
- Check Python interpreter path in status bar
- Ensure virtual environment is activated (if using one)

### Getting Help

- **PLua Issues**: [GitHub Issues](https://github.com/jangabrielsson/plua/issues)
- **VS Code Lua**: [Lua Extension Documentation](https://marketplace.visualstudio.com/items?itemName=sumneko.lua)
- **General VS Code**: [VS Code Documentation](https://code.visualstudio.com/docs)

---

**Happy coding with PLua in VS Code! 🎉**