# Fibaro HC3 REST API Reference

This document provides a comprehensive overview of the 269 REST API endpoints available in the Fibaro Home Center 3 (HC3) system, as implemented in PLua's FastAPI server.

## Model Context Protocol (MCP) Usage

This documentation is optimized for use as context in Model Context Protocol implementations. It provides:

- **Complete API Coverage**: All 269 endpoints with request/response formats
- **Functional Categorization**: Endpoints grouped by use case for efficient context retrieval
- **Tool Implementation Guidance**: Ready-to-use JSON schemas and examples
- **Integration Context**: PLua-specific implementation details and best practices

### Quick MCP Integration Guide

**For Tool Definitions**: Each endpoint includes HTTP method, path, and complete JSON schemas
**For Context Retrieval**: Use category-based sections to provide relevant API subsets
**For Error Handling**: Reference the Authentication & Security section for proper error responses
**For Type Safety**: All examples use proper JSON formatting compatible with Pydantic models

### Common MCP Tool Patterns

```typescript
// Device Control Tool Example
{
  "name": "fibaro_control_device",
  "description": "Control a Fibaro device (turn on/off, set value, etc.)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "deviceId": {"type": "number", "description": "Device ID"},
      "action": {"type": "string", "description": "Action name (turnOn, turnOff, setValue, etc.)"},
      "args": {"type": "array", "description": "Action arguments"}
    },
    "required": ["deviceId", "action"]
  }
}

// Scene Execution Tool Example  
{
  "name": "fibaro_run_scene",
  "description": "Execute a Fibaro scene",
  "inputSchema": {
    "type": "object", 
    "properties": {
      "sceneId": {"type": "number", "description": "Scene ID to execute"},
      "args": {"type": "object", "description": "Scene arguments"}
    },
    "required": ["sceneId"]
  }
}

// Device Query Tool Example
{
  "name": "fibaro_get_devices", 
  "description": "Get Fibaro devices with filtering",
  "inputSchema": {
    "type": "object",
    "properties": {
      "roomId": {"type": "number", "description": "Filter by room ID"},
      "interface": {"type": "array", "items": {"type": "string"}, "description": "Filter by interfaces"},
      "type": {"type": "string", "description": "Filter by device type"}
    }
  }
}
```

## API Organization

This comprehensive reference covers 253+ endpoints organized into functional categories. Click any section to jump directly to the detailed documentation.

