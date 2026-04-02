---
name: quickapp-patterns
description: Common QuickApp implementation patterns: timer polling loops, cancellable timers, retry on failure, async HTTP requests (net.HTTPClient), refreshStates event polling (listening for HC3 device changes), RefreshStateSubscriber class, child device patterns, global variable access, state persistence (QA variables, internalStorage), UI update patterns, calling other devices, time-based schedulers, sending notifications. USE FOR: implementing recurring tasks, reacting to HC3 events, making HTTP calls, managing child devices, keeping state across restarts.
---

# QuickApp Common Patterns

Practical patterns for timers, event polling, HTTP, networking, child devices, and common QuickApp tasks.

---

## Timer Patterns

### Polling loop (setInterval)
```lua
function QuickApp:onInit()
    self.pollInterval = tonumber(self:getVariable("interval")) * 1000 or 30000
    setInterval(function() self:poll() end, self.pollInterval)
    self:poll()  -- also run immediately on start
end

function QuickApp:poll()
    -- your polling logic
    self:updateProperty("value", getReading())
end
```

### One-shot delayed action
```lua
setTimeout(function()
    self:doSomething()
end, 5000)
```

### Cancellable timer
```lua
function QuickApp:onInit()
    self.timer = nil
    self:startTimer()
end

function QuickApp:startTimer()
    if self.timer then clearTimeout(self.timer) end
    self.timer = setTimeout(function()
        self:doWork()
        self.timer = nil
    end, 10000)
end
```

### Retry after failure
```lua
function QuickApp:fetchWithRetry(attempt)
    attempt = attempt or 1
    if attempt > 3 then
        self:error("Failed after 3 attempts")
        return
    end
    local ok, data = pcall(function() return self:doFetch() end)
    if not ok then
        self:warning("Attempt", attempt, "failed, retrying in 5s")
        setTimeout(function() self:fetchWithRetry(attempt + 1) end, 5000)
    end
end
```

---

## HTTP Requests

### GET request
```lua
function QuickApp:fetchData()
    local http = net.HTTPClient()
    http:request("https://api.example.com/status", {
        options = { method = "GET" },
        success = function(response)
            if response.status == 200 then
                local data = json.decode(response.data)
                self:updateProperty("value", data.value)
            else
                self:warning("HTTP", response.status)
            end
        end,
        error = function(err)
            self:error("HTTP error:", tostring(err))
        end
    })
end
```

### POST request with JSON body
```lua
function QuickApp:sendCommand(cmd, payload)
    local http = net.HTTPClient()
    http:request("https://api.example.com/command", {
        options = {
            method = "POST",
            headers = {
                ["Content-Type"] = "application/json",
                ["Authorization"] = "Bearer " .. self:getVariable("token")
            },
            data = json.encode({ command = cmd, data = payload })
        },
        success = function(response)
            self:debug("Response:", response.status)
        end,
        error = function(err)
            self:error("POST failed:", tostring(err))
        end
    })
end
```

### Local HC3 REST API calls (synchronous via api.*)
```lua
-- These are synchronous and safe to use in onInit or timer callbacks
local device = api.get("/devices/" .. self.id)
local vars = api.get("/globalVariables")
local result = api.post("/customEvents/myEvent", {})
api.put("/devices/" .. self.id, { name = "New Name" })
```

---

## RefreshStates — Listening for HC3 Events

`refreshStates` is the HC3 long-polling mechanism to receive device property changes, custom events, and scene triggers in near-real-time.

### Pattern: polling refreshStates in a QuickApp

