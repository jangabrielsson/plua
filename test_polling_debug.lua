-- Simple polling debug test
print("=== POLLING DEBUG TEST ===")

-- Test 1: Check if _PY functions are available
print("\n1. Checking _PY functions:")
print("_PY.pollRefreshStates available:", _PY.pollRefreshStates ~= nil)
print("_PY.addEvent available:", _PY.addEvent ~= nil)
print("_PY.addEventFromLua available:", _PY.addEventFromLua ~= nil)
print("_PY.getEvents available:", _PY.getEvents ~= nil)
print("_PY.stopRefreshStates available:", _PY.stopRefreshStates ~= nil)
print("_PY.getRefreshStatesStatus available:", _PY.getRefreshStatesStatus ~= nil)

-- Test 2: Check current events
print("\n2. Current events:")
local events = _PY.getEvents()
print("Number of events:", #events.events)
for i, event in ipairs(events.events) do
    print("  Event", i, ":", event.type, event.timestamp)
end

json = require("plua.json")

-- Test 3: Set up event hook to track calls
print("\n3. Setting up event hook...")
local event_call_count = 0
local last_event_data = nil

_PY.newRefreshStatesEvent = function(event_data)
    event_call_count = event_call_count + 1
    last_event_data = event_data
    print("  Hook called #" .. event_call_count .. " with event:", json.encode(event_data))
end

-- Test 4: Test manual event addition
print("\n4. Testing manual event addition:")
_PY.addEventFromLua(json.encode({type = "test_event", message = "test1", id = 1}))
_PY.addEventFromLua(json.encode({type = "test_event", message = "test2", id = 2}))
_PY.addEventFromLua(json.encode({type = "test_event", message = "test3", id = 3}))

events = _PY.getEvents()
print("Events after manual addition:", #events.events)
print("Event hook was called", event_call_count, "times")

-- Test 5: Check if polling is working
print("\n5. Testing polling (will wait 10 seconds):")
print("Starting polling...")
local poll_result = _PY.pollRefreshStates(0, "http://192.168.1.57:80/api/refreshStates?last=", {
  headers = {Authorization = "Basic YWRtaW46QWRtaW4xNDc3IQ=="}
})
print("Poll result:", json.encode(poll_result))

-- Wait and check for events and status
for i = 1, 3 do
    print("Waiting 3 seconds...")
    os.execute("sleep 3")
    
    -- Check polling status
    local status = _PY.getRefreshStatesStatus()
    print("Polling status:", json.encode(status))
    
    events = _PY.getEvents()
    print("Events after", i*3, "seconds:", #events.events)
    for j, event in ipairs(events.events) do
        print("  Event", j, ":", event.type, event.timestamp)
    end
end

-- Test 6: Stop polling and check final state
print("\n6. Stopping polling:")
local stop_result = _PY.stopRefreshStates()
print("Stop result:", json.encode(stop_result))

events = _PY.getEvents()
print("Final events count:", #events.events)
print("Total event hook calls:", event_call_count)

print("\n=== DEBUG TEST COMPLETE ===") 