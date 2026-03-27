# HC3 REST API — Scene & Automation

Full reference for Scenes (15), Profiles (9), Custom Events (7), and Global Variables (4) endpoints.

---

## Scenes (15 endpoints)

### Scene Management
- `GET /api/scenes` — List all scenes
- `POST /api/scenes` — Create new scene
  ```json
  {
    "name": "Night Mode", "type": "lua", "mode": "trigger",
    "enabled": true, "restart": true, "maxRunningInstances": 2,
    "hidden": false, "protectedByPin": false, "stopOnAlarm": false,
    "categories": [], "roomId": 0
  }
  ```
- `GET /api/scenes/{sceneID}` — Get scene details and configuration
- `PUT /api/scenes/{sceneID}` — Modify existing scene
  ```json
  { "name": "Updated Scene", "enabled": true, "maxRunningInstances": 1 }
  ```
- `DELETE /api/scenes/{sceneID}` — Delete scene

### Scene Execution
- `GET /api/scenes/{sceneID}/execute` — Execute scene (GET)
- `POST /api/scenes/{sceneID}/execute` — Execute scene asynchronously
  ```json
  { "alexaProhibited": false, "args": {} }
  ```
- `GET /api/scenes/{sceneID}/executeSync` — Execute and wait (GET)
- `POST /api/scenes/{sceneID}/executeSync` — Execute and wait (POST)

### Scene Control
- `GET /api/scenes/{sceneID}/kill` — Stop running scene (GET)
- `POST /api/scenes/{sceneID}/kill` — Stop running scene (POST)
  ```json
  { "force": true }
  ```

### Scene Utilities
- `POST /api/scenes/hasTriggers` — Check if scenes have triggers
  ```json
  { "sceneIds": [1, 2, 3] }
  ```
- `POST /api/scenes/{sceneID}/copy` — Copy scene
  ```json
  { "newName": "Copied Scene", "roomId": 2 }
  ```
- `POST /api/scenes/{sceneID}/convert` — Convert scene format
  ```json
  { "targetFormat": "lua", "preserveStructure": true }
  ```
- `POST /api/scenes/{sceneID}/copyAndConvert` — Copy and convert
  ```json
  { "newName": "Converted Copy", "targetFormat": "lua", "roomId": 2 }
  ```

### Lua Examples
```lua
api.post("/scenes/10/execute", {})
api.post("/scenes/10/kill", { force = true })

-- Preferred Lua API (within QA):
fibaro.scene("execute", {10})
fibaro.scene("kill", {10})
```

---

## Profiles (9 endpoints)

### Profile Management
- `GET /api/profiles` — Get all user profiles
- `POST /api/profiles` — Create new profile
  ```json
  { "name": "Evening Mode", "iconId": 5, "sourceId": 0 }
  ```
- `GET /api/profiles/{profileId}` — Get specific profile
- `PUT /api/profiles/{profileId}` — Update profile
  ```json
  {
    "name": "Updated Evening Mode", "iconId": 7,
    "devices": [{ "id": 1, "action": { "name": "turnOn", "args": [] } }],
    "scenes": [{ "sceneId": 10, "actions": ["start"] }]
  }
  ```
- `DELETE /api/profiles/{profileId}` — Delete profile
- `PUT /api/profiles` — Update global profile settings (`{ "activeProfile": 1 }`)

### Profile Associations
- `PUT /api/profiles/{profileId}/partitions/{partitionId}` — Associate with alarm partition
  ```json
  { "action": "arm" }
  ```
- `PUT /api/profiles/{profileId}/climateZones/{zoneId}` — Associate with climate zone
  ```json
  { "mode": "heating", "properties": { "handSetPointHeating": 22.0, "handMode": "manual" } }
  ```
- `PUT /api/profiles/{profileId}/scenes/{sceneId}` — Associate with scene
  ```json
  { "actions": ["start", "stop"] }
  ```

### Profile Actions
- `POST /api/profiles/reset` — Reset profiles to defaults
- `POST /api/profiles/activeProfile/{profileId}` — Set active profile

### Lua Examples
```lua
fibaro.profile(3, "activateProfile")
api.post("/profiles/activeProfile/3", {})
local profiles = api.get("/profiles")
```

---

## Custom Events (7 endpoints)

### Event Management
- `GET /api/customEvents` — List all custom events
- `POST /api/customEvents` — Create custom event
  ```json
  { "name": "MotionAlert", "userDescription": "Triggered when motion detected" }
  ```
- `GET /api/customEvents/{name}` — Get event details
- `PUT /api/customEvents/{name}` — Update event
  ```json
  { "name": "MotionAlert", "userDescription": "Updated description" }
  ```
- `DELETE /api/customEvents/{name}` — Delete custom event

### Event Triggering
- `POST /api/customEvents/{name}` — Emit event (POST)
- `GET /api/customEvents/{name}/publish` — Emit event (GET)

### Lua Examples
```lua
api.post("/customEvents/MotionAlert", {})
-- Preferred Lua API:
fibaro.emitCustomEvent("MotionAlert")
```

---

## Global Variables (4 endpoints)

### Variable Management
- `GET /api/globalVariables` — List all global variables
- `POST /api/globalVariables` — Create global variable
  ```json
  { "name": "HomeMode", "value": "Home", "isEnum": false, "enumValues": [], "readOnly": false }
  ```
- `GET /api/globalVariables/{name}` — Get variable; returns `{name, value, modified}`
- `PUT /api/globalVariables/{name}` — Update variable value
  ```json
  { "name": "HomeMode", "value": "Away" }
  ```
- `DELETE /api/globalVariables/{name}` — Delete variable

### Lua Examples
```lua
local gv = api.get("/globalVariables/HomeMode")
print(gv.value)
api.put("/globalVariables/HomeMode", { value = "Away" })

-- Preferred Lua API (within QA):
local mode = fibaro.getGlobalVariable("HomeMode")
fibaro.setGlobalVariable("HomeMode", "Away")
```
