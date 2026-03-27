# HC3 REST API — Panels, Data & Miscellaneous

Full reference for Panels/UI (20), Data & Monitoring (13), and Miscellaneous (16) endpoints.

---

## Panels & UI

### Notification Center (4 endpoints)
- `POST /api/notificationCenter` — Create notification
  ```json
  {
    "priority": "info", "wasRead": false, "canBeDeleted": true,
    "type": "GenericSystemNotificationRequest",
    "data": { "title": "System Alert", "text": "Maintenance scheduled", "subType": "Generic" }
  }
  ```
- `GET /api/notificationCenter/{id}` — Get notification
- `PUT /api/notificationCenter/{id}` — Edit notification
  ```json
  { "priority": "warning", "wasRead": true, "data": { "title": "Updated Alert" } }
  ```
- `DELETE /api/notificationCenter/{id}` — Delete notification

### Notification Panel (4 endpoints)
- `GET /api/panels/notifications` — List panel notifications
- `POST /api/panels/notifications` — Create panel notification
  ```json
  { "name": "Door Alert" }
  ```
- `GET /api/panels/notifications/{id}` — Get panel notification
- `PUT /api/panels/notifications/{id}` — Modify panel notification
  ```json
  { "name": "Updated Alert", "sms": "enabled", "email": "enabled", "push": "disabled" }
  ```
- `DELETE /api/panels/notifications/{id}` — Delete notification

### Location Panel (5 endpoints)
- `GET /api/panels/location` — List all locations
- `POST /api/panels/location` — Create location
  ```json
  { "name": "Home", "address": "123 Main St", "longitude": -74.006, "latitude": 40.7128, "radius": 100 }
  ```
- `GET /api/panels/location/{id}` — Get location
- `PUT /api/panels/location/{id}` — Update location
- `DELETE /api/panels/location/{id}` — Delete location

### Family Panel (1 endpoint)
- `GET /api/panels/family` — Get family user tracking data (supports time range query params)

### Favorite Colors (6 endpoints)

Used for color picker presets in RGB/color devices.

**v1 API:**
- `GET /api/panels/favoriteColors` — Get favorite colors
- `POST /api/panels/favoriteColors` — Create color
  ```json
  { "r": 255, "g": 128, "b": 0, "w": 0, "brightness": 80 }
  ```
- `PUT /api/panels/favoriteColors/{id}` — Update color
- `DELETE /api/panels/favoriteColors/{id}` — Delete color

**v2 API:**
- `GET /api/panels/favoriteColors/v2` — Get favorite colors (v2)
- `POST /api/panels/favoriteColors/v2` — Create color (v2)
  ```json
  { "colorComponents": { "red": 255, "green": 128, "blue": 0, "warmWhite": 0 }, "brightness": 80 }
  ```

---

## Data & Monitoring

### Debug Messages (3 endpoints)
- `GET /api/debugMessages` — Recent debug messages (supports level/source filtering)
- `DELETE /api/debugMessages` — Clear messages
  ```json
  { "level": "error", "beforeTimestamp": 1640995200, "source": "scenes" }
  ```
- `GET /api/debugMessages/tags` — Available debug tags

### Diagnostics (2 endpoints)
- `GET /api/diagnostics` — System diagnostic information
- `GET /api/apps/com.fibaro.zwave/diagnostics/transmissions` — Z-Wave transmission diagnostics

### Refresh States (1 endpoint)
- `GET /api/refreshStates?last={lastKnown}` — Get device state changes since last poll

Response:
```json
{
  "last": 12345,
  "changes": [{ "id": 42, "name": "value", "newValue": true, "oldValue": false }],
  "events": [{ "type": "CustomEvent", "data": { "name": "myEvent" } }]
}
```

```lua
local data = api.get("/refreshStates?last=" .. self.lastRefresh)
self.lastRefresh = data.last
for _, change in ipairs(data.changes or {}) do
    self:debug(change.id, change.name, "->", tostring(change.newValue))
end
```

### Weather (1 endpoint)
- `GET /api/weather` — Current weather data

Fields: `Temperature`, `TemperatureUnit`, `Humidity`, `Wind`, `WindUnit`, `WeatherCondition`, `ConditionCode`, `Visibility`, `VisibilityUnit`, `Rain`, `LastUpdated`.

```lua
local w = api.get("/weather")
print(w.Temperature, w.WeatherCondition)
```

### iOS Devices (1 endpoint)
- `GET /api/iosDevices` — Registered iOS devices (mobile app registrations)

### Device Notifications (4 endpoints)
- `GET /api/deviceNotifications/v1` — List device notifications
- `GET /api/deviceNotifications/v1/{deviceID}` — Get device notification settings
- `PUT /api/deviceNotifications/v1/{deviceID}` — Update device notifications
  ```json
  {
    "enabled": true,
    "notifications": [
      { "type": "value_change", "threshold": 50, "condition": "greater_than" },
      { "type": "device_unreachable", "enabled": true }
    ]
  }
  ```
- `DELETE /api/deviceNotifications/v1/{deviceID}` — Delete device notifications

### History Events (2 endpoints)
- `GET /api/events/history` — Historical events (supports extensive filtering by type, time, device)
- `DELETE /api/events/history` — Delete historical events
  ```json
  { "eventType": "CentralSceneEvent", "objectType": "device", "objectId": 25 }
  ```

---

## Miscellaneous

### Icons (3 endpoints)
- `GET /api/icons` — List available icons
- `POST /api/icons` — Upload new icon
  ```json
  { "name": "my_icon", "content": "data:image/png;base64,..." }
  ```
- `DELETE /api/icons` — Delete icon
  ```json
  { "type": "custom", "name": "my_icon", "fileExtension": "svg" }
  ```

### RGB Programs (5 endpoints)
- `GET /api/RGBPrograms` — List all RGB programs
- `POST /api/RGBPrograms` — Create RGB program
  ```json
  {
    "name": "Sunset", "description": "Warm gradient",
    "steps": [
      { "duration": 5000, "color": {"r": 255, "g": 140, "b": 0} },
      { "duration": 3000, "color": {"r": 255, "g": 69, "b": 0} }
    ]
  }
  ```
- `GET /api/RGBPrograms/{id}` — Get program details
- `PUT /api/RGBPrograms/{id}` — Modify program
- `DELETE /api/RGBPrograms/{id}` — Delete program

### Push Notifications (3 endpoints)
- `POST /api/mobile/push` — Send push notification
  ```json
  { "title": "Home Alert", "message": "Motion detected", "category": "security", "badge": 1 }
  ```
- `POST /api/mobile/push/{id}` — Execute push action (`{ "action": "dismiss" }`)
- `DELETE /api/mobile/push/{id}` — Delete push notification

### System Status (3 endpoints)
- `GET /api/service/systemStatus` — Get system status
- `POST /api/service/systemStatus` — Set system status
  ```json
  { "status": "maintenance", "message": "Update in progress", "estimatedTime": 1800 }
  ```
- `POST /api/service/restartServices` — Clear system errors
  ```json
  { "services": ["scenes", "devices", "plugins"], "force": false }
  ```

### System Control
- `POST /api/service/factoryReset` — Perform factory reset (**destructive**)
- `POST /api/service/reboot` — Reboot the system

### UI Sort Order
- `POST /api/sortOrder` — Update UI element sort order

### Home Information
- `GET /api/home` — Get home information and settings
- `PUT /api/home` — Update home settings

### User Activity
- `GET /api/userActivity` — Get user activity list