### [Device Management](#device-management)
- [**Devices** (28 endpoints)](#devices-28-endpoints) - Core device operations, actions, properties, filtering
- [**Plugins** (18 endpoints)](#plugins-18-endpoints) - Plugin management, view updates, event handling
- [**QuickApp** (11 endpoints)](#quickapp-11-endpoints) - QuickApp development, file management, import/export
- [**Additional Interfaces** (2 endpoints)](#additional-interfaces-2-endpoints) - Device interface management

### [Scene & Automation](#scene--automation)
- [**Scenes** (15 endpoints)](#scenes-15-endpoints) - Scene creation, execution, control, conversion
- [**Profiles** (9 endpoints)](#profiles-9-endpoints) - User profile and partition management
- [**Custom Events** (7 endpoints)](#custom-events-7-endpoints) - Custom event definition and triggering
- [**Global Variables** (4 endpoints)](#global-variables-4-endpoints) - Global variable management

### [Energy & Climate](#energy--climate)
- [**Energy** (25 endpoints)](#energy-25-endpoints) - Energy consumption, billing, savings, ecology
- [**Consumption** (6 endpoints)](#consumption-6-endpoints) - Energy consumption panels and metrics
- [**Climate Panel** (7 endpoints)](#climate-panel-7-endpoints) - Climate zone management and control
- [**Humidity Panel** (5 endpoints)](#humidity-panel-5-endpoints) - Humidity zone management
- [**Sprinklers Panel** (9 endpoints)](#sprinklers-panel-9-endpoints) - Sprinkler system control and scheduling

### [System Configuration](#system-configuration)
- [**Network** (19 endpoints)](#network-19-endpoints) - Network configuration, interfaces, connections
- [**Users** (8 endpoints)](#users-8-endpoints) - User management and authentication
- [**Alarms** (16 endpoints)](#alarms-16-endpoints) - Alarm system partitions and history
- [**Rooms** (7 endpoints)](#rooms-7-endpoints) - Room management and grouping
- [**Sections** (5 endpoints)](#sections-5-endpoints) - Section management

### [Panels & UI](#panels--ui)
- [**Notification Center** (4 endpoints)](#notification-center-4-endpoints) - Notification management
- [**Notification Panel** (4 endpoints)](#notification-panel-4-endpoints) - Panel notifications
- [**Location Panel** (5 endpoints)](#location-panel-5-endpoints) - Location and geofencing
- [**Family Panel** (1 endpoint)](#family-panel-1-endpoint) - Family tracking
- [**Favorite Colors** (6 endpoints)](#favorite-colors-6-endpoints) - UI color management

### [Data & Monitoring](#data--monitoring)
- [**Debug Messages** (3 endpoints)](#debug-messages-3-endpoints) - System debug and logging
- [**Device Notifications** (4 endpoints)](#device-notifications-4-endpoints) - Device-specific notifications
- [**History Events** (2 endpoints)](#history-events-2-endpoints) - Event history management
- [**Diagnostics** (2 endpoints)](#diagnostics-2-endpoints) - System diagnostics
- [**Refresh States** (1 endpoint)](#refresh-states-1-endpoint) - Device state refresh
- [**Weather** (1 endpoint)](#weather-1-endpoint) - Weather information

### [Miscellaneous](#miscellaneous)
- [**Icons** (3 endpoints)](#icons-3-endpoints) - Icon management
- [**RGB Programs** (5 endpoints)](#rgb-programs-5-endpoints) - RGB lighting programs
- [**Push Notifications** (3 endpoints)](#push-notifications-3-endpoints) - Mobile push notifications
- [**System Status** (3 endpoints)](#system-status-3-endpoints) - System status monitoring
- [**iOS Devices** (1 endpoint)](#ios-devices-1-endpoint) - iOS device registration

## Device Management

The device management category encompasses core device operations, plugin management, QuickApp development, and device interface management.

### Devices (28 endpoints)

#### Core Device Operations
- `GET /api/devices` - List all devices with filtering options (room, interface, type)
Ex.
  - /api/devices?name=MyQuickApp
  - /api/devices?interface=quickApp

- `POST /api/devices` - Create new plugin device. Use POST /quickApp/ to create a QuickApp.
  ```json
  {
    "name": "Device Name",
    "type": "plugin_device_type",
    "roomID": 1,
    "properties": {
      "configured": true,
      "dead": false,
      "deviceIcon": 1,
      "ip": "192.168.1.100",
      "port": 80,
      "username": "admin",
      "password": "password"
    }
  }
  ```
- `GET /api/devices/{deviceID}` - Get device details and properties
- `PUT /api/devices/{deviceID}` - Modify device configuration
  ```json
  {
    "name": "Updated Device Name",
    "roomID": 2,
    "enabled": true,
    "visible": true,
    "properties": {
      "configured": true,
      "userDescription": "Updated description"
    }
  }
  ```
- `DELETE /api/devices/{deviceID}` - Remove device from system
- `POST /api/devices/filter` - Get filtered device list with advanced criteria
  ```json
  {
    "filters": [
      {
        "filter": "roomId", 
        "value": [1, 2, 3]
      },
      {
        "filter": "interface",
        "value": ["zwave", "energy"]
      }
    ],
    "attributes": {
      "id": true,
      "name": true, 
      "roomID": true,
      "type": true
    }
  }
  ```

#### Device Actions
- `POST /api/devices/{deviceID}/action/{actionName}` - Execute device action
Ex. Call QuckApp 344, function QuickApp:myFun(25,"Heating")
POST /api/devices/344/myFun
  ```json
  {
    "args": [25, "heating"],
    "delay": 0,
    // "integrationPin": "1234"
  }
  ```
- `DELETE /api/devices/action/{timestamp}/{id}` - Cancel delayed action
- `POST /api/devices/groupAction/{actionName}` - Execute group actions on multiple devices
  ```json
  {
    "devices": [1, 2, 3],
    "args": ["turnOn"],
    "delay": 5
  }
  ```

#### Interface Management
- `POST /api/devices/addInterface` - Add interfaces to devices
  ```json
  {
    "devicesId": [1, 2, 3],
    "interfaces": ["energy", "battery"]
  }
  ```
- `POST /api/devices/deleteInterface` - Remove interfaces from devices
  ```json
  {
    "devicesId": [1, 2, 3], 
    "interfaces": ["energy"]
  }
  ```

#### Device Information
- `GET /api/uiDeviceInfo` - Get UI device information with filtering
- `GET /api/devices/hierarchy` - Get device type hierarchy
- `GET /api/devices?property=[lastLoggedUser,{userId}]` - Get mobile devices for specific user

### Plugins (18 endpoints)

#### Plugin Management
- `GET /api/plugins` - Get all plugins information
- `GET /api/plugins/installed` - Get installed plugins list
- `POST /api/plugins/installed` - Install plugin (HC2 compatibility). Don't use for QuickApps.
  ```json
  {
    "type": "com.fibaro.lightBulb"
  }
  ```
- `DELETE /api/plugins/installed` - Delete/uninstall plugin. Don't use for QuickApps.
  ```json
  {
    "type": "com.fibaro.lightBulb",
    "force": false
  }
  ```
- `GET /api/plugins/types` - Get information about available plugin types
- `GET /api/plugins/ipCameras` - Get available IP camera plugins

#### UI and Event Handling
- `GET /api/plugins/callUIEvent` - Trigger UI events with query parameters
- `POST /api/plugins/callUIEvent` - Trigger UI events with JSON payload
  ```json
  {
    "deviceId": 25,
    "elementName": "button1",
    "eventType": "onReleased",
    "value": "clicked"
  }
  ```
- `GET /api/plugins/getView` - Get plugin view configuration
- `POST /api/plugins/updateView` - Update plugin view components
  ```json
  {
    "deviceId": 25,
    "componentName": "label1",
    "propertyName": "text", 
    "newValue": "Updated text"
  }
  ```

#### Property and Interface Management
- `POST /api/plugins/updateProperty` - Update device properties. UPdates property without causing restart of QuickApp. Also generates system event.
  ```json
  {
    "deviceId": 25,
    "propertyName": "value",
    "value": 75
  }
  ```
- `POST /api/plugins/interfaces` - Add or remove device interfaces
  ```json
  {
    "action": "add",
    "deviceId": 25,
    "interfaces": ["energy", "battery"]
  }
  ```
- `POST /api/plugins/restart` - Restart specific plugin
  ```json
  {
    "deviceId": 25
  }
  ```

#### Child Device Support
- `POST /api/plugins/createChildDevice` - Create child devices for multi-channel plugins
  ```json
  {
    "parentId": 25,
    "type": "com.fibaro.binarySwitch",
    "name": "Switch Channel 2",
    "initialProperties": {
      "value": false,
      "dead": false
    },
    "initialInterfaces": ["zwave"]
  }
  ```

#### Event Publishing
- `POST /api/plugins/publishEvent` - Publish events through plugin system
  ```json
  {
    "eventType": "centralSceneEvent",
    "source": 25,
    "data": {
      "keyId": 1,
      "keyAttribute": "Pressed"
    }
  }
  ```

### QuickApp (11 endpoints)

#### QuickApp Creation and Management
- `POST /api/quickApp` - Create new QuickApp device
  ```json
  {
    "name": "My QuickApp",
    "type": "com.fibaro.generic.device",
    "roomId": 1,
    "initialProperties": {
      "userDescription": "Custom QuickApp description"
    },
    "initialInterfaces": ["zwave", "energy"],
    "initialView": { /* UI view configuration */ }
  }
  ```
- `GET /api/quickApp/availableTypes` - Get available QuickApp device types

#### File Management
- `GET /api/quickApp/{deviceId}/files` - List QuickApp source files
- `POST /api/quickApp/{deviceId}/files` - Create new source file
  ```json
  {
    "name": "utils.lua",
    "type": "lua",
    "isOpen": false,
    "isMain": false
  }
  ```
- `PUT /api/quickApp/{deviceId}/files` - Update multiple files at once
  ```json
  [
    {
      "name": "main.lua",
      "content": "-- Updated main file content",
      "isOpen": true
    },
    {
      "name": "utils.lua", 
      "content": "-- Updated utils content",
      "isOpen": false
    }
  ]
  ```
- `GET /api/quickApp/{deviceId}/files/{fileName}` - Get specific file details
- `PUT /api/quickApp/{deviceId}/files/{fileName}` - Update specific file
  ```json
  {
    "name": "main.lua",
    "type": "lua",
    "isOpen": true,
    "isMain": true,
    "content": "-- Updated file content\nfunction QuickApp:onInit()\n  -- initialization code\nend"
  }
  ```
- `DELETE /api/quickApp/{deviceId}/files/{fileName}` - Delete source file

#### Import/Export Operations
- `GET /api/quickApp/export/{deviceId}` - Export QuickApp to .fqa file
- `POST /api/quickApp/export/{deviceId}` - Export encrypted QuickApp to .fqax file
  ```json
  {
    "encrypted": true,
    "serialNumbers": ["HC3-001234", "HC3-005678"]
  }
  ```
- `POST /api/quickApp/import` - Import QuickApp from .fqa/.fqax file
  ```json
  {
    "file": "base64_encoded_fqa_content",
    "roomId": 1
  }
  ```

### Additional Interfaces (2 endpoints)

#### Interface Discovery
- `GET /api/additionalInterfaces` - Get list of all additional interfaces for device
- `GET /api/additionalInterfaces/{interfaceName}` - Get devices that support specific interface

## Scene & Automation

The scene and automation category covers scene management, user profiles, custom events, and global variables for home automation control.

### Scenes (15 endpoints)

#### Scene Management
- `GET /api/scenes` - List all scenes with filtering options
- `POST /api/scenes` - Create new scene
  ```json
  {
    "name": "string",
    "description": "string", 
    "type": "string",
    "mode": "string",
    "icon": "string",
    "content": "string",
    "maxRunningInstances": 0,
    "hidden": false,
    "protectedByPin": false,
    "stopOnAlarm": false,
    "enabled": true,
    "restart": true,
    "categories": [0],
    "scenarioData": { /* ScenarioContent object */ },
    "roomId": 0
  }
  ```
- `GET /api/scenes/{sceneID}` - Get scene details and configuration
- `PUT /api/scenes/{sceneID}` - Modify existing scene
  ```json
  {
    "name": "string",
    "description": "string",
    "mode": "string", 
    "maxRunningInstances": 0,
    "icon": "string",
    "content": "string",
    "hidden": false,
    "protectedByPin": false,
    "stopOnAlarm": false,
    "enabled": true,
    "restart": true,
    "categories": [0],
    "scenarioData": { /* ScenarioContent object */ },
    "roomId": 0
  }
  ```
- `DELETE /api/scenes/{sceneID}` - Delete scene from system

#### Scene Execution
- `GET /api/scenes/{sceneID}/execute` - Execute scene (GET method)
- `POST /api/scenes/{sceneID}/execute` - Execute scene asynchronously
  ```json
  {
    "alexaProhibited": false,
    "args": { /* key-value pairs */ }
  }
  ```
- `GET /api/scenes/{sceneID}/executeSync` - Execute scene synchronously (GET)
- `POST /api/scenes/{sceneID}/executeSync` - Execute scene synchronously (POST)
  ```json
  {
    "alexaProhibited": false,
    "args": { /* key-value pairs */ }
  }
  ```

#### Scene Control
- `GET /api/scenes/{sceneID}/kill` - Stop running scene (GET method)
- `POST /api/scenes/{sceneID}/kill` - Stop running scene (POST method)
  ```json
  {
    "force": true
  }
  ```

#### Scene Utilities
- `POST /api/scenes/hasTriggers` - Check if scenes have triggers
  ```json
  {
    "sceneIds": [1, 2, 3]
  }
  ```
- `POST /api/scenes/{sceneID}/copy` - Copy existing scene
  ```json
  {
    "newName": "Copied Scene",
    "roomId": 2
  }
  ```
- `POST /api/scenes/{sceneID}/convert` - Convert scene to different format
  ```json
  {
    "targetFormat": "lua",
    "preserveStructure": true
  }
  ```
- `POST /api/scenes/{sceneID}/copyAndConvert` - Copy and convert scene in one operation
  ```json
  {
    "newName": "Converted Copy",
    "targetFormat": "lua",
    "roomId": 2
  }
  ```

### Profiles (9 endpoints)

#### Profile Management
- `GET /api/profiles` - Get all user profiles
- `PUT /api/profiles` - Update profile settings
  ```json
  {
    "activeProfile": 1
  }
  ```
- `POST /api/profiles` - Create new profile
  ```json
  {
    "name": "Evening Mode",
    "iconId": 5,
    "sourceId": 0
  }
  ```
- `GET /api/profiles/{profileId}` - Get specific profile details
- `PUT /api/profiles/{profileId}` - Update specific profile
  ```json
  {
    "name": "Updated Evening Mode",
    "iconId": 7,
    "devices": [
      {
        "id": 1,
        "action": {
          "name": "turnOn",
          "isUIAction": false,
          "args": []
        }
      }
    ],
    "scenes": [
      {
        "sceneId": 10,
        "actions": ["start"]
      }
    ]
  }
  ```
- `DELETE /api/profiles/{profileId}` - Delete profile

#### Profile Associations
- `PUT /api/profiles/{profileId}/partitions/{partitionId}` - Associate profile with partition
  ```json
  {
    "action": "arm"
  }
  ```
- `PUT /api/profiles/{profileId}/climateZones/{zoneId}` - Associate profile with climate zone
  ```json
  {
    "mode": "heating",
    "properties": {
      "handSetPointHeating": 22.0,
      "handSetPointCooling": 24.0,
      "handMode": "manual"
    }
  }
  ```
- `PUT /api/profiles/{profileId}/scenes/{sceneId}` - Associate profile with scene
  ```json
  {
    "actions": ["start", "stop"]
  }
  ```

#### Profile Actions
- `POST /api/profiles/reset` - Reset profiles to defaults
- `POST /api/profiles/activeProfile/{profileId}` - Set active profile

### Custom Events (7 endpoints)

#### Event Management
- `GET /api/customEvents` - List all defined custom events
- `POST /api/customEvents` - Create new custom event
  ```json
  {
    "name": "myCustomEvent",
    "userDescription": "Event triggered when something specific happens"
  }
  ```
- `GET /api/customEvents/{customEventName}` - Get custom event details
- `PUT /api/customEvents/{customEventName}` - Modify custom event
  ```json
  {
    "name": "myCustomEvent",
    "userDescription": "Updated event description"
  }
  ```
- `DELETE /api/customEvents/{customEventName}` - Delete custom event

#### Event Triggering
- `POST /api/customEvents/{customEventName}` - Emit custom event (POST)
- `GET /api/customEvents/{customEventName}/publish` - Emit custom event (GET)

### Global Variables (4 endpoints)

#### Variable Management
- `GET /api/globalVariables` - List all global variables
- `POST /api/globalVariables` - Create new global variable
  ```json
  {
    "name": "myVariable",
    "value": "initial value",
    "isEnum": false,
    "enumValues": [],
    "readOnly": false
  }
  ```
- `GET /api/globalVariables/{globalVariableName}` - Get variable value
- `PUT /api/globalVariables/{globalVariableName}` - Update variable value
  ```json
  {
    "name": "myVariable", 
    "value": "updated value",
    "isEnum": false,
    "enumValues": [],
    "readOnly": false
  }
  ```
- `DELETE /api/globalVariables/{globalVariableName}` - Delete global variable

## Energy & Climate

This category manages energy consumption monitoring, climate control, and environmental systems.

### Energy (25 endpoints)

#### Device and Consumption Monitoring
- `GET /api/energy/devices` - List energy-enabled devices
- `GET /api/energy/consumption/summary` - Overall energy consumption summary
- `GET /api/energy/consumption/metrics` - Energy consumption metrics
- `GET /api/energy/consumption/detail` - Detailed consumption data
- `GET /api/energy/consumption/room/{roomId}/detail` - Room-specific consumption
- `GET /api/energy/consumption/device/{deviceId}/detail` - Device-specific consumption
- `DELETE /api/energy/consumption` - Delete consumption data
  ```json
  {
    "deviceIds": [1, 2, 3],
    "startPeriod": "2025-01-01",
    "endPeriod": "2025-01-31"
  }
  ```

#### Billing Management
- `GET /api/energy/billing/summary` - Billing summary information
- `GET /api/energy/billing/periods` - Get billing periods
- `POST /api/energy/billing/periods` - Create billing period
  ```json
  {
    "duration": "1", // months: 1,2,3,6,12
    "startDate": "2025-01-01",
    "fixedCost": 25.50
  }
  ```
- `GET /api/energy/billing/tariff` - Get current tariff information
- `PUT /api/energy/billing/tariff` - Update tariff settings
  ```json
  {
    "rate": 0.15,
    "name": "Standard Tariff",
    "returnRate": 0.08,
    "additionalTariffs": [
      {
        "rate": 0.22,
        "name": "Peak Hours",
        "startTime": "17:00",
        "endTime": "21:00", 
        "days": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
      }
    ]
  }
  ```

#### Installation Costs
- `GET /api/energy/installationCost` - Get installation cost data
- `POST /api/energy/installationCost` - Add installation cost entry
  ```json
  {
    "date": "2025-01-15",
    "cost": 5000.00,
    "name": "Solar Panel Installation"
  }
  ```
- `GET /api/energy/installationCost/{id}` - Get specific installation cost
- `PUT /api/energy/installationCost/{id}` - Update installation cost
  ```json
  {
    "date": "2025-01-15", 
    "cost": 5500.00,
    "name": "Solar Panel Installation (Updated)"
  }
  ```
- `DELETE /api/energy/installationCost/{id}` - Delete installation cost

#### Savings and Ecology
- `GET /api/energy/savings/detail` - Detailed savings information
- `GET /api/energy/savings/summary` - Energy savings summary
- `GET /api/energy/savings/installation` - Installation savings data
- `GET /api/energy/ecology/summary` - Environmental impact summary
- `GET /api/energy/ecology/detail` - Detailed ecology metrics

#### Settings
- `GET /api/energy/settings` - Get energy system settings
- `PUT /api/energy/settings` - Update energy settings
  ```json
  {
    "consumptionMeasurement": "kWh",
    "energyConsumptionMeters": [1, 2, 3],
    "energyProductionMeters": [4, 5],
    "powerConsumptionMeters": [6, 7],
    "powerProductionMeters": [8],
    "gridConsumptionMeters": [1],
    "gridProductionMeters": [4],
    "gridPowerConsumptionMeters": [6],
    "gridPowerProductionMeters": [8]
  }
  ```

### Consumption (6 endpoints)

#### Panel Energy Data
- `GET /api/panels/energy?details=summary&period={period}` - Energy summary by period
- `GET /api/panels/energy?id={id}` - Energy data for specific device
- `GET /api/panels/energy?details=billing&period={period}` - Billing details
- `GET /api/panels/energy?details=savings&period={period}` - Savings information
- `GET /api/panels/energy?details=ranking&period={period}` - Device ranking by consumption
- `GET /api/panels/energy?details=ecology&period={period}` - Ecology impact data

### Climate Panel (7 endpoints)

#### Climate Zone Management
- `GET /api/panels/climate` - List all climate zones (with detailed option)
- `POST /api/panels/climate` - Create new climate zone
  ```json
  {
    "name": "Living Room Climate",
    "devices": [1, 2, 3],
    "handMode": "manual",
    "handSetPointHeating": 21.0,
    "handSetPointCooling": 25.0,
    "scheduleHeating": {
      "monday": {
        "morning": {"hour": 6, "minute": 0, "temperature": 20.0},
        "day": {"hour": 8, "minute": 0, "temperature": 18.0},
        "evening": {"hour": 18, "minute": 0, "temperature": 21.0},
        "night": {"hour": 22, "minute": 0, "temperature": 17.0}
      }
    }
  }
  ```
- `GET /api/panels/climate/{climateID}` - Get specific climate zone details
- `PUT /api/panels/climate/{climateID}` - Update climate zone settings
  ```json
  {
    "name": "Updated Living Room Climate",
    "handSetPointHeating": 22.0,
    "handSetPointCooling": 24.0,
    "mode": "heating",
    "devices": [1, 2, 3, 4]
  }
  ```
- `DELETE /api/panels/climate/{climateID}` - Delete climate zone

#### Climate System Operations
- `POST /api/panels/climate/action/createDefaultZones` - Create default climate zones
- `GET /api/panels/climate/availableDevices` - List available climate devices

### Humidity Panel (5 endpoints)

#### Humidity Zone Management
- `GET /api/panels/humidity` - List all humidity zones
- `POST /api/panels/humidity` - Create new humidity zone
  ```json
  {
    "name": "Bedroom Humidity"
  }
  ```
- `GET /api/panels/humidity/{humidityID}` - Get humidity zone details
- `PUT /api/panels/humidity/{humidityID}` - Update humidity zone
  ```json
  {
    "name": "Updated Bedroom Humidity",
    "properties": {
      "currentHumidity": 45.0,
      "handHumidity": 50.0,
      "vacationHumidity": 40.0,
      "rooms": [1, 2],
      "monday": {
        "morning": {"hour": 6, "minute": 0, "humidity": 45.0},
        "day": {"hour": 8, "minute": 0, "humidity": 50.0},
        "evening": {"hour": 18, "minute": 0, "humidity": 45.0},
        "night": {"hour": 22, "minute": 0, "humidity": 40.0}
      }
    }
  }
  ```
- `DELETE /api/panels/humidity/{humidityID}` - Delete humidity zone

### Sprinklers Panel (9 endpoints)

#### Schedule Management
- `GET /api/panels/sprinklers` - Get all sprinkler schedules
- `POST /api/panels/sprinklers` - Create new sprinkler schedule
  ```json
  {
    "name": "Garden Watering Schedule"
  }
  ```
- `GET /api/panels/sprinklers/{scheduleId}` - Get specific schedule
- `PUT /api/panels/sprinklers/{scheduleId}` - Update sprinkler schedule
  ```json
  {
    "name": "Updated Garden Schedule",
    "days": ["MONDAY", "WEDNESDAY", "FRIDAY"],
    "sequences": [
      {
        "startTime": 21600,
        "sprinklers": [
          {
            "deviceId": 10,
            "duration": 1800
          }
        ]
      }
    ],
    "isActive": true
  }
  ```
- `DELETE /api/panels/sprinklers/{scheduleId}` - Remove schedule

#### Sequence Management
- `POST /api/panels/sprinklers/{scheduleId}/sequences` - Create sprinkler sequence
  ```json
  {
    "startTime": 21600,
    "sprinklers": [
      {
        "deviceId": 10,
        "duration": 1800
      },
      {
        "deviceId": 11, 
        "duration": 900
      }
    ]
  }
  ```
- `PUT /api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}` - Update sequence
  ```json
  {
    "startTime": 25200,
    "sprinklers": [
      {
        "deviceId": 10,
        "duration": 2400
      }
    ]
  }
  ```
- `DELETE /api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}` - Delete sequence

#### Watering Control
- `POST /api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}/startWatering` - Start watering
  ```json
  {
    "duration": 1800,
    "zones": [1, 2, 3]
  }
  ```
- `POST /api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}/stopWatering` - Stop watering
  ```json
  {
    "immediate": true
  }
  ```

## System Configuration

This category encompasses network settings, user management, alarm systems, and organizational structures.

### Network (19 endpoints)

#### Interface Configuration
- `GET /api/settings/network/interfaces` - List all network interfaces
- `GET /api/settings/network/interfaces/{interfaceName}` - Get interface configuration
- `PUT /api/settings/network/interfaces/{interfaceName}` - Update interface settings

#### Connection Management
- `GET /api/settings/network/connections` - List network connections
- `POST /api/settings/network/connections` - Add new network connection
  ```json
  {
    "name": "MyWiFiNetwork",
    "enabled": true,
    "apConfig": {
      "ssid": "MyWiFiNetwork",
      "security": "WPA2",
      "password": "mypassword",
      "fallback": false,
      "hidden": false
    },
    "ipConfig": {
      "ipMode": "dhcp"
    }
  }
  ```
- `GET /api/settings/network/connections/{connectionUuid}` - Get connection status
- `PUT /api/settings/network/connections/{connectionUuid}` - Update connection
  ```json
  {
    "name": "UpdatedWiFiNetwork",
    "enabled": true,
    "apConfig": {
      "ssid": "UpdatedSSID",
      "security": "WPA3",
      "password": "newpassword"
    },
    "ipConfig": {
      "ipMode": "static",
      "ip": "192.168.1.100",
      "mask": "255.255.255.0",
      "gateway": "192.168.1.1",
      "dns1": "8.8.8.8",
      "dns2": "8.8.4.4"
    }
  }
  ```
- `DELETE /api/settings/network/connections/{connectionUuid}` - Remove connection

#### Connection Control
- `POST /api/settings/network/connections/{connectionUuid}/check` - Check connection status
  ```json
  {
    "timeout": 5000
  }
  ```
- `POST /api/settings/network/connections/{connectionUuid}/connect` - Connect to wireless
  ```json
  {
    "password": "wifi_password",
    "auto": true
  }
  ```
- `POST /api/settings/network/connections/{connectionUuid}/disconnect` - Disconnect wireless
  ```json
  {
    "graceful": true
  }
  ```

#### Radio Configuration
- `GET /api/settings/network/radio` - Get radio configuration
- `PUT /api/settings/network/radio` - Update radio settings
  ```json
  {
    "zwave": {
      "enabled": true
    },
    "zigbee": {
      "enabled": false
    }
  }
  ```
- `GET /api/settings/network/radio/{radioType}` - Get radio config by type
- `PUT /api/settings/network/radio/{radioType}` - Update radio by type
  ```json
  {
    "enabled": true
  }
  ```

#### Network Information
- `GET /api/settings/network` - Get network configurations
- `GET /api/settings/network/connectivity` - Get internet connectivity status
- `GET /api/settings/network/interfaces/{interfaceName}/apList` - List access points
- `GET /api/settings/network/interfaces/{interfaceName}/apInfo` - AP information

#### System Operations
- `PUT /api/settings/network/resetInterfaces` - Reset network interfaces
  ```json
  {
    "interfaces": ["eth0", "wlan0"],
    "restartServices": true
  }
  ```
- `GET /api/settings/network/AccessPointMode` - Get access point status
- `PUT /api/settings/network/AccessPointMode` - Set access point mode
  ```json
  {
    "accessPointEnabled": true
  }
  ```
- `GET /api/settings/network/enabledProtocols` - Get enabled protocols
- `PUT /api/settings/network/enabledProtocols` - Set enabled protocols
  ```json
  {
    "http": true,
    "https": true
  }
  ```

### Users (8 endpoints)

#### User Management
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
  ```json
  {
    "email": "user@example.com",
    "name": "John Doe",
    "type": "guest"
  }
  ```
- `GET /api/users/{userID}` - Get user details
- `PUT /api/users/{userID}` - Update user information
  ```json
  {
    "name": "John Smith",
    "email": "john.smith@example.com",
    "type": "guest",
    "pin": "1234",
    "alarmRights": [1, 2],
    "climateZoneRights": [1],
    "profileRights": [1, 2, 3],
    "sendNotifications": true,
    "tracking": 1,
    "useOptionalArmPin": false,
    "integrationPin": "5678"
  }
  ```
- `DELETE /api/users/{userID}` - Delete user account

#### User Actions
- `POST /api/users/{userID}/raInvite` - Send remote access invite
  ```json
  {
    "message": "Welcome to the home automation system"
  }
  ```
- `POST /api/users/action/changeAdmin/{newAdminId}` - Change admin user
  ```json
  {
    "currentAdminPin": "1234"
  }
  ```
- `POST /api/users/action/confirmAdminTransfer` - Confirm admin transfer
  ```json
  {
    "confirmationCode": "abcd1234"
  }
  ```
- `POST /api/users/action/cancelAdminTransfer` - Cancel admin transfer
  ```json
  {
    "reason": "Operation cancelled by user"
  }
  ```
- `POST /api/users/action/synchronize` - Synchronize users
  ```json
  {
    "force": false
  }
  ```

### Alarms (16 endpoints)

#### Partition Management
- `GET /api/alarms/v1/partitions` - List all alarm partitions
- `POST /api/alarms/v1/partitions` - Create new partition
  ```json
  {
    "name": "Ground Floor",
    "armDelay": 30,
    "breachDelay": 60, 
    "devices": [1, 2, 3, 4]
  }
  ```
- `GET /api/alarms/v1/partitions/{partitionID}` - Get partition details
- `PUT /api/alarms/v1/partitions/{partitionID}` - Update partition
  ```json
  {
    "name": "Ground Floor Updated",
    "armDelay": 45,
    "breachDelay": 90,
    "devices": [1, 2, 3, 4, 5]
  }
  ```
- `DELETE /api/alarms/v1/partitions/{partitionID}` - Delete partition

#### System Arming/Disarming
- `POST /api/alarms/v1/partitions/actions/tryArm` - Try to arm all partitions
  ```json
  {
    "armingType": "full"
  }
  ```
- `POST /api/alarms/v1/partitions/actions/arm` - Arm all partitions
  ```json
  {
    "armingType": "full"
  }
  ```
- `DELETE /api/alarms/v1/partitions/actions/arm` - Disarm all partitions

#### Individual Partition Control
- `POST /api/alarms/v1/partitions/{partitionID}/actions/tryArm` - Try arm partition
  ```json
  {
    "armingType": "partial"
  }
  ```
- `POST /api/alarms/v1/partitions/{partitionID}/actions/arm` - Arm partition
  ```json
  {
    "armingType": "night"
  }
  ```
- `DELETE /api/alarms/v1/partitions/{partitionID}/actions/arm` - Disarm partition

#### Monitoring and Status
- `GET /api/alarms/v1/history` - Get alarm history with filtering
- `GET /api/alarms/v1/partitions/breached` - Get breached partition IDs
- `GET /api/alarms/v1/devices` - List alarm system devices

### Rooms (7 endpoints)

#### Room Management
- `GET /api/rooms` - List all rooms
- `POST /api/rooms` - Create new room
  ```json
  {
    "name": "Living Room",
    "sectionID": 1,
    "category": "living",
    "icon": "living_room",
    "iconExtension": "svg",
    "iconColor": { /* color configuration */ },
    "visible": true
  }
  ```
- `GET /api/rooms/{roomID}` - Get room details
- `PUT /api/rooms/{roomID}` - Update room information
  ```json
  {
    "name": "Updated Living Room",
    "sectionID": 1,
    "icon": "living_room_new", 
    "iconExtension": "svg",
    "iconColor": { /* color configuration */ },
    "defaultSensors": {
      "temperature": 1,
      "humidity": 2,
      "light": 3
    },
    "defaultThermostat": 10,
    "category": "living",
    "visible": true
  }
  ```
- `DELETE /api/rooms/{roomID}` - Delete room

#### Room Actions
- `POST /api/rooms/{roomID}/action/setAsDefault` - Set room as default
  ```json
  {
    "setDefault": true
  }
  ```
- `POST /api/rooms/{roomID}/groupAssignment` - Assign devices to room group
  ```json
  {
    "deviceIds": [1, 2, 3, 4]
  }
  ```

### Sections (5 endpoints)

#### Section Management
- `GET /api/sections` - List all sections
- `POST /api/sections` - Create new section
  ```json
  {
    "name": "Ground Floor"
  }
  ```
- `GET /api/sections/{sectionID}` - Get section details
- `PUT /api/sections/{sectionID}` - Update section
  ```json
  {
    "name": "Updated Ground Floor",
    "sortOrder": 1
  }
  ```
- `DELETE /api/sections/{sectionID}` - Delete section

## Panels & UI

This category manages user interface elements, notifications, and visual customization.

### Notification Center (4 endpoints)

#### Notification Management
- `POST /api/notificationCenter` - Create new notification
  ```json
  {
    "priority": "info",
    "wasRead": false,
    "canBeDeleted": true,
    "type": "GenericSystemNotificationRequest",
    "data": {
      "title": "System Alert",
      "text": "System maintenance scheduled",
      "name": "maintenance_alert",
      "subType": "Generic"
    }
  }
  ```
- `GET /api/notificationCenter/{notificationId}` - Get notification details
- `PUT /api/notificationCenter/{notificationId}` - Edit notification
  ```json
  {
    "priority": "warning",
    "wasRead": true,
    "data": {
      "title": "Updated System Alert",
      "text": "Maintenance completed successfully"
    }
  }
  ```
- `DELETE /api/notificationCenter/{notificationId}` - Delete notification

### Notification Panel (4 endpoints)

#### Panel Notifications
- `GET /api/panels/notifications` - List all panel notifications
- `POST /api/panels/notifications` - Create panel notification
  ```json
  {
    "name": "Door Alert"
  }
  ```
- `GET /api/panels/notifications/{notificationID}` - Get panel notification
- `PUT /api/panels/notifications/{notificationID}` - Modify panel notification
  ```json
  {
    "name": "Updated Door Alert",
    "sms": "enabled",
    "email": "enabled", 
    "push": "disabled"
  }
  ```
- `DELETE /api/panels/notifications/{notificationID}` - Delete panel notification

### Location Panel (5 endpoints)

#### Location Management
- `GET /api/panels/location` - List all locations
- `POST /api/panels/location` - Create new location
  ```json
  {
    "name": "Home",
    "address": "123 Main Street, City",
    "longitude": -74.006,
    "latitude": 40.7128,
    "radius": 100
  }
  ```
- `GET /api/panels/location/{locationID}` - Get location details
- `PUT /api/panels/location/{locationID}` - Update location
  ```json
  {
    "name": "Updated Home Location",
    "address": "456 New Street, City",
    "longitude": -74.008,
    "latitude": 40.7150,
    "radius": 150
  }
  ```
- `DELETE /api/panels/location/{locationID}` - Delete location

### Family Panel (1 endpoint)

#### Family Tracking
- `GET /api/panels/family` - Get family user tracking data with time range

### Favorite Colors (6 endpoints)

#### Color Palette Management
- `GET /api/panels/favoriteColors` - Get favorite colors (v1)
- `POST /api/panels/favoriteColors` - Create favorite color (v1)
  ```json
  {
    "r": 255,
    "g": 128,
    "b": 0,
    "w": 0,
    "brightness": 80
  }
  ```
- `PUT /api/panels/favoriteColors/{favoriteColorID}` - Update favorite color (v1)
  ```json
  {
    "r": 200,
    "g": 100,
    "b": 50,
    "w": 10,
    "brightness": 75
  }
  ```
- `DELETE /api/panels/favoriteColors/{favoriteColorID}` - Delete favorite color (v1)
- `GET /api/panels/favoriteColors/v2` - Get favorite colors (v2)
- `POST /api/panels/favoriteColors/v2` - Create favorite color (v2)
  ```json
  {
    "colorComponents": {
      "red": 255,
      "green": 128,
      "blue": 0,
      "warmWhite": 0
    },
    "brightness": 80
  }
  ```

## Data & Monitoring

This category provides system monitoring, debugging, and data management capabilities.

### Debug Messages (3 endpoints)

#### Debug Information
- `GET /api/debugMessages` - Get system debug messages with filtering
- `DELETE /api/debugMessages` - Clear debug messages
  ```json
  {
    "level": "error",
    "beforeTimestamp": 1640995200,
    "source": "scenes"
  }
  ```
- `GET /api/debugMessages/tags` - Get available debug message tags

### Diagnostics (2 endpoints)

#### System Diagnostics
- `GET /api/diagnostics` - Get system diagnostic information
- `GET /api/apps/com.fibaro.zwave/diagnostics/transmissions` - Get Z-Wave transmission diagnostics

### Refresh States (1 endpoint)

#### State Management
- `GET /api/refreshStates` - Get device refresh states

### Weather (1 endpoint)

#### Weather Information
- `GET /api/weather` - Get current weather data

### iOS Devices (1 endpoint)

#### Mobile Device Management
- `GET /api/iosDevices` - Get registered iOS devices

### Device Notifications (4 endpoints)

#### Device-Specific Notifications
- `GET /api/deviceNotifications/v1` - List device notifications
- `PUT /api/deviceNotifications/v1/{deviceID}` - Update device notifications
  ```json
  {
    "enabled": true,
    "notifications": [
      {
        "type": "value_change",
        "threshold": 50,
        "condition": "greater_than"
      },
      {
        "type": "device_unreachable",
        "enabled": true
      }
    ]
  }
  ```
- `GET /api/deviceNotifications/v1/{deviceID}` - Get device notification settings
- `DELETE /api/deviceNotifications/v1/{deviceID}` - Delete device notifications

### History Events (2 endpoints)

#### Event History Management
- `GET /api/events/history` - Get historical events with extensive filtering
- `DELETE /api/events/history` - Delete historical events by criteria
  ```json
  {
    "eventType": "CentralSceneEvent",
    "timestamp": 1640995200,
    "objectType": "device",
    "objectId": 25
  }
  ```

## Miscellaneous

This category includes various utility endpoints for icons, RGB programs, system operations, and mobile features.

### Icons (3 endpoints)

#### Icon Management
- `GET /api/icons` - List available icons
- `POST /api/icons` - Upload new icon
  ```json
  {
    "name": "my_custom_icon",
    "content": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
  }
  ```
- `DELETE /api/icons` - Delete icons
  ```json
  {
    "type": "custom",
    "name": "my_icon",
    "fileExtension": "svg"
  }
  ```

### RGB Programs (5 endpoints)

#### RGB Lighting Programs
- `GET /api/RGBPrograms` - List all RGB programs
- `POST /api/RGBPrograms` - Create new RGB program
  ```json
  {
    "name": "Sunset Colors",
    "description": "Warm sunset gradient",
    "steps": [
      {
        "duration": 5000,
        "color": {"r": 255, "g": 140, "b": 0}
      },
      {
        "duration": 3000,
        "color": {"r": 255, "g": 69, "b": 0}
      }
    ]
  }
  ```
- `GET /api/RGBPrograms/{programID}` - Get RGB program details
- `PUT /api/RGBPrograms/{programID}` - Modify RGB program
  ```json
  {
    "name": "Ocean Blues",
    "description": "Cool ocean wave colors",
    "steps": [
      {
        "duration": 4000,
        "color": {"r": 0, "g": 100, "b": 200}
      },
      {
        "duration": 2000,
        "color": {"r": 0, "g": 150, "b": 255}
      }
    ]
  }
  ```
- `DELETE /api/RGBPrograms/{programID}` - Delete RGB program

### Push Notifications (3 endpoints)

#### Mobile Push Messages
- `POST /api/mobile/push` - Create push message
  ```json
  {
    "title": "Home Alert",
    "message": "Motion detected in living room",
    "category": "security",
    "badge": 1,
    "sound": "default"
  }
  ```
- `POST /api/mobile/push/{id}` - Execute push action
  ```json
  {
    "action": "dismiss",
    "response": "acknowledged"
  }
  ```
- `DELETE /api/mobile/push/{id}` - Delete push notification

### System Status (3 endpoints)

#### System Monitoring
- `GET /api/service/systemStatus` - Get system status
- `POST /api/service/systemStatus` - Set system status
  ```json
  {
    "status": "maintenance",
    "message": "System update in progress",
    "estimatedTime": 1800
  }
  ```
- `POST /api/service/restartServices` - Clear system errors
  ```json
  {
    "services": ["scenes", "devices", "plugins"],
    "force": false
  }
  ```

### System Operations (1 endpoint)

#### System Control
- `POST /api/service/factoryReset` - Perform factory reset

### Additional Endpoints

#### Sort Order
- `POST /api/sortOrder` - Update UI element sort order

#### System Reboot
- `POST /api/service/reboot` - Reboot the system

#### Home Information
- `GET /api/home` - Get home information
- `PUT /api/home` - Update home settings

#### User Activity
- `GET /api/userActivity` - Get user activity list

#### Login Status
- `GET /api/loginStatus` - Get current login status
- `POST /api/loginStatus` - Perform login actions

#### Location Settings
- `GET /api/settings/location` - Get location settings
- `PUT /api/settings/location` - Update location settings

#### LED Settings
- `GET /api/settings/led` - Get LED brightness settings
- `PUT /api/settings/led` - Update LED brightness

#### Remote Access
- `GET /api/settings/remoteAccess/status` - Get remote access status
- `GET /api/settings/remoteAccess/status/{typeName}` - Get specific remote access type
- `PUT /api/settings/remoteAccess/status/{typeName}` - Update remote access settings

#### Certificates
- `GET /api/settings/certificates/ca` - Get root CA certificate

#### Info Settings
- `GET /api/settings/info` - Get system info settings
- `PUT /api/settings/info` - Update system info settings

## Authentication & Security

All endpoints require proper authentication through the HC3 system. The API supports:

- User-based access control
- Role-based permissions
- Secure communication protocols
- Session management

## Error Handling

The API provides comprehensive error responses with:

- HTTP status codes
- Detailed error messages
- Validation feedback
- Request context information

## Integration with PLua

This FastAPI implementation serves as a bridge between PLua's Lua environment and the Fibaro HC3 system, enabling:

- Lua-based QuickApp development
- Real-time device control
- Scene automation
- Energy monitoring
- System configuration

### MCP Implementation Patterns

**Device Operations**: Use `/api/devices` endpoints for device discovery, control, and monitoring
**Automation**: Combine `/api/scenes` and `/api/customEvents` for complex automation workflows  
**Energy Management**: Leverage `/api/energy` endpoints for consumption monitoring and optimization
**Climate Control**: Use `/api/panels/climate` for temperature and HVAC management
**Security**: Implement `/api/alarms` endpoints for alarm system integration
**Notifications**: Use `/api/notificationCenter` for user alerts and system messages

**Typical MCP Workflow**:
1. Discover devices using `GET /api/devices`
2. Get device details with `GET /api/devices/{deviceID}`
3. Control devices via `POST /api/devices/{deviceID}/action/{actionName}`
4. Monitor status through periodic device queries
5. Create automation with scenes and custom events

**Best Practices for MCP**:
- Cache device lists to minimize API calls
- Use filtering parameters to reduce response sizes
- Implement proper error handling for network timeouts
- Group related operations for efficiency
- Use WebSocket connections for real-time updates when available

The endpoints are automatically generated from Swagger documentation and provide full type safety through Pydantic models, ensuring reliable integration with both the HC3 system and PLua's emulation environment.
