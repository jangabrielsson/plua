"""
Main entry point for plua application
"""

import asyncio
import argparse
import sys
import os
import signal
import atexit
from typing import Optional
import lupa

from .runtime import LuaAsyncRuntime
from .repl import run_repl


def cleanup_on_exit():
    """Cleanup function called on process termination"""
    try:
        from .luafuns_lib import close_all_quickapp_windows
        from .desktop_ui import shutdown_desktop_ui
        
        print("\nCleaning up on exit...")
        
        # Close QuickApp windows
        result = close_all_quickapp_windows()
        if result.get('closed_count', 0) > 0:
            print(f"Closed {result['closed_count']} QuickApp windows")
            
        # Shutdown desktop UI manager
        shutdown_desktop_ui()
        
        # Force close any remaining Python processes that might be hanging
        try:
            import psutil
            import os
            current_pid = os.getpid()
            current_process = psutil.Process(current_pid)
            
            # Get all child processes
            children = current_process.children(recursive=True)
            for child in children:
                try:
                    child.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
            # Wait a moment for graceful termination
            import time
            time.sleep(0.2)
            
            # Force kill any remaining children
            for child in children:
                try:
                    if child.is_running():
                        child.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except ImportError:
            # psutil not available, skip process cleanup
            pass
        except Exception:
            # Any other error in process cleanup, ignore
            pass
            
    except Exception as e:
        # Don't print errors during shutdown unless debugging
        pass


def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down...")
        # Force cleanup of mobdebug and desktop processes
        force_cleanup_all()
        sys.exit(0)
    
    # Register signal handlers for common termination signals
    signals_to_handle = []
    
    # SIGTERM - standard termination signal (used by VS Code, Docker, etc.)
    if hasattr(signal, 'SIGTERM'):
        signals_to_handle.append(signal.SIGTERM)
    
    # SIGINT - interrupt signal (Ctrl+C) - though we also handle KeyboardInterrupt
    if hasattr(signal, 'SIGINT'):
        signals_to_handle.append(signal.SIGINT)
    
    # SIGHUP - hangup signal (terminal disconnection)
    if hasattr(signal, 'SIGHUP'):
        signals_to_handle.append(signal.SIGHUP)
    
    # SIGBREAK - Windows specific break signal (Ctrl+Break)
    if hasattr(signal, 'SIGBREAK'):
        signals_to_handle.append(signal.SIGBREAK)
    
    # Register handlers for available signals
    for sig in signals_to_handle:
        try:
            signal.signal(sig, signal_handler)
        except (OSError, ValueError):
            # Some signals may not be available on all platforms
            pass
    
    # Also register atexit handler as final fallback
    atexit.register(cleanup_on_exit)


def force_cleanup_all():
    """Force cleanup of all resources when terminating"""
    try:
        from .luafuns_lib import close_all_quickapp_windows
        from .desktop_ui import shutdown_desktop_ui
        
        print("Force cleaning up all resources...")
        
        # 1. Try to close QuickApp windows gracefully
        try:
            result = close_all_quickapp_windows()
            if result.get('closed_count', 0) > 0:
                print(f"Closed {result['closed_count']} QuickApp windows")
        except Exception:
            pass
            
        # 2. Shutdown desktop UI
        try:
            shutdown_desktop_ui()
        except Exception:
            pass
            
        # 3. Kill any hanging Python processes
        try:
            import subprocess
            import sys
            
            if sys.platform.startswith('win'):
                # Windows: Kill all python processes from this process tree
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(os.getpid())], 
                             capture_output=True, timeout=2)
            else:
                # Unix: Send SIGKILL to process group
                os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)
        except Exception:
            pass
            
    except Exception:
        # Final fallback - just exit
        pass


def init_quickapp_project() -> None:
    """Initialize a new QuickApp project with .vscode config, .project file, and starter Lua file"""
    from pathlib import Path
    import json
    import urllib.request
    import urllib.error
    
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


def show_greeting() -> None:
    """Display greeting with plua and Lua versions"""
    from . import __version__

    # Get Lua version efficiently
    try:
        lua = lupa.LuaRuntime()
        lua_version = lua.eval('_VERSION')
    except Exception:
        lua_version = "Lua (version unknown)"

    print(f"Plua v{__version__} with {lua_version}")


