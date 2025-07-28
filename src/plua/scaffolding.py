"""
Project scaffolding utilities for plua
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any


def init_quickapp_project() -> None:
    """Initialize a new QuickApp project with .vscode config, .project file, and starter Lua file"""
    
    # Get current directory
    project_dir = Path.cwd()
    vscode_dir = project_dir / ".vscode"
    
    print(f"Initializing QuickApp project in: {project_dir}")
    
    # QuickApp templates available on GitHub
    templates = {
        "basic": {
            "name": "Basic QuickApp",
            "description": "Simple starter template with button callback",
            "content": None  # Will use built-in template
        },
        "alarmPartition": {
            "name": "Alarm Partition",
            "description": "Security system partition controller",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/alarmPartition.lua"
        },
        "binarySensor": {
            "name": "Binary Sensor", 
            "description": "Sensor reporting true/false state",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/binarySensor.lua"
        },
        "binarySwitch": {
            "name": "Binary Switch",
            "description": "On/Off switch with turnOn/turnOff actions",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/binarySwitch.lua"
        },
        "coDetector": {
            "name": "CO Detector",
            "description": "Carbon monoxide detector sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/coDetector.lua"
        },
        "colorController": {
            "name": "Color Controller", 
            "description": "RGB/HSV color control device",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/colorController.lua"
        },
        "deviceController": {
            "name": "Device Controller",
            "description": "Generic device controller interface",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/deviceController.lua"
        },
        "doorSensor": {
            "name": "Door Sensor",
            "description": "Door/window open/close sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/doorSensor.lua"
        },
        "energyMeter": {
            "name": "Energy Meter",
            "description": "Power and energy consumption meter",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/energyMeter.lua"
        },
        "fireDetector": {
            "name": "Fire Detector",
            "description": "Fire/smoke detector sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/fireDetector.lua"
        },
        "floodSensor": {
            "name": "Flood Sensor",
            "description": "Water flood detection sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/floodSensor.lua"
        },
        "genericDevice": {
            "name": "Generic Device",
            "description": "Basic device template",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/genericDevice.lua"
        },
        "heatDetector": {
            "name": "Heat Detector",
            "description": "Heat detection sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/heatDetector.lua"
        },
        "humiditySensor": {
            "name": "Humidity Sensor",
            "description": "Humidity level sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/humiditySensor.lua"
        },
        "hvacSystemAuto": {
            "name": "HVAC System Auto",
            "description": "Auto HVAC system controller",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/hvacSystemAuto.lua"
        },
        "hvacSystemCool": {
            "name": "HVAC System Cool",
            "description": "Cooling HVAC system controller",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/hvacSystemCool.lua"
        },
        "hvacSystemHeat": {
            "name": "HVAC System Heat",
            "description": "Heating HVAC system controller",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/hvacSystemHeat.lua"
        },
        "hvacSystemHeatCool": {
            "name": "HVAC System Heat/Cool",
            "description": "Full HVAC system with heating and cooling",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/hvacSystemHeatCool.lua"
        },
        "lightSensor": {
            "name": "Light Sensor",
            "description": "Ambient light level sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/lightSensor.lua"
        },
        "motionSensor": {
            "name": "Motion Sensor",
            "description": "PIR motion detector sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/motionSensor.lua"
        },
        "multilevelSensor": {
            "name": "Multilevel Sensor",
            "description": "Generic sensor with numeric values",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/multilevelSensor.lua"
        },
        "multilevelSwitch": {
            "name": "Multilevel Switch",
            "description": "Dimmer/level control with setValue action",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/multilevelSwitch.lua"
        },
        "player": {
            "name": "Player",
            "description": "Media player control device",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/player.lua"
        },
        "powerMeter": {
            "name": "Power Meter",
            "description": "Electrical power consumption meter",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/powerMeter.lua"
        },
        "rainDetector": {
            "name": "Rain Detector",
            "description": "Rain detection sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/rainDetector.lua"
        },
        "rainSensor": {
            "name": "Rain Sensor",
            "description": "Rain measurement sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/rainSensor.lua"
        },
        "remoteController": {
            "name": "Remote Controller",
            "description": "Remote control device interface",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/remoteController.lua"
        },
        "smokeSensor": {
            "name": "Smoke Sensor",
            "description": "Smoke detection sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/smokeSensor.lua"
        },
        "temperatureSensor": {
            "name": "Temperature Sensor",
            "description": "Temperature measurement sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/temperatureSensor.lua"
        },
        "thermostat": {
            "name": "Thermostat",
            "description": "Basic thermostat controller",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/thermostat.lua"
        },
        "thermostatCool": {
            "name": "Thermostat Cool",
            "description": "Cooling-only thermostat",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/thermostatCool.lua"
        },
        "thermostatHeat": {
            "name": "Thermostat Heat",
            "description": "Heating-only thermostat",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/thermostatHeat.lua"
        },
        "thermostatHeatCool": {
            "name": "Thermostat Heat/Cool",
            "description": "Full thermostat with heating and cooling",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/thermostatHeatCool.lua"
        },
        "thermostatSetpoint": {
            "name": "Thermostat Setpoint",
            "description": "Thermostat setpoint controller",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/thermostatSetpoint.lua"
        },
        "thermostatSetpointCool": {
            "name": "Thermostat Setpoint Cool",
            "description": "Cooling setpoint controller",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/thermostatSetpointCool.lua"
        },
        "thermostatSetpointHeat": {
            "name": "Thermostat Setpoint Heat",
            "description": "Heating setpoint controller",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/thermostatSetpointHeat.lua"
        },
        "thermostatSetpointHeatCool": {
            "name": "Thermostat Setpoint Heat/Cool",
            "description": "Dual setpoint controller for heating/cooling",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/thermostatSetpointHeatCool.lua"
        },
        "waterLeakSensor": {
            "name": "Water Leak Sensor",
            "description": "Water leak detection sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/waterLeakSensor.lua"
        },
        "weather": {
            "name": "Weather",
            "description": "Weather station device",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/weather.lua"
        },
        "windSensor": {
            "name": "Wind Sensor",
            "description": "Wind speed/direction sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/windSensor.lua"
        },
        "windowCovering": {
            "name": "Window Covering",
            "description": "Blinds/shades with open/close/stop",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/windowCovering.lua"
        },
        "windowSensor": {
            "name": "Window Sensor",
            "description": "Window open/close sensor",
            "url": "https://raw.githubusercontent.com/jangabrielsson/plua/main/examples/fibaro/stdQAs/windowSensor.lua"
        }
    }
    
    # Present template menu
    print("\nAvailable QuickApp templates:")
    template_keys = list(templates.keys())
    for i, key in enumerate(template_keys, 1):
        template = templates[key]
        print(f"[{i}] {template['name']} - {template['description']}")
    
    print(f"\nChoose template (1-{len(template_keys)}) or press Enter for basic template: ", end="", flush=True)
    
    try:
        choice = input().strip()
        if not choice:
            selected_key = "basic"
        else:
            choice_num = int(choice)
            if 1 <= choice_num <= len(template_keys):
                selected_key = template_keys[choice_num - 1]
            else:
                print(f"Invalid choice. Using basic template.")
                selected_key = "basic"
    except (ValueError, KeyboardInterrupt):
        print("\nUsing basic template.")
        selected_key = "basic"
    
    selected_template = templates[selected_key]
    print(f"Selected: {selected_template['name']}")
    
    # Create .vscode directory if it doesn't exist
    vscode_dir.mkdir(exist_ok=True)
    
    # Create launch.json for VS Code debugging
    launch_json_path = vscode_dir / "launch.json"
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Run plua with current file",
                "type": "python",
                "request": "launch",
                "module": "plua",
                "args": ["--fibaro", "-i", "${file}"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {
                    "PYTHONPATH": "${workspaceFolder}"
                }
            },
            {
                "name": "Run plua interactive",
                "type": "python", 
                "request": "launch",
                "module": "plua",
                "args": ["--fibaro", "-i"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            }
        ]
    }
    
    if launch_json_path.exists():
        print(f"  Updating {launch_json_path}")
    else:
        print(f"  Creating {launch_json_path}")
    
    with open(launch_json_path, 'w') as f:
        json.dump(launch_config, f, indent=4)
    
    # Create tasks.json for HC3 upload/download
    tasks_json_path = vscode_dir / "tasks.json"
    tasks_config = {
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
    
    if tasks_json_path.exists():
        print(f"  Updating {tasks_json_path}")
    else:
        print(f"  Creating {tasks_json_path}")
    
    with open(tasks_json_path, 'w') as f:
        json.dump(tasks_config, f, indent=4)
    
    # Create .project file for HC3 project configuration
    project_file_path = project_dir / ".project"
    project_config = '''{
  "name": "My QuickApp",
  "id": 0,
  "type": "com.fibaro.quickApp",
  "properties": {
    "deviceIcon": 0,
    "viewLayout": {"$jason": {"body": {"header": {"title": "quickApp_device_812"},"sections": {"items": [{"components": [{"name": "button","text": "Hello","type": "button"}],"type": "vertical"}]}}}},
    "uiCallbacks": ["main.lua"]
  },
  "apiVersion": "1.2",
  "initialProperties": {},
  "initialInterfaces": [],
  "files": [
    {
      "name": "main",
      "type": "lua",
      "isMain": true,
      "isOpen": true,
      "content": "main.lua"
    }
  ]
}'''
    
    if project_file_path.exists():
        print(f"  Project file already exists: {project_file_path}")
    else:
        print(f"  Creating {project_file_path}")
        with open(project_file_path, 'w') as f:
            f.write(project_config)
    
    # Create main.lua starter file
    main_lua_path = project_dir / "main.lua"
    
    # Get template content
    if selected_key == "basic" or "url" not in selected_template:
        # Use built-in basic template
        main_lua_content = '''--%%name:My QuickApp
--%%type:com.fibaro.quickApp
--%%description:A starter QuickApp template

function QuickApp:onInit()
    self:debug("QuickApp started:", self.name, self.id)
    
    -- Initialize UI callback
    self:updateProperty("log", "QuickApp initialized at " .. os.date("%c"))
    
    -- Example: Set up a timer for periodic updates
    fibaro.setTimeout(5000, function()
        self:updateProperty("log", "Timer update at " .. os.date("%c"))
    end)
end

function QuickApp:button(event)
    self:debug("Button pressed!")
    self:updateProperty("log", "Button pressed at " .. os.date("%c"))
    
    -- Example: Toggle a property or call an API
    local currentValue = self:getVariable("counter") or "0"
    local newValue = tostring(tonumber(currentValue) + 1)
    self:setVariable("counter", newValue)
    self:updateProperty("log", "Button count: " .. newValue)
end

-- Add more QuickApp methods here as needed
-- function QuickApp:turnOn()
-- function QuickApp:turnOff()
-- function QuickApp:setValue(value)
'''
    else:
        # Fetch template from GitHub
        print(f"  Fetching {selected_template['name']} template from GitHub...")
        try:
            with urllib.request.urlopen(selected_template['url']) as response:
                main_lua_content = response.read().decode('utf-8')
            print(f"  ✓ Template downloaded successfully")
        except urllib.error.URLError as e:
            print(f"  ✗ Failed to fetch template: {e}")
            print(f"  Falling back to basic template")
            main_lua_content = '''--%%name:My QuickApp
--%%type:com.fibaro.quickApp
--%%description:A starter QuickApp template

function QuickApp:onInit()
    self:debug("QuickApp started:", self.name, self.id)
    
    -- Initialize UI callback
    self:updateProperty("log", "QuickApp initialized at " .. os.date("%c"))
    
    -- Example: Set up a timer for periodic updates
    fibaro.setTimeout(5000, function()
        self:updateProperty("log", "Timer update at " .. os.date("%c"))
    end)
end

function QuickApp:button(event)
    self:debug("Button pressed!")
    self:updateProperty("log", "Button pressed at " .. os.date("%c"))
    
    -- Example: Toggle a property or call an API
    local currentValue = self:getVariable("counter") or "0"
    local newValue = tostring(tonumber(currentValue) + 1)
    self:setVariable("counter", newValue)
    self:updateProperty("log", "Button count: " .. newValue)
end

-- Add more QuickApp methods here as needed
-- function QuickApp:turnOn()
-- function QuickApp:turnOff()
-- function QuickApp:setValue(value)
'''
    
    if main_lua_path.exists():
        print(f"  Lua file already exists: {main_lua_path}")
    else:
        print(f"  Creating {main_lua_path}")
        with open(main_lua_path, 'w') as f:
            f.write(main_lua_content)
    
    print(f"\nQuickApp project initialized successfully with {selected_template['name']} template!")
    print("\nNext steps:")
    print("1. Open this folder in VS Code")
    print("2. Edit main.lua with your QuickApp logic")
    print("3. Use F5 to run/debug with plua (includes --fibaro flag)")
    print("4. Use Ctrl+Shift+P -> 'Tasks: Run Task' -> 'QA, upload current file as QA to HC3' to upload to HC3")
    print("5. Configure HC3 connection in your environment or .env file")
    print("\nTip: Always use 'plua --fibaro main.lua' for QuickApp development")


def get_vscode_launch_config() -> Dict[str, Any]:
    """Get VS Code launch configuration for plua projects"""
    return {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Run plua with current file",
                "type": "python",
                "request": "launch",
                "module": "plua",
                "args": ["--fibaro", "-i", "${file}"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {
                    "PYTHONPATH": "${workspaceFolder}"
                }
            },
            {
                "name": "Run plua interactive",
                "type": "python", 
                "request": "launch",
                "module": "plua",
                "args": ["--fibaro", "-i"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            }
        ]
    }


def get_vscode_tasks_config() -> Dict[str, Any]:
    """Get VS Code tasks configuration for HC3 integration"""
    return {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "QA, upload current file as QA to HC3",
                "type": "shell",
                "command": "lua",
                "args": [
                    "-e",
                    "\"require('hc3emu2')\"",
                    "uploadQA",
                    "${relativeFile}"
                ],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                }
            },
            {
                "label": "QA, update single file (part of .project)",
                "type": "shell",
                "command": "lua",
                "args": [
                    "-e",
                    "\"require('hc3emu2')\"",
                    "updateFile",
                    "${relativeFile}"
                ],
                "group": "build"
            },
            {
                "label": "QA, update QA (defined in .project)",
                "type": "shell",
                "command": "lua",
                "args": [
                    "-e",
                    "\"require('hc3emu2')\"",
                    "updateQA",
                    "${relativeFile}"
                ],
                "group": "build"
            }
        ]
    }


def get_basic_quickapp_template() -> str:
    """Get the basic QuickApp template content"""
    return '''--%%name:My QuickApp
--%%type:com.fibaro.quickApp
--%%description:A starter QuickApp template

function QuickApp:onInit()
    self:debug("QuickApp started:", self.name, self.id)
    
    -- Initialize UI callback
    self:updateProperty("log", "QuickApp initialized at " .. os.date("%c"))
    
    -- Example: Set up a timer for periodic updates
    fibaro.setTimeout(5000, function()
        self:updateProperty("log", "Timer update at " .. os.date("%c"))
    end)
end

function QuickApp:button(event)
    self:debug("Button pressed!")
    self:updateProperty("log", "Button pressed at " .. os.date("%c"))
    
    -- Example: Toggle a property or call an API
    local currentValue = self:getVariable("counter") or "0"
    local newValue = tostring(tonumber(currentValue) + 1)
    self:setVariable("counter", newValue)
    self:updateProperty("log", "Button count: " .. newValue)
end

-- Add more QuickApp methods here as needed
-- function QuickApp:turnOn()
-- function QuickApp:turnOff()
-- function QuickApp:setValue(value)
'''


def get_project_config() -> str:
    """Get the .project file configuration for HC3"""
    return '''{
  "name": "My QuickApp",
  "id": 0,
  "type": "com.fibaro.quickApp",
  "properties": {
    "deviceIcon": 0,
    "viewLayout": {"$jason": {"body": {"header": {"title": "quickApp_device_812"},"sections": {"items": [{"components": [{"name": "button","text": "Hello","type": "button"}],"type": "vertical"}]}}}},
    "uiCallbacks": ["main.lua"]
  },
  "apiVersion": "1.2",
  "initialProperties": {},
  "initialInterfaces": [],
  "files": [
    {
      "name": "main",
      "type": "lua",
      "isMain": true,
      "isOpen": true,
      "content": "main.lua"
    }
  ]
}'''