```lua
function QuickApp:onInit()
    self.lastRefresh = 0
    self:startRefreshPolling()
end

function QuickApp:startRefreshPolling()
    local function poll()
        local url = "/refreshStates?last=" .. self.lastRefresh
        local http = net.HTTPClient()
        http:request("http://localhost:11112" .. url, {
            options = { method = "GET", timeout = 5000 },
            success = function(response)
                if response.status == 200 then
                    local data = json.decode(response.data)
                    self.lastRefresh = data.last or self.lastRefresh
                    self:processEvents(data.changes or {})
                end
                setTimeout(function() poll() end, 0)
            end,
            error = function(err)
                self:warning("refreshStates error, retrying in 3s")
                setTimeout(function() poll() end, 3000)
            end
        })
    end
    poll()
end

function QuickApp:processEvents(changes)
    for _, change in ipairs(changes) do
        self:debug("Device", change.id, "property", change.name, "=", tostring(change.newValue))
        if change.id == 42 and change.name == "value" then
            self:onDeviceTriggered(change.newValue)
        end
    end
end
```

### Using the built-in RefreshStateSubscriber class

> **Prefer this over polling.** `RefreshStateSubscriber` listens to the HC3 event stream, so it reacts immediately when a device changes state — no waiting for the next poll interval. It is also more efficient because no repeated HTTP requests are made to fetch device state.

`subscribe(filter, handler)` — `filter(event)` is called first; if it returns `true`, `handler(event)` is called. A common pattern is to pass a filter that always returns `true` and do all filtering inside the handler.

```lua
function QuickApp:onInit()
    self.rss = RefreshStateSubscriber()

    -- filter always returns true; handler does the filtering
    self.rss:subscribe(
        function(event) return true end,
        function(event)
            if event.type == "DevicePropertyUpdatedEvent" then
                local id = event.data.id
                local prop = event.data.property
                local val = event.data.newValue
                self:debug("Device", id, prop, "->", tostring(val))
            end
        end
    )

    self.rss:run()
end

function QuickApp:onDestroy()
    if self.rss then self.rss:stop() end
end
```

### Narrowing with a real filter
```lua
-- Only invoke handler for a specific device's value changes
self.rss:subscribe(
    function(event)
        return event.type == "DevicePropertyUpdatedEvent"
            and event.data.id == watchedId
            and event.data.property == "value"
    end,
    function(event)
        self:applyValue(event.data.newValue)
    end
)
```

### Listening for CustomEvents
```lua
self.rss:subscribe(
    function(event) return true end,
    function(event)
        if event.type == "CustomEvent" and event.data.name == "myEvent" then
            self:debug("Custom event received!")
        end
    end
)
```

---

## Child Device Patterns

### Defining a child class
```lua
class 'MyChild'(QuickAppChild)

function MyChild:__init(device)
    QuickAppChild.__init(self, device)
end

function MyChild:onInit()
    self:debug("Child", self.id, "started")
end

function MyChild:turnOn()
    self:updateProperty("value", true)
end

function MyChild:turnOff()
    self:updateProperty("value", false)
end
```

### Creating children from the parent
```lua
function QuickApp:onInit()
    self:initChildDevices({ ["com.fibaro.binarySwitch"] = MyChild })

    if #api.get("/devices?parentId=" .. self.id) == 0 then
        self:createChildDevice({
            name = "Channel 1",
            type = "com.fibaro.binarySwitch",
            initialProperties = { value = false }
        }, MyChild)
    end
end
```

### Calling parent from child
```lua
function MyChild:doSomething()
    -- self.parent is available after __init in child's onInit()
    self.parent:debug("Child reporting to parent")
    self.parent:updateProperty("log", "Child " .. self.id .. " active")
end
```

> **For more advanced child management** — UID-based addressing, declarative `initChildren`, per-child UI, and `internalStorage` per child — use the plua **QwikAppChild** library. Ask `/qwikchild` for full details.

---

## Variable Storage — When to Use What

| Storage | Visible in UI | Saved with QA | Shared across QAs | Use for |
|---|---|---|---|---|
| **Fibaro Global Variable** | No | No | Yes | System-wide values shared by multiple QAs or Scenes (e.g. `HomeMode`, `AlarmArmed`) |
| **QuickApp variable** (`self:getVariable`) | Yes | Yes | No | User-configurable parameters (API keys, IP addresses, poll intervals) — shown in the QA panel and exported with the QA `.fqa` file |
| **internalStorage** | No | No | No | Private runtime state that must survive QA restarts but should not be visible or user-editable (e.g. last-seen timestamps, cached values, counters) |

