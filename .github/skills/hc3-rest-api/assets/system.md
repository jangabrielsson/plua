# HC3 REST API — System Configuration

Full reference for Network (19), Users (8), Alarms (16), Rooms (7), and Sections (5) endpoints.

---

## Network (19 endpoints)

### Interface Configuration
- `GET /api/settings/network/interfaces` — List all network interfaces
- `GET /api/settings/network/interfaces/{interfaceName}` — Get interface configuration
- `PUT /api/settings/network/interfaces/{interfaceName}` — Update interface settings
- `GET /api/settings/network/interfaces/{interfaceName}/apList` — List access points
- `GET /api/settings/network/interfaces/{interfaceName}/apInfo` — Access point info

### Connection Management
- `GET /api/settings/network/connections` — List network connections
- `POST /api/settings/network/connections` — Add connection
  ```json
  {
    "name": "MyWiFi", "enabled": true,
    "apConfig": { "ssid": "MyWiFi", "security": "WPA2", "password": "pass" },
    "ipConfig": { "ipMode": "dhcp" }
  }
  ```
- `GET /api/settings/network/connections/{uuid}` — Get connection status
- `PUT /api/settings/network/connections/{uuid}` — Update connection
  ```json
  {
    "apConfig": { "ssid": "NewSSID", "security": "WPA3" },
    "ipConfig": { "ipMode": "static", "ip": "192.168.1.100", "mask": "255.255.255.0",
                  "gateway": "192.168.1.1", "dns1": "8.8.8.8" }
  }
  ```
- `DELETE /api/settings/network/connections/{uuid}` — Remove connection
- `POST /api/settings/network/connections/{uuid}/check` — Check connection
- `POST /api/settings/network/connections/{uuid}/connect` — Connect wifi
  ```json
  { "password": "wifi_password", "auto": true }
  ```
- `POST /api/settings/network/connections/{uuid}/disconnect` — Disconnect wifi

### Radio Configuration
- `GET /api/settings/network/radio` — Get radio configuration
- `PUT /api/settings/network/radio` — Update radio settings
  ```json
  { "zwave": { "enabled": true }, "zigbee": { "enabled": false } }
  ```
- `GET /api/settings/network/radio/{radioType}` — Get radio by type
- `PUT /api/settings/network/radio/{radioType}` — Update radio by type

### Network Information
- `GET /api/settings/network` — All network configurations
- `GET /api/settings/network/connectivity` — Internet connectivity status
- `PUT /api/settings/network/resetInterfaces` — Reset network interfaces
- `GET /api/settings/network/AccessPointMode` — Access point status
- `PUT /api/settings/network/AccessPointMode` — Set access point mode
  ```json
  { "accessPointEnabled": true }
  ```
- `GET /api/settings/network/enabledProtocols` — Get enabled protocols
- `PUT /api/settings/network/enabledProtocols` — Set enabled protocols
  ```json
  { "http": true, "https": true }
  ```

---

## Users (8 endpoints)

### User Management
- `GET /api/users` — List all users
- `POST /api/users` — Create user
  ```json
  { "email": "user@example.com", "name": "John Doe", "type": "guest" }
  ```
- `GET /api/users/{userID}` — Get user details
- `PUT /api/users/{userID}` — Update user
  ```json
  {
    "name": "John Smith", "email": "j@example.com", "type": "guest",
    "pin": "1234", "sendNotifications": true, "tracking": 1,
    "alarmRights": [1, 2], "climateZoneRights": [1], "profileRights": [1,2,3]
  }
  ```
- `DELETE /api/users/{userID}` — Delete user

### User Actions
- `POST /api/users/{userID}/raInvite` — Send remote access invite
- `POST /api/users/action/changeAdmin/{newAdminId}` — Change admin user
  ```json
  { "currentAdminPin": "1234" }
  ```
- `POST /api/users/action/confirmAdminTransfer` — Confirm admin transfer
- `POST /api/users/action/cancelAdminTransfer` — Cancel admin transfer
- `POST /api/users/action/synchronize` — Synchronize users

---

## Alarms (16 endpoints)

### Partition Management
- `GET /api/alarms/v1/partitions` — List all alarm partitions
- `POST /api/alarms/v1/partitions` — Create partition
  ```json
  { "name": "Ground Floor", "armDelay": 30, "breachDelay": 60, "devices": [1,2,3] }
  ```
- `GET /api/alarms/v1/partitions/{partitionID}` — Get partition details
- `PUT /api/alarms/v1/partitions/{partitionID}` — Update partition
- `DELETE /api/alarms/v1/partitions/{partitionID}` — Delete partition

### System Arming
- `POST /api/alarms/v1/partitions/actions/tryArm` — Try to arm all partitions
  ```json
  { "armingType": "full" }
  ```
- `POST /api/alarms/v1/partitions/actions/arm` — Arm all partitions
- `DELETE /api/alarms/v1/partitions/actions/arm` — Disarm all partitions

### Individual Partition Control
- `POST /api/alarms/v1/partitions/{id}/actions/tryArm` — Try arm partition
  ```json
  { "armingType": "partial" }
  ```
- `POST /api/alarms/v1/partitions/{id}/actions/arm` — Arm partition
  ```json
  { "armingType": "night" }
  ```
- `DELETE /api/alarms/v1/partitions/{id}/actions/arm` — Disarm partition

### Monitoring
- `GET /api/alarms/v1/history` — Alarm history with filtering
- `GET /api/alarms/v1/partitions/breached` — Get breached partition IDs
- `GET /api/alarms/v1/devices` — Alarm system devices

### Lua Examples
```lua
api.post("/alarms/v1/partitions/1/actions/arm", { armingType = "full" })
-- Preferred Lua API:
fibaro.alarm(1, "arm")
fibaro.alarm(1, "disarm")
```

---

## Rooms (7 endpoints)

### Room Management
- `GET /api/rooms` — List all rooms
- `POST /api/rooms` — Create room
  ```json
  { "name": "Living Room", "sectionID": 1, "category": "living", "visible": true }
  ```
- `GET /api/rooms/{roomID}` — Get room details
- `PUT /api/rooms/{roomID}` — Update room
  ```json
  {
    "name": "Updated Living Room", "sectionID": 1,
    "defaultSensors": { "temperature": 1, "humidity": 2 },
    "defaultThermostat": 10
  }
  ```
- `DELETE /api/rooms/{roomID}` — Delete room
- `POST /api/rooms/{roomID}/action/setAsDefault` — Set room as default
- `POST /api/rooms/{roomID}/groupAssignment` — Assign devices to room group
  ```json
  { "deviceIds": [1, 2, 3] }
  ```

### Lua Examples
```lua
local rooms = api.get("/rooms")
local living = api.get("/rooms/5")
print(living.name)
```

---

## Sections (5 endpoints)

- `GET /api/sections` — List all sections
- `POST /api/sections` — Create section
  ```json
  { "name": "Ground Floor" }
  ```
- `GET /api/sections/{sectionID}` — Get section details
- `PUT /api/sections/{sectionID}` — Update section
  ```json
  { "name": "Updated Ground Floor", "sortOrder": 1 }
  ```
- `DELETE /api/sections/{sectionID}` — Delete section
