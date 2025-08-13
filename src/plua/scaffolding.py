"""
Project scaffolding utilities for plua
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any
from .path_utils import get_static_file


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
    launch_config = get_vscode_launch_config()
    
    if launch_json_path.exists():
        print(f"  Updating {launch_json_path}")
    else:
        print(f"  Creating {launch_json_path}")
    
    with open(launch_json_path, 'w') as f:
        json.dump(launch_config, f, indent=4)
    
    # Create tasks.json for HC3 upload/download
    tasks_json_path = vscode_dir / "tasks.json"
    tasks_config = get_vscode_tasks_config()
    
    if tasks_json_path.exists():
        print(f"  Updating {tasks_json_path}")
    else:
        print(f"  Creating {tasks_json_path}")
    
    with open(tasks_json_path, 'w') as f:
        json.dump(tasks_config, f, indent=4)
    
    # Create .project file for HC3 project configuration
    project_file_path = project_dir / ".project"
    project_config = get_project_config()
    
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
        main_lua_content = get_basic_quickapp_template()
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
            main_lua_content = get_basic_quickapp_template()
    
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
    config_path = get_static_file('vscode_launch_config.json')
    with open(config_path, 'r') as f:
        config_content = f.read()
    return json.loads(config_content)


def get_vscode_tasks_config() -> Dict[str, Any]:
    """Get VS Code tasks configuration for HC3 integration"""
    config_path = get_static_file('vscode_tasks_config.json')
    with open(config_path, 'r') as f:
        config_content = f.read()
    return json.loads(config_content)


def get_basic_quickapp_template() -> str:
    """Get the basic QuickApp template content"""
    template_path = get_static_file('basic_quickapp_template.lua')
    with open(template_path, 'r') as f:
        return f.read()


def get_project_config() -> str:
    """Get the .project file configuration for HC3"""
    config_path = get_static_file('project_config.json')
    with open(config_path, 'r') as f:
        return f.read()
