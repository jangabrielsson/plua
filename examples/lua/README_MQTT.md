# MQTT Client API - Fibaro HC3 Compatible

EPLua now provides a fully compatible MQTT client implementation that follows the Fibaro Home Center 3 API specification.

## Key Features

- **Official Fibaro API**: Use `mqtt.Client.connect()` for full HC3 compatibility
- **EventTarget API**: Standard `addEventListener()` method for event handling
- **QoS Support**: Full Quality of Service level support
- **Multiple Topics**: Subscribe/unsubscribe to multiple topics at once
- **Last Will Testament**: Support for LWT messages
- **Backward Compatibility**: Legacy `net.MQTTClient()` still works

## Quick Start

```lua
-- Connect using Fibaro HC3 API
local client = mqtt.Client.connect("mqtt://broker.example.com:1883", {
  clientId = "MyDevice",
  callback = function(errorCode)
    print("Connected:", errorCode == 0)
  end
})

-- Add event listeners
client:addEventListener('connected', function(event)
  print("Connected! Session present:", event.sessionPresent)
end)

client:addEventListener('message', function(event)
  print("Received:", event.topic, "->", event.payload)
end)
```

## Available Namespaces

- **`mqtt.Client`** - Official Fibaro API (recommended)
- **`mqtt.QoS`** - Quality of Service levels
- **`net.Client`** - Alias for `mqtt.Client`
- **`net.MQTTClient()`** - Legacy constructor (backward compatibility)

## QoS Levels

```lua
mqtt.QoS.AT_MOST_ONCE   -- 0
mqtt.QoS.AT_LEAST_ONCE  -- 1  
mqtt.QoS.EXACTLY_ONCE   -- 2
```

## Events

- **`connected`** - Connection established
- **`closed`** - Connection closed
- **`subscribed`** - Subscription confirmed
- **`unsubscribed`** - Unsubscription confirmed
- **`published`** - Message published
- **`message`** - Message received
- **`error`** - Error occurred

## Methods

- **`connect(uri, options)`** - Static method to create and connect
- **`disconnect(options)`** - Disconnect from broker
- **`subscribe(topic/topics, options)`** - Subscribe to topic(s)
- **`unsubscribe(topics, options)`** - Unsubscribe from topic(s)
- **`publish(topic, payload, options)`** - Publish message
- **`addEventListener(event, callback)`** - Add event listener
- **`removeEventListener(event)`** - Remove event listener
- **`isConnected()`** - Check connection status
- **`getInfo()`** - Get client information

## Example Usage

See `examples/lua/mqtt_example.lua` for comprehensive examples including:
- Basic connection and messaging
- Multiple topic subscriptions
- Last Will and Testament
- Error handling

This implementation is fully compatible with existing Fibaro HC3 Quick Apps that use MQTT.
