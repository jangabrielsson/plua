--%%name:EventLibTest
--%%type:com.fibaro.genericDevice
--%% offline:true
--%%desktop:true

--%%file:$fibaro.lib.eventlib,eventlib

--------ENDOFHEADERS------

 function sensorBreachedEvent()
 print("Breached triggered")
 end

Event = Event_std

Event.id='start'
Event{type='QAstart'}
function Event:handler(event)
  Event:attachRefreshstate()
end

local sensor_id = 5556 -- binarySensor will get next id, e.g. 5556

Event.id='breachevent'                            
Event{type='device', id = sensor_id, value=true} 
function Event:handler(event) 
  sensorBreachedEvent()
end

local sensor = fibaro.plua.lib.loadQAString([[
--%%name:BinarySwitch
--%%type:com.fibaro.binarySwitch
--%%desktop:true
function QuickApp:onInit() self:debug("Binaryswitch",self.id) end
function QuickApp:turnOn() 
  self:debug("binary switch turned on")
  self:updateProperty("value", true)
end
function QuickApp:turnOff() 
  self:debug("binary switch turned off")
  self:updateProperty("value", false)
end
]])

function QuickApp:onInit()
  self:debug(self.id,self.name,sensor.device.id)
  fibaro.call(sensor.device.id,"turnOn")
end

--setInterval(function() print('ok') end,3600)