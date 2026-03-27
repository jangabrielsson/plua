# HC3 REST API — Energy & Climate

Full reference for Energy (25), Consumption (6), Climate Panel (7), Humidity Panel (5), and Sprinklers Panel (9) endpoints.

---

## Energy (25 endpoints)

### Device and Consumption Monitoring
- `GET /api/energy/devices` — List energy-enabled devices
- `GET /api/energy/consumption/summary` — Overall energy consumption summary
- `GET /api/energy/consumption/metrics` — Energy consumption metrics
- `GET /api/energy/consumption/detail` — Detailed consumption data
- `GET /api/energy/consumption/room/{roomId}/detail` — Room-specific consumption
- `GET /api/energy/consumption/device/{deviceId}/detail` — Device-specific consumption
- `DELETE /api/energy/consumption` — Delete consumption data
  ```json
  { "deviceIds": [1, 2, 3], "startPeriod": "2025-01-01", "endPeriod": "2025-01-31" }
  ```

### Billing Management
- `GET /api/energy/billing/summary` — Billing summary
- `GET /api/energy/billing/periods` — Billing periods
- `POST /api/energy/billing/periods` — Create billing period
  ```json
  { "duration": "1", "startDate": "2025-01-01", "fixedCost": 25.50 }
  ```
  duration: months (1, 2, 3, 6, 12)
- `GET /api/energy/billing/tariff` — Current tariff
- `PUT /api/energy/billing/tariff` — Update tariff
  ```json
  {
    "rate": 0.15, "name": "Standard",
    "additionalTariffs": [
      { "rate": 0.22, "name": "Peak", "startTime": "17:00", "endTime": "21:00",
        "days": ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY"] }
    ]
  }
  ```

### Installation Costs
- `GET /api/energy/installationCost` — All installation costs
- `POST /api/energy/installationCost` — Add cost entry
  ```json
  { "date": "2025-01-15", "cost": 5000.00, "name": "Solar Panel Installation" }
  ```
- `GET /api/energy/installationCost/{id}` — Get specific cost
- `PUT /api/energy/installationCost/{id}` — Update cost
- `DELETE /api/energy/installationCost/{id}` — Delete cost

### Savings and Ecology
- `GET /api/energy/savings/detail` — Savings detail
- `GET /api/energy/savings/summary` — Savings summary
- `GET /api/energy/savings/installation` — Installation savings
- `GET /api/energy/ecology/summary` — Environmental impact summary
- `GET /api/energy/ecology/detail` — Detailed ecology metrics

### Settings
- `GET /api/energy/settings` — Energy system settings
- `PUT /api/energy/settings` — Update energy settings
  ```json
  {
    "consumptionMeasurement": "kWh",
    "energyConsumptionMeters": [1, 2, 3],
    "energyProductionMeters": [4, 5],
    "gridConsumptionMeters": [1],
    "gridProductionMeters": [4]
  }
  ```

---

## Consumption Panel (6 endpoints)

- `GET /api/panels/energy?details=summary&period={period}` — Energy summary by period
- `GET /api/panels/energy?id={id}` — Energy data for specific device
- `GET /api/panels/energy?details=billing&period={period}` — Billing details
- `GET /api/panels/energy?details=savings&period={period}` — Savings information
- `GET /api/panels/energy?details=ranking&period={period}` — Device ranking by consumption
- `GET /api/panels/energy?details=ecology&period={period}` — Ecology impact data

Period values: `hour`, `day`, `week`, `month`, `year`

---

## Climate Panel (7 endpoints)

### Climate Zone Management
- `GET /api/panels/climate` — List all climate zones
- `POST /api/panels/climate` — Create climate zone
  ```json
  {
    "name": "Living Room Climate", "devices": [1, 2, 3],
    "handMode": "manual", "handSetPointHeating": 21.0, "handSetPointCooling": 25.0,
    "scheduleHeating": {
      "monday": {
        "morning": {"hour": 6, "minute": 0, "temperature": 20.0},
        "evening": {"hour": 18, "minute": 0, "temperature": 21.0},
        "night": {"hour": 22, "minute": 0, "temperature": 17.0}
      }
    }
  }
  ```
- `GET /api/panels/climate/{climateID}` — Get climate zone details
- `PUT /api/panels/climate/{climateID}` — Update climate zone
  ```json
  { "name": "Updated Zone", "handSetPointHeating": 22.0, "mode": "heating", "devices": [1,2,3] }
  ```
- `DELETE /api/panels/climate/{climateID}` — Delete climate zone
- `POST /api/panels/climate/action/createDefaultZones` — Create default zones
- `GET /api/panels/climate/availableDevices` — List available climate devices

---

## Humidity Panel (5 endpoints)

- `GET /api/panels/humidity` — List all humidity zones
- `POST /api/panels/humidity` — Create humidity zone
  ```json
  { "name": "Bedroom Humidity" }
  ```
- `GET /api/panels/humidity/{humidityID}` — Get zone details
- `PUT /api/panels/humidity/{humidityID}` — Update zone
  ```json
  {
    "name": "Updated Zone",
    "properties": {
      "handHumidity": 50.0, "vacationHumidity": 40.0, "rooms": [1, 2],
      "monday": { "morning": {"hour":6,"minute":0,"humidity":45.0} }
    }
  }
  ```
- `DELETE /api/panels/humidity/{humidityID}` — Delete zone

---

## Sprinklers Panel (9 endpoints)

### Schedule Management
- `GET /api/panels/sprinklers` — All sprinkler schedules
- `POST /api/panels/sprinklers` — Create schedule
  ```json
  { "name": "Garden Schedule" }
  ```
- `GET /api/panels/sprinklers/{scheduleId}` — Get schedule
- `PUT /api/panels/sprinklers/{scheduleId}` — Update schedule
  ```json
  {
    "name": "Updated Schedule", "days": ["MONDAY","WEDNESDAY","FRIDAY"],
    "sequences": [{ "startTime": 21600, "sprinklers": [{"deviceId":10,"duration":1800}] }],
    "isActive": true
  }
  ```
- `DELETE /api/panels/sprinklers/{scheduleId}` — Delete schedule

### Sequence Management
- `POST /api/panels/sprinklers/{scheduleId}/sequences` — Create sequence
  ```json
  { "startTime": 21600, "sprinklers": [{"deviceId":10,"duration":1800},{"deviceId":11,"duration":900}] }
  ```
- `PUT /api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}` — Update sequence
- `DELETE /api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}` — Delete sequence

### Watering Control
- `POST /api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}/startWatering` — Start watering
  ```json
  { "duration": 1800, "zones": [1, 2, 3] }
  ```
- `POST /api/panels/sprinklers/{scheduleId}/sequences/{sequenceId}/stopWatering` — Stop watering
  ```json
  { "immediate": true }
  ```
