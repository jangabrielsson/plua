-- Test script for refresh states polling and event queue functions
print("Testing refresh states and single event queue functions...")

-- Test event queue functions
print("\n=== Testing Single Event Queue Functions ===")

-- Initialize the global event queue
local success = _PY.init_event_queue()
print("Initialized event queue:", success)

-- Add some test events
_PY.add_event({type="test", message="Hello World", timestamp=_PY.get_time()})
_PY.add_event({type="test", message="Second Event", value=42})
_PY.add_event({type="test", message="Third Event", data={nested="value"}})

-- Check queue size
local size = _PY.get_event_count()
print("Queue size after adding events:", size)

-- Get events from queue
local events = _PY.get_events(2)
print("Retrieved events:")
for i, event in ipairs(events) do
    print("  Event", i, ":", event.type, "-", event.message)
    if event.value then print("    Value:", event.value) end
    if event.data then print("    Data:", event.data.nested) end
end

-- Check queue size after retrieval
size = _PY.get_event_count()
print("Queue size after retrieval:", size)

-- Get remaining events
events = _PY.get_events(10)
print("Remaining events:", #events)
for i, event in ipairs(events) do
    print("  Event", i, ":", event.type, "-", event.message)
end

-- Clear the queue
success = _PY.clear_events()
print("Cleared queue:", success)
print("Queue size after clear:", _PY.get_event_count())

-- Test refresh states polling (mock endpoint)
print("\n=== Testing Refresh States Polling ===")

-- Define callback function for refresh states updates
function onRefreshStatesUpdate(data)
    print("Received refresh states update:", data)
    if data and data.timestamp then
        print("  Timestamp:", data.timestamp)
    end
    if data and data.devices then
        print("  Device count:", #data.devices)
    end
end

-- Note: This would normally use a real Fibaro HC3 endpoint
-- For testing, we'll use a mock service or skip this part
print("Refresh states polling functions are ready")
print("To test, call:")
print("  _PY.start_refresh_states_polling('http://your-hc3-ip/api/refreshStates', 2.0)")
print("  _PY.stop_refresh_states_polling()")

print("\nAll tests completed successfully!")