async def run_interactive(
    runtime=None,
    script_fragments: list = None,
    main_script: str = None,
    main_file: str = None,
    duration: Optional[int] = None,
) -> None:
    """
    Run script content first (if any), then enter interactive REPL
    """
    # Name the main task
    current_task = asyncio.current_task()
    if current_task:
        current_task.set_name("interactive_runtime")

    if runtime is None:
        from .runtime import LuaAsyncRuntime
        runtime = LuaAsyncRuntime()

    api_task = None
    api_server = None

    api_config = runtime.config.get('api_config')
    debug = runtime.config.get('debug', False)
    debugger_config = runtime.config.get('debugger_config')
    source_name = runtime.config.get('source_name')

    if api_config:
        from .api_server import PlUA2APIServer
        print(f"API server on {api_config['host']}:{api_config['port']}")
        print(f"WebUI on http://127.0.0.1:{api_config['port']}/web")
        api_server = PlUA2APIServer(runtime, api_config['host'], api_config['port'])

        def broadcast_view_hook(qa_id, component_name, property_name, data_json):
            if api_server:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(api_server.broadcast_view_update(qa_id, component_name, property_name, data_json))
                except Exception as e:
                    print(f"Error creating view broadcast task for QA {qa_id}: {e}")

        runtime.interpreter.set_broadcast_view_update_hook(broadcast_view_hook)
        api_task = asyncio.create_task(api_server.start_server(), name="api_server")

    try:
        # First, execute any script content if provided
        has_script_content = bool(script_fragments or main_script or main_file)
        if has_script_content:
            print("Executing script content...")
            await runtime.start_script_only(
                script_fragments=script_fragments,
                main_script=main_script,
                main_file=main_file,
                debugger_config=debugger_config,
                source_name=source_name,
                debug=debug,
                api_server=api_server
            )
            print("Script execution completed. Entering interactive mode...")
        else:
            # Initialize runtime for REPL only
            await runtime.initialize(
                debugger_config=debugger_config,
                debug=debug,
                api_server=api_server
            )

        # Now enter interactive REPL
        from .repl import PluaREPL
        repl = PluaREPL(runtime)
        await repl.start()

    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
    except Exception as e:
        print(f"Runtime error: {e}")
    finally:
        if api_server:
            try:
                await api_server.stop()
            except Exception:
                pass
        if api_task and not api_task.done():
            api_task.cancel()
            try:
                await asyncio.gather(api_task, return_exceptions=True)
            except Exception:
                pass


async def run_script(
    runtime=None,
    script_fragments: list = None,
    main_script: str = None,
    main_file: str = None,
    duration: Optional[int] = None,
) -> None:
    """
    Run Lua script fragments and main script with the async runtime, optionally with REST API server
    """
    # Name the main task
    current_task = asyncio.current_task()
    if current_task:
        current_task.set_name("main_runtime")

    if runtime is None:
        from .runtime import LuaAsyncRuntime
        runtime = LuaAsyncRuntime()
    api_task = None
    api_server = None

    api_config = runtime.config.get('api_config')
    debug = runtime.config.get('debug', False)
    debugger_config = runtime.config.get('debugger_config')
    source_name = runtime.config.get('source_name')
    if api_config:
        from .api_server import PlUA2APIServer
        print(f"API server on {api_config['host']}:{api_config['port']}")
        print(f"WebUI on http://127.0.0.1:{api_config['port']}/web")
        api_server = PlUA2APIServer(runtime, api_config['host'], api_config['port'])

        def broadcast_view_hook(qa_id, component_name, property_name, data_json):
            if api_server:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(api_server.broadcast_view_update(qa_id, component_name, property_name, data_json))
                except Exception as e:
                    print(f"Error creating view broadcast task for QA {qa_id}: {e}")

        runtime.interpreter.set_broadcast_view_update_hook(broadcast_view_hook)
        api_task = asyncio.create_task(api_server.start_server(), name="api_server")

    try:
        await runtime.start(
            script_fragments=script_fragments,
            main_script=main_script,
            main_file=main_file,
            duration=duration,
            debugger_config=debugger_config,
            source_name=source_name,
            debug=debug,
            api_server=api_server
        )
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
        # Ensure runtime is properly stopped
        if 'runtime' in locals():
            runtime.stop()
    except Exception as e:
        print(f"Runtime error: {e}")
        # Ensure runtime is properly stopped
        if 'runtime' in locals():
            runtime.stop()
    finally:
        if api_server:
            try:
                await api_server.stop()
            except Exception:
                pass
        if api_task and not api_task.done():
            api_task.cancel()
            try:
                await asyncio.gather(api_task, return_exceptions=True)
            except Exception:
                pass


