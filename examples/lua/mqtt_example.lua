-- MQTT Client Example following Fibaro HC3 API
-- Based on: https://manuals.fibaro.com/knowledge-base-browse/hc3-quick-apps-mqtt-client/

-- mqtt = {
--   Client = net.Client,
--   QoS = net.QoS,
--   MQTTConnectReturnCode = net.MQTTConnectReturnCode
-- }

print("MQTT Client Example - Fibaro HC3 API Compatible")

-- Example 1: Basic connection and messaging (Fibaro style)
function connectExample()
  print("\n=== Example 1: Basic Connection ===")
  
  -- Connect using the official Fibaro API
  local client = mqtt.Client.connect("mqtt://broker.hivemq.com:1883", {
    clientId = "EPLua_Demo_" .. tostring(os.time()),
    keepAlivePeriod = 60,
    cleanSession = true,
    callback = function(errorCode)
      print("Connect result:", errorCode == 0 and "Success" or "Failed: " .. tostring(errorCode))
    end
  })
  
  -- Add event listeners using EventTarget API
  client:addEventListener('connected', function(event)
    print("Connected! Session present:", event.sessionPresent)
    print("Return code:", event.returnCode)
    
    -- Subscribe to a topic
    client:subscribe("eplua/demo", {
      qos = mqtt.QoS.AT_LEAST_ONCE,
      callback = function(errorCode)
        print("Subscribe result:", errorCode == 0 and "Success" or "Failed")
      end
    })
  end)
  
  client:addEventListener('subscribed', function(event)
    print("Subscribed! Packet ID:", event.packetId)
    print("Results:", json and json.encode(event.results) or "subscription confirmed")
    
    -- Publish a message
    client:publish("eplua/demo", "Hello from EPLua!", {
      qos = mqtt.QoS.AT_LEAST_ONCE,
      retain = false,
      callback = function(errorCode)
        print("Publish result:", errorCode == 0 and "Success" or "Failed")
      end
    })
  end)
  
  client:addEventListener('message', function(event)
    print("Message received:")
    print("  Topic:", event.topic)
    print("  Payload:", event.payload)
    print("  QoS:", event.qos)
    print("  Retain:", event.retain)
    print("  Packet ID:", event.packetId)
    print("  Duplicate:", event.dup)
  end)
  
  client:addEventListener('published', function(event)
    print("Message published! Packet ID:", event.packetId)
  end)
  
  client:addEventListener('closed', function(event)
    print("Connection closed")
  end)
  
  client:addEventListener('error', function(event)
    print("MQTT Error:", event.code)
  end)
  
  return client
end

-- Example 2: Multiple topic subscription
function multiTopicExample()
  print("\n=== Example 2: Multiple Topics ===")
  
  local client = mqtt.Client.connect("mqtt://broker.hivemq.com:1883", {
    clientId = "EPLua_Multi_" .. tostring(os.time()),
    callback = function(errorCode)
      if errorCode == 0 then
        print("Multi-topic client connected")
        
        -- Subscribe to multiple topics
        client:subscribe({
          {"lights/+", mqtt.QoS.AT_MOST_ONCE},
          {"sensors/#", mqtt.QoS.AT_LEAST_ONCE},
          "system/status" -- defaults to options.qos
        }, {
          qos = mqtt.QoS.EXACTLY_ONCE, -- default for topics without explicit QoS
          callback = function(errorCode)
            print("Multi-subscribe result:", errorCode)
          end
        })
      end
    end
  })
  
  client:addEventListener('message', function(event)
    if event.topic:match("^lights/") then
      print("Light message:", event.topic, "->", event.payload)
    elseif event.topic:match("^sensors/") then
      print("Sensor message:", event.topic, "->", event.payload)
    elseif event.topic == "system/status" then
      print("System status:", event.payload)
    end
  end)
  
  return client
end

-- Example 3: Last Will and Testament
function lastWillExample()
  print("\n=== Example 3: Last Will and Testament ===")
  
  local client = mqtt.Client.connect("mqtt://broker.hivemq.com:1883", {
    clientId = "EPLua_LastWill_" .. tostring(os.time()),
    lastWill = {
      topic = "eplua/status",
      payload = "offline",
      qos = mqtt.QoS.AT_LEAST_ONCE,
      retain = true
    },
    callback = function(errorCode)
      if errorCode == 0 then
        print("Last will client connected")
        -- Publish online status
        client:publish("eplua/status", "online", {
          qos = mqtt.QoS.AT_LEAST_ONCE,
          retain = true
        })
      end
    end
  })
  
  return client
end

-- Start examples
local client1 = connectExample()

-- Clean up after 10 seconds
setTimeout(function()
  print("\n=== Cleaning up ===")
  if client1 then
    client1:disconnect({
      callback = function(errorCode)
        print("Disconnected:", errorCode == 0 and "Success" or "Failed")
      end
    })
  end
end, 10000)

print("\nMQTT examples running... Check the output above for connection results.")
print("Note: QoS enum available as mqtt.QoS.AT_MOST_ONCE, mqtt.QoS.AT_LEAST_ONCE, mqtt.QoS.EXACTLY_ONCE")
print("Note: Use mqtt.Client.connect() for the official Fibaro HC3 compatible API")
