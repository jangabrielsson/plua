# EventLib v0.52 - Advanced Event Handling for Fibaro HC3

**Author:** Jan Gabrielsson (jan@gabrielsson.com)  
**License:** GNU GPL v3  
**Forum:** https://forum.fibaro.com/topic/74161-eventlib/

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [API Reference](#api-reference)
  - [Event Declaration](#event-declaration)
  - [Event Types](#event-types)
  - [Pattern Matching](#pattern-matching)
  - [Time Specifications](#time-specifications)
  - [Handler Methods](#handler-methods)
- [Advanced Features](#advanced-features)
- [Resource Helpers](#resource-helpers)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

EventLib is a powerful event-driven programming library for Fibaro Home Center 3 (HC3). It provides a declarative, reactive approach to automation scripting with advanced features like:

- **Pattern matching** with variable extraction and constraints
- **Scheduled events** with cron-like syntax and timer support
- **Event transformations** for complex event handling
- **State tracking** with `trueFor()` for debouncing and time-based conditions
- **Resource helpers** for cleaner device and global variable access
- **Clean, consistent API** for event handling

EventLib eliminates the need for manual polling and provides a clean, maintainable way to respond to HC3 events.

---

## Installation

1. Copy the entire `eventlib.lua` content into your QuickApp or Scene
2. The library will automatically initialize on first use
3. Initialize EventLib with: `Event = Event_std`

**Example:**
```lua
-- Load the library
Event = Event_std
fibaro.debugFlags.post = true  -- Enable debug logging (optional)

-- Attach to HC3 event stream at startup
Event.id = 'start'
Event{type='QAstart'}
function Event:handler(event)
  Event:attachRefreshstate()  -- Start receiving HC3 events
end
```

**Important:** Call `Event:attachRefreshstate()` in a `QAstart` handler to ensure all libraries are loaded first.

---

## Quick Start

### Basic Event Handler

```lua
Event = Event_std

-- React to device property changes
Event.id = 'myLight'
Event{type='device', id=123, property='value'}
function Event:handler(event)
  self:trace("Light changed to: " .. event.value)
end
```

### Timer Event

```lua
-- Execute every 10 seconds
Event.id = 'myTimer'
Event{type='timer', time='+/00:10'}
function Event:handler(event)
  self:debug("Timer triggered!")
end
```

### Anonymous Handlers

```lua
-- Use Event.id = '_' for quick one-off handlers
Event.id = '_'
Event{type='device', id=456, property='value'}
function Event:handler(event)
  if event.value > 50 then
    fibaro.call(123, "turnOn")
  end
end
```

### Complete QuickApp Startup

```lua
Event = Event_std

-- STEP 1: Initialize EventLib at startup (REQUIRED)
Event.id = 'start'
Event{type='QAstart'}
function Event:handler(event)
  Event:attachRefreshstate()  -- Connect to HC3 event stream
  self:debug("EventLib initialized")
end

-- STEP 2: Define your event handlers
Event.id = 'motionDetector'
Event{type='device', id=100, property='value'}
function Event:handler(event)
  if event.value > 0 then
    self:debug("Motion detected!")
    fibaro.call(200, "turnOn")  -- Turn on light
  end
end

Event.id = 'dailyReport'
Event{type='cron', time='0 8 * * *'}  -- Every day at 8:00
function Event:handler(event)
  self:debug("Daily report running...")
end
```

**Key Points:**
- Always attach RefreshState in a `QAstart` handler
- Define handlers after initialization
- Without `attachRefreshstate()`, device events won't trigger

---

## Core Concepts

### Event Declaration and Handler

EventLib uses a three-step pattern:

1. **Set the handler ID:**
   ```lua
   Event.id = 'myHandler'
   ```

2. **Declare what events to listen for:**
   ```lua
   Event{type='device', id=123, property='value'}
   ```

3. **Define what to do when the event occurs:**
   ```lua
   function Event:handler(event)
     -- Your code here
   end
   ```

**Note:** The function is always named `Event:handler` regardless of the handler ID.

### Optional Handler Properties

You can set additional properties before declaring events:

```lua
Event.id = 'myHandler'
Event.tag = 'DisplayName'      -- Optional: Display tag in logs
Event.tagColor = 'yellow'      -- Optional: Tag color (yellow, red, green, etc.)
Event.debug = true             -- Optional: Enable debug output

Event{type='device', id=123, property='value'}
function Event:handler(event)
  -- Your code
end
```

### Event Flow

1. HC3 generates an event (device change, custom event, etc.)
2. EventLib receives the event via `RefreshStateSubscriber`
3. Event is transformed and normalized
4. Pattern matching finds matching handlers
5. Handler function is called with event data

### The Handler Context (`self`)

Inside handlers, `self` provides useful methods and properties:

- `self.id` - Handler identifier
- `self._event` - Current event
- `self._match` - Pattern match results (captured variables)
- `self.date` - Timestamp of event
- Logging methods: `debug()`, `trace()`, `warning()`, `error()`
- Timer methods: `post()`, `cancel()`, `cancelAll()`, `timer()`
- State methods: `trueFor()`, `again()`
- Control methods: `enable()`, `disable()`

---

## API Reference

### Event Declaration

The Event_std API follows this pattern:

```lua
Event = Event_std  -- Initialize EventLib

-- Set handler ID (required)
Event.id = 'handlerName'

-- Set optional properties
Event.tag = 'MyTag'           -- Display name in logs
Event.tagColor = 'yellow'     -- Tag color
Event.debug = true            -- Enable debug output

-- Define event pattern
Event{type='...', ...}

-- Define handler function (always named "handler")
function Event:handler(event)
  -- Handler code
  -- Access matched values via self._match
end
```

**Anonymous Handler:**
```lua
-- Use '_' as ID for quick one-off handlers
Event.id = '_'
Event{type='...', ...}
function Event:handler(event)
  -- Handler code
end
```

**Complete Example:**
```lua
Event.id = 'temperatureAlert'
Event.tag = 'Climate'
Event.tagColor = 'red'
Event.debug = true

Event{type='device', id=50, property='value', value='$temp>25'}
function Event:handler(event)
  self:warning("High temperature: " .. self._match.temp .. "°C")
end
```

### Event Types

EventLib supports all HC3 event types:

#### Device Events
```lua
{type='device', id=<number>, property='value'}
{type='device', id=<number>, property='power'}
{type='device', id={123,456}, property='value'}  -- Multiple devices
{type='device', id=<number>, property='centralSceneEvent'}
{type='device', id=<number>, property='sceneActivationEvent'}
{type='device', id=<number>, property='accessControlEvent'}
```

#### Global Variables
```lua
{type='global-variable', name='myVar'}
```

#### QuickApp Variables
```lua
{type='quickvar', id=<qaId>, name='varName'}
{type='quickvar', id=<qaId>}  -- Any variable on this QA
```

#### Custom Events
```lua
{type='custom-event', name='myEvent'}
```

#### Profile Events
```lua
{type='profile', property='activeProfile'}
```

#### Weather Events
```lua
{type='weather', property='Temperature'}
{type='weather', property='Wind'}
```

#### Scene Events
```lua
{type='sceneEvent', id=<number>, value='started'}
{type='sceneEvent', id=<number>, value='finished'}
```

#### Device Lifecycle Events
```lua
{type='deviceEvent', id=<number>, value='created'}
{type='deviceEvent', id=<number>, value='modified'}
{type='deviceEvent', id=<number>, value='removed'}
{type='deviceEvent', id=<number>, value='crashed'}
```

#### Alarm Events
```lua
{type='alarm', property='armed', id=<partitionId>}
{type='alarm', property='breached', id=<partitionId>}
{type='alarm', property='homeArmed'}
```

#### Location Events
```lua
{type='location', id=<userId>, property=<locationId>}
```

#### Timer Events
```lua
{type='timer', time='10:30'}           -- Daily at 10:30
{type='timer', time='+/00:10'}         -- Every 10 minutes
{type='timer', time='t/10:30'}         -- Today at 10:30
{type='timer', time='n/sunset+10'}     -- Next sunset + 10 min
```

#### Cron Events
```lua
{type='cron', time='30 10 * * *'}      -- Daily at 10:30
{type='cron', time='*/5 * * * *'}      -- Every 5 minutes
{type='cron', time='0 8 * * mon-fri'}  -- Weekdays at 8:00
{type='cron', time='sunrise+10 * * *'} -- Sunrise + 10 min daily
```

#### System Events
```lua
{type='QAstart'}                        -- QuickApp started (initialization)
{type='function'}                       -- Internal function call
{type='schedule'}                       -- Internal scheduled event
```

**QAstart Event Usage:**
The `QAstart` event is posted when your QuickApp initializes. Use it to set up EventLib properly:

```lua
Event.id = 'start'
Event{type='QAstart'}
function Event:handler(event)
  Event:attachRefreshstate()  -- Enable HC3 event reception
  self:debug("EventLib initialized and attached to HC3 events")
end
```

**Why use QAstart?** You can't call `Event:attachRefreshstate()` immediately because all libraries must be loaded first. The `QAstart` event ensures proper initialization timing.

---

### Pattern Matching

EventLib supports powerful pattern matching with variable extraction and constraints.

#### Variable Extraction

Use `$variableName` to capture values from events:

```lua
Event.id = 'anyDevice'
Event{type='device', id=123, property='value', value='$val'}
function Event:handler(event)
  -- Access captured values via self._match
  self:trace("Device value: " .. self._match.val)
end
```

**Note:** Device `id` cannot use pattern matching as it's used for event hashing. Use fixed IDs or multiple IDs: `id={100,101,102}`

#### Constraints

Add constraints to variables using operators:

- `$var` - Any value (captures in `self._match.var`)
- `$_` - Any value (not captured, anonymous)
- `$var==<value>` - Equals
- `$var~=<value>` - Not equals
- `$var<><regex>` - Pattern match
- `$var><value>` - Greater than
- `$var<=<value>` - Less than or equal
- `$var>=<value>` - Greater than or equal
- `$var<<value>` - Less than

**Examples:**

```lua
-- Trigger only when value > 50
Event.id = 'highTemp'
Event{type='device', id=100, property='value', value='$_>50'}
function Event:handler(event)
  self:debug("High temperature detected")
end

-- Capture value with constraint
Event.id = 'lowBattery'
Event{type='device', id=200, property='batteryLevel', value='$level<20'}
function Event:handler(event)
  self:warning("Low battery: " .. self._match.level .. "%")
end

-- Pattern match on value property
Event.id = 'anyOn'
Event{type='device', id=150, property='value', value='$val>0'}
function Event:handler(event)
  self:debug("Device turned on with value: " .. self._match.val)
end
```

---

### Time Specifications

EventLib supports flexible time specifications:

#### Absolute Times

```lua
"10:30"        -- 10:30 (as seconds from midnight)
"10:30:45"     -- 10:30:45 with seconds
```

#### Relative Times (Prefixes)

```lua
"+/00:10"      -- 10 minutes from now (repeating with aligned option)
"t/10:30"      -- Today at 10:30
"n/10:30"      -- Next occurrence of 10:30 (today or tomorrow)
```

#### Sunrise/Sunset

```lua
"sunrise"      -- Sunrise time
"sunset"       -- Sunset time
"sunrise+30"   -- 30 minutes after sunrise
"sunset-60"    -- 60 minutes before sunset
```

#### Timer Options

- **`aligned=true`** - Align timer to interval boundaries (e.g., every 10 min at :00, :10, :20...)

```lua
Event.id = 'alignedTimer'
Event{type='timer', time='+/00:10', aligned=true}
function Event:handler(event)
  self:debug("Aligned timer triggered")
end
```

#### Cron Format

Standard cron format: `"minute hour day month weekday"`

```lua
"30 10 * * *"       -- Daily at 10:30
"0 */2 * * *"       -- Every 2 hours
"0 8 * * mon-fri"   -- Weekdays at 8:00
"*/15 * * * *"      -- Every 15 minutes
"0 0 1 * *"         -- First day of month
"0 0 last * *"      -- Last day of month
"0 0 lastw * *"     -- Last weekday of month
```

**Cron with Sun Events:**

```lua
"sunrise 0 * * *"       -- At sunrise daily
"sunset+30 0 * * *"     -- 30 min after sunset daily
```

---

### Handler Methods

Methods available on `self` inside handler functions:

#### Logging Methods

```lua
self:debug(...)         -- Debug message
self:trace(...)         -- Trace message
self:warning(...)       -- Warning message
self:error(...)         -- Error message
self:debugf(fmt, ...)   -- Formatted debug
self:tracef(fmt, ...)   -- Formatted trace
```

#### Timer Methods

```lua
-- Post an event (same as fibaro.post, but tracked by handler)
self:post(event, time)

-- Cancel a specific timer
self:cancel(ref)

-- Cancel all timers created by this handler
self:cancelAll()

-- Schedule a function call
self:timer(seconds, function, args...)
```

**Example:**
```lua
Event.id = 'myHandler'
Event{...}
function Event:handler(event)
  -- Post event in 5 seconds
  local ref = self:post({type='custom-event', name='test'}, 5)
  
  -- Schedule function
  self:timer(10, function() 
    self:debug("10 seconds passed")
  end)
  
  -- Cancel all timers
  self:cancelAll()
end
```

#### State Methods

```lua
-- Wait for condition to be true for specified time
self:trueFor(time, condition)

-- Repeat handler after time delay
self:again(maxRepeats)
```

**trueFor Example:**
```lua
Event.id = 'motionSensor'
Event{type='device', id=100, property='value'}
function Event:handler(event)
  -- Trigger only if motion stays on for 30 seconds
  if self:trueFor(30, event.value > 0) then
    self:debug("Motion detected for 30+ seconds!")
  end
end
```

**again Example:**
```lua
Event.id = 'repeater'
Event{type='device', id=100, property='value', value='$_>0'}
function Event:handler(event)
  -- Repeat 3 times, every 5 seconds
  local count = self:again(3)
  self:debug("Repeat #" .. count)
end
```

#### Control Methods

```lua
-- Enable/disable handler
self:enable()
self:disable()

-- Check time ranges
self:between(startTime, endTime)
```

**Example:**
```lua
Event.id = 'nightHandler'
Event{...}
function Event:handler(event)
  if self:between("sunset", "sunrise") then
    self:debug("Running during night")
  end
end
```

#### Breaking Event Chain

Return `self.BREAK` to prevent other handlers from processing the event:

```lua
Event.id = 'myHandler'
Event{...}
function Event:handler(event)
  if event.value > 100 then
    self:trace("Blocking event")
    return self.BREAK
  end
end
```

---

## Advanced Features

### Event Transformers

Register custom event transformers to convert one event type to others:

```lua
Event:_transformEvent('myType', function(event)
  -- Return array of new events or false to skip
  return {
    {type='device', id=100, property='value'},
    {type='custom-event', name='transformed'}
  }
end)
```

### Managed Events

Register custom managed event types:

```lua
Event:_managedEvent('myTimer', function(k, event)
  -- Custom timer management logic
  -- Schedule event, return modified event
  return event
end)
```

### Attaching to RefreshState

To receive HC3 system events (device changes, global variables, etc.), you must connect EventLib to the HC3 event stream:

```lua
Event:attachRefreshstate()
```

**Important:** This must be called **after** all libraries are loaded. The recommended approach is to use the `QAstart` event:

```lua
Event = Event_std

-- Setup handler at startup
Event.id = 'start'
Event{type='QAstart'}
function Event:handler(event)
  Event:attachRefreshstate()  -- Enable HC3 event reception
  self:debug("EventLib ready - listening to HC3 events")
end

-- Now define your event handlers
Event.id = 'myLight'
Event{type='device', id=123, property='value'}
function Event:handler(event)
  self:debug("Light changed to: " .. event.value)
end
```

**What it does:**
- Connects to HC3's `RefreshStateSubscriber` event stream
- Enables handlers to receive device events, global variable changes, etc.
- Must be called once during QuickApp initialization

**Without attachRefreshstate():** Only timer, cron, and manually posted events will work.

### Multiple Device IDs

Handle multiple devices with one pattern:

```lua
-- Automatically expanded to multiple handlers
Event.id = 'multiLight'
Event{type='device', id={123, 456, 789}, property='value'}
function Event:handler(event)
  self:trace("Light " .. event.id .. " changed")
end
```

### Global Event Posting

Post events from anywhere in your code:

```lua
-- Post immediately
fibaro.post({type='custom-event', name='myEvent'})

-- Post after delay (seconds)
fibaro.post({type='custom-event', name='myEvent'}, 30)

-- Using Event namespace
Event:post({type='custom-event', name='myEvent'}, 10)
```

### Manual Event Handling

Process events manually without RefreshState:

```lua
-- Send event directly to EventLib
Event:post({type='device', id=100, property='value', value=50})
```

---

## Resource Helpers

EventLib includes helper functions for cleaner device and variable access.

### GLOB - Global Variable Helper

Create a global variable object:

```lua
local myVar = GLOB("MyVariable")

-- Read value
local val = myVar.value

-- Watch for changes
myVar.watch = function(self, newValue, oldValue, glob)
  self:debug("Variable changed: " .. oldValue .. " -> " .. newValue)
end

-- Access name
print(tostring(myVar))  -- "MyVariable"
```

### DEV - Device Helper

Create a device object:

```lua
local myLight = DEV(123)

-- Read properties
local state = myLight.value
local power = myLight.power
local name = myLight.name

-- Watch specific property
myLight.watch_value = function(self, event, dev)
  self:debug(dev .. " value: " .. event.value)
end

-- Access device data
print(tostring(myLight))  -- Device name
```

---

## Examples

### Example 1: Motion-Activated Light

```lua
Event = Event_std

-- Turn on light when motion detected
Event.id = 'motionOn'
Event{type='device', id=100, property='value'}
function Event:handler(event)
  if event.value > 0 then
    fibaro.call(200, "turnOn")
    -- Auto-off after 5 minutes
    self:post({type='device', id=200, property='targetLevel', value=0}, 300)
  end
end
```

### Example 2: Temperature Monitor with Alerts

```lua
Event = Event_std

Event.id = 'tempMonitor'
Event{type='device', id=50, property='value'}
function Event:handler(event)
  -- Alert if high temp persists for 60 seconds
  if self:trueFor(60, event.value > 28) then
    self:warning("High temperature: " .. event.value)
    fibaro.call(100, "sendPush", "Temperature alert!")
  end
end
```

### Example 3: Daily Morning Routine

```lua
Event = Event_std

Event.id = 'morning'
Event{type='cron', time='0 7 * * mon-fri'}
function Event:handler(event)
  self:debug("Starting morning routine")
  
  -- Turn on lights gradually
  fibaro.call(101, "setValue", 30)
  self:timer(60, function()
    fibaro.call(101, "setValue", 100)
  end)
  
  -- Coffee maker on
  fibaro.call(102, "turnOn")
end
```

### Example 4: Smart Night Mode

```lua
Event = Event_std

-- Activate at sunset
Event.id = 'nightStart'
Event{type='timer', time='n/sunset'}
function Event:handler(event)
  self:debug("Night mode activated")
  fibaro.call(1, "setActiveProfile", "Night")
  fibaro.call({200,201,202}, "turnOff")
end

-- Deactivate at sunrise
Event.id = 'nightEnd'
Event{type='timer', time='n/sunrise'}
function Event:handler(event)
  self:debug("Night mode deactivated")
  fibaro.call(1, "setActiveProfile", "Day")
end
```

### Example 5: Pattern Matching with Constraints

```lua
Event = Event_std

-- React to multiple devices with value > 50
Event.id = 'anyHigh'
Event{type='device', id={100,101,102}, property='value', value='$val>50'}
function Event:handler(event)
  self:debugf("Device %d exceeded threshold: %s", 
    event.id, self._match.val)
end

-- React to specific device turning off
Event.id = 'lightOff'
Event{type='device', id=123, property='value', value='$_==0'}
function Event:handler(event)
  self:debug("Light turned off")
end
```

### Example 6: Using Tags and Colors

```lua
Event = Event_std

Event.id = 'tempAlert'
Event.tag = 'TempMonitor'
Event.tagColor = 'red'
Event.debug = true

Event{type='device', id=50, property='value', value='$temp>25'}
function Event:handler(event)
  self:warning("High temp: " .. self._match.temp)
end
```

### Example 7: Complex State Machine

```lua
Event = Event_std

local state = "idle"

Event.id = 'button'
Event{type='device', id=100, property='centralSceneEvent'}
function Event:handler(event)
  local keyId = event.value.keyId
  
  if state == "idle" and keyId == 1 then
    state = "armed"
    self:debug("System armed")
    
    -- Disarm after 30 seconds if not triggered
    self:timer(30, function()
      if state == "armed" then
        state = "idle"
        self:debug("Auto-disarmed")
      end
    end)
  elseif state == "armed" and keyId == 2 then
    state = "triggered"
    self:warning("ALARM TRIGGERED!")
    fibaro.alert("alarm", {1, 2})
  end
end
```

---

## Best Practices

### 1. Use Meaningful Handler Names

```lua
-- Good
Event.id = 'frontDoorMotion'
Event.id = 'bedroomTempAlert'

-- Avoid
Event.id = 'h1'
Event.id = 'temp'
```

### 2. Add Tags for Complex QuickApps

```lua
Event.id = 'handler1'
Event.tag = 'Security'
Event.tagColor = 'red'
```

### 3. Use trueFor for Debouncing

```lua
-- Wait for stable state before acting
if self:trueFor(30, event.value > threshold) then
  -- Take action
end
```

### 4. Clean Up Timers

```lua
Event.id = 'myHandler'
Event{...}
function Event:handler(event)
  -- Cancel previous timers before creating new ones
  self:cancelAll()
  self:post(newEvent, delay)
end
```

### 5. Enable Debug Logging During Development

```lua
fibaro.debugFlags.post = true  -- See all event posts
Event.debug = true             -- Debug specific handler
```

### 6. Use Multiple Device IDs for Flexibility

```lua
-- Instead of many similar handlers
Event.id = 'sensor1'
Event{type='device', id=100, property='value'}
function Event:handler(event) end

Event.id = 'sensor2'
Event{type='device', id=101, property='value'}
function Event:handler(event) end

-- Use one handler for multiple devices
Event.id = 'allSensors'
Event{type='device', id={100,101,102,103}, property='value'}
function Event:handler(event)
  -- Handle all listed sensors
  self:debug("Sensor " .. event.id .. " triggered")
end
```

**Note:** Device IDs cannot use pattern matching. Use array syntax `id={100,101,102}` for multiple devices.

### 7. Handle Errors Gracefully

```lua
Event.id = 'myHandler'
Event{...}
function Event:handler(event)
  local ok, err = pcall(function()
    -- Your code here
  end)
  if not ok then
    self:error("Handler failed: " .. err)
  end
end
```

### 8. Use Anonymous Handlers for Simple Cases

```lua
-- Quick one-off handlers
Event.id = '_'
Event{type='device', id=123, property='value'}
function Event:handler(event)
  if event.value > 0 then fibaro.call(456, "turnOn") end
end
```

---

## Troubleshooting

### Events Not Triggering

**Problem:** Handler not executing  
**Solutions:**
- Ensure `Event:attachRefreshstate()` is called
- Verify event pattern matches actual events
- Enable debug: `fibaro.debugFlags.post = true`
- Check handler isn't disabled

### Timer Not Firing

**Problem:** Timer events not executing  
**Solutions:**
- Verify time format: `"10:30"` not `10:30`
- Check prefix: `"+/00:10"` for relative, `"t/10:30"` for today
- For aligned timers, ensure `aligned=true` flag set

### Pattern Matching Not Working

**Problem:** Variables not captured correctly  
**Solutions:**
- Check `$` prefix: `$var` not `var`
- Verify constraint syntax: `$val>50` not `$val > 50`
- Examine `self._match` table to see what was captured

### trueFor Not Working

**Problem:** `trueFor` condition not triggering  
**Solutions:**
- Ensure same event keeps firing (condition stays true)
- Check that timer isn't being cancelled elsewhere
- Remember `trueFor` returns false initially

### Memory Issues

**Problem:** QuickApp running out of memory  
**Solutions:**
- Use `self:cancelAll()` to clean up timers
- Avoid creating too many anonymous handlers
- Disable unused handlers with `self:disable()`

### Debugging Tips

```lua
-- Enable all debug flags
fibaro.debugFlags.post = true
```

---

## Changelog

### v0.52 (Current)
- Initial documented release
- Full pattern matching support with variable extraction and constraints
- trueFor and again state tracking for complex conditions
- Cron and timer support with sunrise/sunset calculations
- Resource helpers (DEV, GLOB) for cleaner code
- Event_std API with id, events, handler pattern

---

## Support

- **Forum Thread:** https://forum.fibaro.com/topic/74161-eventlib/
- **Author:** jan@gabrielsson.com
- **License:** GNU GPL v3

---

## Contributing

EventLib is open source under GPL v3. Contributions, bug reports, and feature requests are welcome on the Fibaro forum thread.

---

*This documentation is maintained for EventLib v0.52. Please report any errors or suggest improvements on the forum.*