def main() -> None:
    """Main entry point for the plua command line tool"""

    parser = argparse.ArgumentParser(
        description="plua - Python-Lua async runtime with timer support (https://github.com/jangabrielsson/plua/blob/main/README.md)",
        epilog="Examples:\n"
               "  plua                               # Interactive REPL mode\n"
               "  plua script.lua                    # Run script.lua with API server\n"
               "  plua -i script.lua                 # Run script.lua then enter REPL\n"
               "  plua --noapi script.lua            # Run script.lua without API server\n"
               "  plua --api-port 9000 script.lua    # Run with API on port 9000\n"
               "  plua --duration 10 script.lua      # Run for 10 seconds\n"
               "  plua -e 'print(\"hello\")'           # Run inline script\n"
               "  plua -e 'x=1' -e 'print(x)'        # Multiple -e fragments\n"
               "  plua -e 'print(\"start\")' script.lua # Combine -e and file\n"
               "  plua -i -e 'x=1' script.lua        # Run fragments + file, then REPL\n"
               "  plua -a 'extra args' script.lua    # Pass extra arguments to runtime\n"
               "  plua --fibaro script.lua           # Run with Fibaro API support\n"
               "  plua --debugger script.lua         # Run with MobDebug\n"
               "  plua --debugger --debug script.lua # Run with verbose debug logging\n"
               "  plua --cleanup-port                # Clean up stuck API port\n"
               "  plua --close-windows               # Close all QuickApp windows\n"
               "  plua --close-qa-window 123         # Close window for QA ID 123\n"
               "  plua --cleanup-registry            # Clean up old window registry entries\n"
               "  plua --desktop script.lua          # Force desktop UI (override QA)\n"
               "  plua --desktop=false script.lua    # Force no desktop UI (override QA)\n"
               "  plua --debugger --debugger-host 192.168.1.100 script.lua",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # log command line given to plua
    #  print(f"Command line: {' '.join(sys.argv)}")

    parser.add_argument(
        "-e",
        help="Execute inline Lua code (like lua -e). Can be used multiple times.",
        action="append",
        type=str,
        dest="script_fragments"
    )

    parser.add_argument(
        "--duration", "-d",
        help="Duration in seconds to run (default: run forever)",
        type=int,
        default=None
    )

    parser.add_argument(
        "--debugger",
        help="Enable MobDebug debugger (handled in init.lua)",
        action="store_true"
    )

    parser.add_argument(
        "--debugger-host",
        help="Host for MobDebug connection (default: localhost)",
        type=str,
        default="localhost"
    )

    parser.add_argument(
        "--debugger-port",
        help="Port for MobDebug connection (default: 8172)",
        type=int,
        default=8172
    )

    parser.add_argument(
        "--debug",
        help="Enable debug logging for MobDebug and plua internals",
        action="store_true"
    )

    parser.add_argument(
        "--ignore-lua",
        help="Busted compatibility",
        action="store_true"
    )

    parser.add_argument(
        "--lua",
        help="Enable debug logging for MobDebug and plua internals",
        type=str,
        default="lua"  # Default to 'lua' if not specified
    )

    parser.add_argument(
        "--fibaro",
        help="Load Fibaro API support (equivalent to -e \"require('fibaro')\")",
        action="store_true"
    )

    parser.add_argument(
        "-i", "--interactive",
        help="Enter interactive REPL after running script fragments and main file",
        action="store_true"
    )

    parser.add_argument(
        "-a", "--args",
        help="Extra arguments to pass to the Lua runtime",
        type=str,
        default=None
    )

    parser.add_argument(
        "-l", "--library",
        help="EIgnored for now...",
        type=str,
        default=None
    )

    parser.add_argument(
        "--version", "-v",
        help="Show version and exit",
        action="store_true"
    )

    parser.add_argument(
        "lua_file",
        help="Lua file to execute",
        nargs="?",  # Optional positional argument
        type=str
    )

    parser.add_argument(
        "--noapi",
        help="Disable the REST API server (API is enabled by default on port 8888)",
        action="store_true"
    )

    parser.add_argument(
        "--api-port",
        help="Port for REST API server (default: 8888)",
        type=int,
        default=8888
    )

    parser.add_argument(
        "--api-host",
        help="Host for REST API server (default: 0.0.0.0)",
        type=str,
        default="0.0.0.0"
    )

    parser.add_argument(
        "--cleanup-port",
        help="Clean up the API port and exit (useful when port is stuck)",
        action="store_true"
    )

    parser.add_argument(
        "--close-windows",
        help="Close all open QuickApp windows and exit",
        action="store_true"
    )

    parser.add_argument(
        "--close-qa-window",
        help="Close QuickApp window for specific QA ID and exit",
        type=int,
        metavar="QA_ID"
    )

    parser.add_argument(
        "--cleanup-registry",
        help="Clean up old window registry entries and exit",
        action="store_true"
    )

    parser.add_argument(
        "--desktop",
        help="Override desktop UI mode for QuickApp windows (true/false). If not specified, QA decides based on --%%desktop header",
        nargs="?",
        const="true",
        type=str,
        default=None
    )

    parser.add_argument(
        "--init-quickapp",
        help="Initialize a new QuickApp project with .vscode config, .project file, and starter code",
        action="store_true"
    )

    args = parser.parse_args()

    # Set up signal handlers for graceful shutdown (especially for VS Code termination)
    setup_signal_handlers()

    # Show greeting with version information first
    show_greeting()

    if args.version:
        sys.exit(0)

    # Handle port cleanup if requested
    if args.cleanup_port:
        from .api_server import cleanup_port_cli
        # Use the API port for cleanup
        cleanup_port = args.api_port
        success = cleanup_port_cli(cleanup_port, args.api_host)
        print(f"Port cleanup completed for {args.api_host}:{cleanup_port}")
        sys.exit(0 if success else 1)

    # Handle window closure if requested
    if args.close_windows:
        try:
            from .luafuns_lib import close_all_quickapp_windows
            result = close_all_quickapp_windows()
            if result.get("success"):
                print(f"QuickApp window closure: {result['message']}")
            else:
                print(f"Error closing QuickApp windows: {result.get('error', 'Unknown error')}")
                sys.exit(1)
            
            # Also cleanup any lingering mobdebug connections on port 8172
            try:
                import socket
                import time
                
                # Try to bind to the mobdebug port to see if it's free
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.bind(('localhost', 8172))
                    sock.close()
                    print("MobDebug port 8172 is clean")
                except OSError as e:
                    sock.close()
                    print(f"MobDebug port 8172 cleanup: {e}")
                    
                    # Try to cleanup any processes using the port
                    try:
                        import psutil
                        for conn in psutil.net_connections():
                            if conn.laddr.port == 8172:
                                try:
                                    proc = psutil.Process(conn.pid)
                                    print(f"Found process using port 8172: {proc.name()} (PID: {conn.pid})")
                                    # Don't kill - just report for now to avoid issues
                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    pass
                    except ImportError:
                        pass  # psutil not available
                        
            except Exception as e:
                print(f"Note: MobDebug port check failed: {e}")
            
            # Use os._exit() to bypass atexit handlers since we've already done the cleanup
            os._exit(0 if result['success'] else 1)
        except Exception as e:
            print(f"Error closing QuickApp windows: {e}")
            os._exit(1)

    # Handle specific QA window closure if requested  
    if args.close_qa_window:
        try:
            from .luafuns_lib import close_quickapp_window
            result = close_quickapp_window(args.close_qa_window)
            print(f"QuickApp {args.close_qa_window} window closure: {result.get('message', result.get('error', 'Unknown result'))}")
            os._exit(0 if result.get('success') else 1)
        except Exception as e:
            print(f"Error closing QA {args.close_qa_window} window: {e}")
            os._exit(1)

    # Handle registry cleanup if requested
    if args.cleanup_registry:
        try:
            from .luafuns_lib import _cleanup_old_registry_entries
            import json
            from pathlib import Path
            
            registry_file = Path.home() / ".plua" / "window_registry.json"
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    registry = json.load(f)
                
                initial_count = len(registry.get("windows", {}))
                _cleanup_old_registry_entries(registry, max_closed_entries=5)  # More aggressive cleanup
                final_count = len(registry.get("windows", {}))
                
                with open(registry_file, 'w') as f:
                    json.dump(registry, f, indent=2)
                    f.write('\n')
                
                removed_count = initial_count - final_count
                print(f"Registry cleanup completed: removed {removed_count} old entries ({initial_count} -> {final_count})")
            else:
                print("No window registry file found - nothing to clean up")
            
            os._exit(0)
        except Exception as e:
            print(f"Error cleaning up registry: {e}")
            os._exit(1)

    # Handle QuickApp project initialization if requested
    if args.init_quickapp:
        try:
            init_quickapp_project()
            os._exit(0)
        except Exception as e:
            print(f"Error initializing QuickApp project: {e}")
            os._exit(1)

    # Prepare debugger config if requested
    debugger_config = None
    if args.debugger:
        debugger_config = {
            'host': args.debugger_host,
            'port': args.debugger_port,
            'debug': args.debug
        }
    
    # Parse desktop argument: None means QA decides, True/False means CLI override
    desktop_override = None
    if args.desktop is not None:
        desktop_str = args.desktop.lower()
        if desktop_str in ('true', '1', 'yes', 'on'):
            desktop_override = True
        elif desktop_str in ('false', '0', 'no', 'off'):
            desktop_override = False
        else:
            print(f"Warning: Invalid --desktop value '{args.desktop}'. Use true/false. Ignoring.")
            desktop_override = None
    
    # Collect all config into a single dictionary
    config = {
        'debugger_config': debugger_config,
        'debug': args.debug,
        'api_config': None if args.noapi else {'host': args.api_host, 'port': args.api_port},
        'source_name': None,  # source_name will be set based on args.lua_file
        'args': args.args,  # Extra arguments passed via -a/--args
        'desktop': desktop_override,  # Desktop UI mode override (None = QA decides, True/False = CLI override)
        # Add more CLI flags here as needed
    }
    runtime = LuaAsyncRuntime(config=config)
    
    # Initialize desktop UI if explicitly requested via CLI (desktop_override = True)
    # Note: If desktop_override is None, the QA will decide based on --%%desktop header
    if desktop_override is True:
        try:
            from .desktop_ui import initialize_desktop_ui
            api_base_url = f"http://{args.api_host}:{args.api_port}" if not args.noapi else "http://localhost:8888"
            initialize_desktop_ui(api_base_url)
            print(f"Desktop UI initialized via CLI override. API available at {api_base_url}")
        except ImportError:
            print("Warning: Desktop UI not available. Install with: pip install pywebview")
        except Exception as e:
            print(f"Warning: Could not initialize desktop UI: {e}")
    
    # Determine which script to run
    script_fragments = args.script_fragments or []

    # Add Fibaro support if requested
    if args.fibaro:
        script_fragments = ["require('fibaro')"] + script_fragments

    main_script = None
    main_file = None
    source_file_name = None  # Track the file name for debugging

    # Check if Lua file exists if provided
    if args.lua_file:
        if not os.path.exists(args.lua_file):
            print(f"Error: File '{args.lua_file}' not found")
            sys.exit(1)
        # Store the file path instead of reading content
        main_file = args.lua_file
        # Use the file name for debugging (preserve relative path for VS Code)
        source_file_name = args.lua_file
        config['source_name'] = source_file_name

    # Determine if we should enter interactive mode
    has_script_content = bool(script_fragments or main_script or main_file)
    interactive_mode = args.interactive or not has_script_content

    if has_script_content and not interactive_mode:
        # Run script and exit
        try:
            asyncio.run(run_script(runtime=runtime, script_fragments=script_fragments, main_script=main_script, main_file=main_file, duration=args.duration))
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            # Cleanup QuickApp windows on interruption
            try:
                from .luafuns_lib import close_all_quickapp_windows
                close_all_quickapp_windows()
            except Exception as e:
                print(f"Window cleanup error: {e}")
            sys.exit(0)
        except asyncio.CancelledError:
            # Handle cancellation during shutdown (e.g., from _PY.isRunning termination)
            # This is expected behavior, exit cleanly without showing error
            try:
                from .luafuns_lib import close_all_quickapp_windows
                close_all_quickapp_windows()
            except:
                pass
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            try:
                from .luafuns_lib import close_all_quickapp_windows
                close_all_quickapp_windows()
            except:
                pass
            sys.exit(1)
    else:
        # Either no script content (implicit interactive) or explicit -i flag
        # Run script content first (if any), then enter REPL
        try:
            asyncio.run(run_interactive(runtime=runtime, script_fragments=script_fragments, main_script=main_script, main_file=main_file, duration=args.duration))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            # Cleanup QuickApp windows on interruption
            try:
                from .luafuns_lib import close_all_quickapp_windows
                close_all_quickapp_windows()
                # Also ensure runtime is stopped
                if 'runtime' in locals():
                    runtime.stop()
            except Exception as e:
                print(f"Window cleanup error: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()