> **Fibaro Global Variables** are the right choice when a value needs to be read or written by more than one QuickApp or Scene.

> **QuickApp variables** are the right choice for settings the user may want to change — they appear in the HC3 UI under the device panel and are bundled into the QA when it is downloaded as a `.fqa` file.

> **internalStorage** stores arbitrary Lua values (tables, strings, numbers, booleans — anything JSON-encodable). You do **not** need to call `json.encode`/`json.decode` yourself; the API handles serialisation transparently. Functions cannot be stored.

---

## Global Variable Patterns

```lua
local mode = fibaro.getGlobalVariable("HomeMode")
fibaro.setGlobalVariable("HomeMode", "Away")

-- Alternative via api.*
local gv = api.get("/globalVariables/HomeMode")
print(gv.value)
api.put("/globalVariables/HomeMode", { value = "Home" })
```

---

## State Persistence

### Using QuickApp variables (user-visible, saved with QA)
```lua
function QuickApp:onInit()
    -- Read user-configured parameter set in the HC3 UI
    local interval = tonumber(self:getVariable("pollInterval")) or 30
    self.pollInterval = interval * 1000
end
```

### Saving runtime state across restarts with QuickApp variables
```lua
function QuickApp:setState(val)
    self.state = val
    self:setVariable("savedState", tostring(val))
    self:updateProperty("value", val)
end

function QuickApp:onInit()
    local saved = self:getVariable("savedState")
    self.state = saved == "true"
end
```

### Using internalStorage (private, not user-visible)
```lua
-- Store any JSON-encodable Lua value — no manual json.encode needed
self:internalStorageSet("lastSeen", os.time())
self:internalStorageSet("cache", { temp = 21.5, hum = 55 })

local ts    = self:internalStorageGet("lastSeen")   -- nil if not set
local cache = self:internalStorageGet("cache")       -- returns Lua table directly
self:internalStorageRemove("lastSeen")
self:internalStorageClear()
```

---

## Error Handling

```lua
local ok, result = pcall(function()
    return json.decode(rawData)
end)
if not ok then
    self:error("JSON parse failed:", result)
    return
end

local function safeGet(path)
    local resp = api.get(path)
    if not resp then
        return nil, "API call failed: " .. path
    end
    return resp, nil
end
```

---

## UI Update Patterns

```lua
self:updateView("statusLabel", "text", "Connected")
self:updateView("tempSlider", "value", tostring(math.floor(temp)))
self:updateView("toggleBtn", "text", self.active and "Deactivate" or "Activate")
self:updateView("advancedPanel", "visible", "false")
self:updateView("modeSelect", "value", tostring(selectedMode))
```

---

## Calling Other Devices

```lua
fibaro.call(42, "turnOn")
fibaro.call(42, "setValue", 75)
local val = fibaro.getValue(42, "value")
self:turnOn()  -- prefer self:method() over fibaro.call(self.id, ...) for self
```

---

## Scheduler / Time-Based Actions

```lua
function QuickApp:onInit()
    setInterval(function() self:checkTime() end, 60000)
end

function QuickApp:checkTime()
    local hour   = tonumber(os.date("%H"))
    local minute = tonumber(os.date("%M"))

    if hour == 7 and minute == 0 then
        fibaro.call(10, "turnOn")
    elseif hour == 23 and minute == 0 then
        fibaro.call(10, "turnOff")
    end
end
```

---

## Sending Notifications

```lua
fibaro.alert("push", {1}, "Motion detected!")
fibaro.alert("email", {1}, "Temperature too high: " .. temp .. "°C")
fibaro.emitCustomEvent("MotionAlert")
```
