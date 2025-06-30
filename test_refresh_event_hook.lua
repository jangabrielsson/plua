--%%name:RefreshEventHookTest
--%%type:com.fibaro.binarySwitch
--%% offline:true

function QuickApp:onInit()
  self:debug("Testing refresh states event hook...")

  -- Create a hook function to receive refresh states events
  _PY.newRefreshStatesEvent = function(event_data)
    self:debug("Received refresh states event:", json.encode(event_data))
    
    -- You can process the event here
    if event_data.event and event_data.event.type then
      self:debug("Event type:", event_data.event.type)
      
      -- Example: Handle different event types
      if event_data.event.type == "deviceUpdate" then
        self:debug("Device update event received!")
      elseif event_data.event.type == "systemEvent" then
        self:debug("System event received!")
      end
    end
  end

  -- Test 1: Add events manually and verify hook is called
  self:debug("Test 1: Adding test events manually...")
  _PY.addEvent('{"type": "deviceUpdate", "deviceId": 123, "property": "state", "value": "on"}')
  _PY.addEvent('{"type": "systemEvent", "message": "System started"}')
  
  -- Get events to verify they were stored
  local events = _PY.getEvents(0)
  self:debug("Total events in queue:", #events.events)
  
  -- Test 2: Start polling (this would normally connect to HC3)
  self:debug("Test 2: Starting polling...")
  local poll_result = _PY.pollRefreshStates(0, "http://192.168.1.57:80/api/refreshStates?last=", {
    headers = {Authorization = "Basic YWRtaW46QWRtaW4xNDc3IQ=="}
  })
  self:debug("Poll result:", json.encode(poll_result))
  
  -- Test 3: Simulate events being received during polling
  self:debug("Test 3: Simulating events during polling...")
  setTimeout(function()
    -- Add more events while polling is active
    _PY.addEvent('{"type": "deviceUpdate", "deviceId": 456, "property": "temperature", "value": 22.5}')
    _PY.addEvent('{"type": "alarmChange", "partition": 1, "state": "armed"}')
    
    self:debug("Added simulated events during polling")
  end, 1000)
  
  -- Wait and then stop polling
  setTimeout(function()
    self:debug("Event hook test completed!")
    _PY.stopRefreshStates()
  end, 3000)
end 