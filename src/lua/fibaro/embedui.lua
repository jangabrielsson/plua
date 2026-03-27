local binFalse = "<center><font color='red'>FALSE</font></center>"
local binTrue = "<center><font color='green'>TRUE</font></center>"

local function customBin(value) return value and binTrue or binFalse end

local embedUIs = {
  ["com.fibaro.binarySwitch"] = {
    {{label='__binarysensorValue',text=binFalse}},
    {{button='__turnOn',text='Turn On',onReleased='turnOn'},{button='__turnOff',text='Turn Off',onReleased='turnOff'}}
  },
  ["com.fibaro.multilevelSwitch"] = {
    {{label='__multiswitchValue',text='0'}},
    {{button='__turnOn',text='Turn On',onReleased='turnOn'},{button='__turnOff',text='Turn Off',onReleased='turnOff'}},
    {{slider='__setValue',text='',onChanged='setValue'}}
  },
  ["com.fibaro.colorController"] = {
    {{label='__colorComponentValue',text='white'}},
    {{button='__turnOn',text='Turn On',onReleased='turnOn'},{button='__turnOff',text='Turn Off',onReleased='turnOff'}},
    {{slider='__setValue',text='',onChanged='setValue'}},
    {{slider='__setColorComponentR',text='',max='255',onChanged='setValue'}},
    {{slider='__setColorComponentG',text='',max='255',onChanged='setValue'}},
    {{slider='__setColorComponentB',text='',max='255',onChanged='setValue'}},
    {{slider='__setColorComponentW',text='',max='255',onChanged='setValue'}}

  },
  ["com.fibaro.multilevelSensor"] = {
    {{label='__multisensorValue',text='0'}},
  },
  ["com.fibaro.binarySensor"] = {
    {{label='__binarysensorValue',text=binFalse}},
  },
  ["com.fibaro.doorSensor"] = {
    {{label='__doorSensor',text=binFalse}},
  },
  ["com.fibaro.windowSensor"] = {
    {{label='__windowSensor',text=binFalse}},
  },
  ["com.fibaro.temperatureSensor"] = {
    {{label='__temperatureSensor',text='0'}},
  },
  ["com.fibaro.humiditySensor"] = {
    {{label='__humiditySensor',text='0'}},
  },
}

local watches = {
  ["com.fibaro.binarySwitch"] = {
    value = { id = "__binarysensorValue", fmt=customBin, prop="text" },
  },
  ["com.fibaro.multilevelSwitch"] = {
    value = { 
      { id= '__setValue', prop='value', fmt='%s'},
      {id = "__multiswitchValue", fmt="%.3f", prop="text"},
    }
  },
  ["com.fibaro.colorController"] = {
    value = { id = "__colorComponentValue", prop="text", fmt=function(val)
      if type(val) == "table" then
        local r = val.dimming and math.floor(val.dimming.brightness + 0.5) or 0
        local c = val.color or {}
        return string.format(
          "<font color='rgb(%d,%d,%d)'>%s</font>",
          c.r or 0, c.g or 0, c.b or 0,
          r > 0 and "ON" or "OFF"
        )
      else
        return binFalse
      end
    end},
  },
  ["com.fibaro.multilevelSensor"] = {
    value = { id = "__multisensorValue", fmt="%.3f", prop="text"},
  },
  ["com.fibaro.doorSensor"] = {
    value = { id = "__doorSensor", fmt=customBin, prop="text" },
  },
  ["com.fibaro.windowSensor"] = {
    value = { id = "__windowSensor", fmt=customBin, prop="text" },
  },
  ["com.fibaro.temperatureSensor"] = {
    value = { id = "__temperatureSensor", fmt="%.2f°", prop="text"},
  },
  ["com.fibaro.humiditySensor"] = {
    value = { id = "__humiditySensor", fmt="%.2f%%", prop="text"},
  },
}

return {
  UI = embedUIs,
  watches = watches,
}