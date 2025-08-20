---@diagnostic disable-next-line: undefined-global

-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
--[[Start  off instuctions

It also support Language:
en  -  English
no  -  Norwegian
(adds languages on request:D )

Special Thanks to @jgab https://forum.fibaro.com/profile/2168-jgab/
Nothing could have been done without his Eventlib, emulators and guides on the forum!!


Changelog:

]]  ----End off instuctions
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
--[[
MIT License

Copyright (c) 2025 Brors94

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

]]
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---hc3emu setup directives



--%%name:Template QA
--%%type:com.fibaro.genericDevice
--%%description:"My description"
--%%desktop:true
--%%save:Template.fqa
--%%offline:true


----hc3emu lib files
--%%file:$fibaro.lib.eventlib,Eventlib
--%%file:$fibaro.lib.qwikchild,qwickchild


-----------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---UI setup 
---🕒➕➖🟩🌡️🟨🟥❌✅❗🚩💡📧


--%%u:{label="label_v1",text="label_v1"}
--%%u:{{switch="V1_n",text="V1_n",value="false",visible=true,onLongPressDown="V1_n_ld",onLongPressReleased="V1_n_lr",onReleased="V1_n"},{switch="V1_p",text="V1_p",value="false",visible=true,onLongPressDown="V1_p_ld",onLongPressReleased="V1_p_lr",onReleased="V1_p"}}



--%%u:{label="infoline1",text=""}
--%%u:{label="info_time",text=""}
--%%u:{{switch="time_n",text="🕒➖",value="false",onLongPressDown="time_n_l",onReleased="time_n"},{switch="time_p",text="🕒➕",value="false",onLongPressDown="time_p_l",onReleased="time_p"}}

--%%u:{label="infoline2",text=""}


--%%u:{{switch="V1_n",text="V1_n",value="false",visible=true,onLongPressDown="V1_n_ld",onLongPressReleased="V1_n_lr",onReleased="V1_n"},{switch="V1_p",text="V1_p",value="false",visible=true,onLongPressDown="V1_p_ld",onLongPressReleased="V1_p_lr",onReleased="V1_p"}}



--%%u:{{switch="T1",text="T1",value="false",visible=true,onLongPressDown="T1_ld",onLongPressReleased="T1_lr",onReleased="T1"},{switch="T2",text="T2",value="false",visible=true,onLongPressDown="T2_ld",onLongPressReleased="T2_lr",onReleased="T2"}}
--%%u:{slider="Slider1",  min=20,max=80, onChanged='Slider1'}





--%%u:{label="infoline10",text="infoline10"}
--%%u:{label="info_push_user",text="info_push_user"}
--%%u:{multi="Push_user_choice",text="Push_user_choice",onToggled="Push_user_choice",options={}}
--%%u:{label="info_push_device",text="info_push_device"}
--%%u:{multi="Push_device_choice",text="Push_device_choice",onToggled="Push_device_choice",options={}}

--%%u:{label="infoline11",text="infoline11"}



--%%u:{label="s1",text=""}
--%%u:{label="s2",text=""}
--%%u:{label="s3",text=""}
--%%u:{label="s4",text=""}
--%%u:{label="s5",text=""}
--%%u:{label="s6",text=""}
--%%u:{label="s7",text=""}
--%%u:{label="s8",text=""}
--%%u:{label="s9",text=""}
--%%u:{label="Setup_manual",text=""}
--%%u:{{button="Restart",text="Restart",visible=true,onReleased="Restart"},{button="s13",text="s13",visible=false,onReleased="s13"}}
--%%u:{label="s10",text=""}
--%%u:{label="s11",text=""}
--%%u:{label="s12",text=""}



-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---ui templates:
---🕒➕➖🟩🌡️🟨🟥❌✅❗🚩💡📧



--u={label="Info_name",text=""}

--u={slider="Slider1", min=20,max=80, onChanged='Slider1'}


--u={{switch="T1",text="T1",value="false",visible=true,onLongPressDown="T1_ld",onLongPressReleased="T1_lr",onReleased="T1"},{switch="T2",text="T2",value="false",visible=true,onLongPressDown="T2_ld",onLongPressReleased="T2_lr",onReleased="T2"}}


--u={{switch="V1_n",text="V1_n",value="false",visible=true,onLongPressDown="V1_n_ld",onLongPressReleased="V1_n_lr",onReleased="V1_n"},{switch="V1_p",text="V1_p",value="false",visible=true,onLongPressDown="V1_p_ld",onLongPressReleased="V1_p_lr",onReleased="V1_p"}}




-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---Quickapp variabel setup
--%%var=motionsensorid:"37" 



--Scene_id is for push interactive scene 
--%%var=Scene_id:""

--%%var=color1:"#ff9933"      ----Orange            #ff9933     --- works on white and black
--%%var=color2:"#99ff33"      ----Green             #99ff33     --- works on white and black
--%%var=color3:"#990000"      ----red               #990000     --- works on white and black 
--%%var=color4:"#66ffff"      ----turquoise         #66ffff     --- works on white and black
--%%var=Setup:"0" 
--%%var=language:"en" 
--%%var=refresh_mem:"60" 





-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
-----local variabels







-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
-----starttime measure
local starttime = os.clock()
local start_date = os.date()
print("starttime: ",starttime)
Event_std = Event_std
local Event = Event_std
local Fontsize = 2


-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
----jgab eventlib 
Event.id='start'
Event{type='QAstart'}
function Event:handler(event)
Event:attachRefreshstate()
end

-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
----jgab storage function
---@diagnostic disable-next-line
function QuickApp:setupStorage()
 local storage,qa = {},self
 function storage:__index(key) return qa:internalStorageGet(key) end
 function storage:__newindex(key,val)
    if val == nil then qa:internalStorageRemove(key)
    else qa:internalStorageSet(key,val) end
  end
 return setmetatable({},storage) 
end

local upd = QuickApp.updateView
function QuickApp:updateView(id,typ,val)
  print("UPDV",id,typ,json.encode(val))
  if val == nil then val = "" end
  upd(self,id,typ,val)
end

--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------
--Function ONinit      
--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------
---@diagnostic disable-next-line
function QuickApp:onInit()
self.store = self:setupStorage()
local room_id 
local quickapp_id = self.id
local self_room_id
local quickapp_name = self.name
if room_id == nil then
self_room_id = hub.getRoomID(quickapp_id)
else 
self_room_id = room_id
end
---@diagnostic disable-next-line
local self_room_name = hub.getRoomName(self_room_id) or "no data"
self:debug("DeviceId:",self.id, "   " ,"Name:", self.name)
self:debug("Room:",self_room_id, "   " ,"Room Name:", self_room_name)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
self:updateProperty("log", "QA Started")
self:updateProperty("deviceRole", "Other")
self:updateProperty("categories",{"other"})
self:updateProperty("useUiView",false)
self:updateProperty("hasUIView",false)






--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------
-----just to fixs labels/buttons not showing
local show_labels = {
"turnoff",
"turnon"
} 
for _,val in pairs(show_labels) do self:updateView(val,"visible",true) end
--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------
local hide_label = {
"unused1",
"unused2",


"s1",
"s2",
"s3",
"s4",
"s5",
"s6",
"s7",
"s8",
"s9",
"s10",
"s11",
"s12",
"s13"


} 
for _,val in pairs(hide_label) do self:updateView(val,"visible",false) end
--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------

for _,val in pairs(hide_label) do self:updateView(val,"Text","") end
--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------


  local check_qa_enabled = api.get("/devices/"..quickapp_id.."") 
  check_qa_enabled = check_qa_enabled.enabled or true
  print("check_qa_enabled: ",check_qa_enabled)
  if check_qa_enabled == true then
  
--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------

--self:updateProperty("batteryLevel",50)
--self:updateProperty("dead",true)
--self:isTypeOf(typ)
--self:callAction(name, ...)
--self:setName(name)
--self:setEnabled(bool)
--self:setVisible(bool)
--self:updateProperty("deviceIcon", iconNumber) 
--fibaro.call(<device.id>, "updateProperty", "dead", true)

--__TAG = "QA_Room_Controller".."_"..tostring(quickapp_id)



--[[
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
------Supported language check 
local lang
local language = self:getVariable("language") or "en"
if string.lower(language) == "en" then
print("English")
elseif  string.lower(language) == "no"  then
print("Norwegian")
elseif  string.lower(language) == "de"  then
print("German")
elseif  string.lower(language) == "pl"  then
print("Polish")
elseif  string.lower(language) == "fr"  then
print("French")
else
language = "en"
print("Language not recognised, English is set")
self:setVariable("language", "en")
end
local translation = lang:translation(self:getVariable("language")) 
----------------------------------------------------------------
------------language setup variables
--local status_translated = ""..translation["Safe"]..""
--if self.store.pir_status == "Detected" then status_translated = ""..translation["Detected"].."" end
]]









-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
------------------description off QA
function UserDescription()
local line = ""
local line = ""..line.."\n"..quickapp_name..""
local line = ""..line.."\nMade by Joachim Brørs Sommerfeld, Norway"
local line = ""..line.."\njoachim.brors.sommerfeld@gmail.com"
local line = ""..line.."\nI am not a programer by craft/work,"
local line = ""..line.."\nit is only a hobby so the code isnt perfect :D "
local line = ""..line.."\nUse at own risk! ^^\n"
local line = ""..line.."\nThis quickapp also uses the Eventlib made by:"
local line = ""..line.."\neventLib©️jan@gabrielsson.com"
local line = ""..line.."\nAnd wouldnt work without it! Thanks!"
local line = ""..line.."\n"
self:updateProperty("userDescription",""..line.."") 
end
UserDescription()





-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
------label colors 
local color1 = self:getVariable("color1") or "Orange"  --"<font color=Orange>"
color1 = "<font color="..color1..">"
local color2 = self:getVariable("color2") or "green"  --"<font color=green>"
color2 = "<font color="..color2..">"
local color3 = self:getVariable("color3") or "red"  --"<font color=red>"
color3 = "<font color="..color3..">"
local color4 = self:getVariable("color4") or "turquoise"  ----"turquoise"


-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
--------- first time QA runs
if self.store.first_time == nil then   ----       ~=
--if 0 == 0 then
  -------





  self.store.kbc_val_max = "0.0001"
  self.store.cpp_val_max = "0.0001"
  self.store.kb_val_max = "0.0001"
  -------
  self.store.first_time = "First time Installation is Done"
  print(self.store.first_time)
end---if self.store.first_time == nil then 

----------------------------------------------------------------
----------------------------------------------------------------
local setup = self:getVariable("Setup") or "0"
if setup ~= "0" then
  self:setVariable("Setup", "0")
  -------





  self.store.kbc_val_max = "0.0001"
  self.store.cpp_val_max = "0.0001"
  self.store.kb_val_max = "0.0001"
  -------
  self.store.first_time = "First time Installation is Done"
  print(self.store.first_time)
end-- if setup ~= "0" then

-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---local vars
local T1
local T2
local l_start = "<table width= 400px border = 0px><td align =left>"
local l_end   = ""
local left_right = "left"


------------------------------------
local refresh_mem = tonumber(self:getVariable("refresh_mem") )
if refresh_mem == nil then refresh_mem = 60 end
------------------------------------


----------------------------------------------
local function fmt_2digit(v) 
  local val = string.format("%02d",v)
  return val
  end
----------------------------------------------
local function fmt_2desi(v) 
  local val = string.format("%.2f",v)
  return val
  end
----------------------------------------------
local function fmt_0desi(v) 
  local val = string.format("%.0f",v)
  return val
  end
----------------------------------------------
local function fmt_1desi(v) 
  local val = string.format("%.1f",v)
  return val
  end
----------------------------------------------
local function fmt_2dig_2desi(v) 
  local val = string.format("%02d.2f",v)
  return val
  end
----------------------------------------------




-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------








-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
self.store.v1_val = 0
local v1_short = 1
local v1_long = 10
local v1_max = 100
local v1_min= 0

---@diagnostic disable-next-line
function QuickApp:V1_n(args)
  self:updateView("V1_n", "value", "true")
  V1_n()
end
---------------------------
function V1_n()
  self.store.v1_val = self.store.v1_val - v1_short
 if self.store.v1_val < v1_min then
  self.store.v1_val = v1_max
 end
    hub.setTimeout(200, function()
      self:updateView("V1_n", "value", "false")
    end)
end
---------------------------
---@diagnostic disable-next-line
function QuickApp:V1_n_ld(args)
  self:updateView("V1_n", "value", "true")
  V1_n_ld()
end
---------------------------
function V1_n_ld()
  self.store.v1_val = self.store.v1_val - v1_long
 if self.store.v1_val < v1_min then
  self.store.v1_val = v1_max
 end
end
---------------------------
---@diagnostic disable-next-line
function QuickApp:V1_n_lr(args)
  self:updateView("V1_n", "value", "false")
end
---------------------------
---------------------------
---------------------------
---@diagnostic disable-next-line
function QuickApp:V1_p(args)
  self:updateView("V1_p", "value", "true")
  V1_p()
end
---------------------------
function V1_p()
  self.store.v1_val = self.store.v1_val + v1_short
 if self.store.v1_val < v1_min then
  self.store.v1_val = v1_max
 end
    hub.setTimeout(200, function()
      self:updateView("V1_p", "value", "false")
    end)
end
---------------------------
---@diagnostic disable-next-line
function QuickApp:V1_p_ld(args)
  self:updateView("V1_p", "value", "true")
  V1_p_ld()
end
---------------------------
function V1_p_ld()
  self.store.v1_val = self.store.v1_val + v1_long
 if self.store.v1_val > v1_max then
  self.store.v1_val = v1_min
 end
end
---------------------------
---@diagnostic disable-next-line
function QuickApp:V1_p_lr(args)
  self:updateView("V1_p", "value", "false")
end
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------


















-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---@diagnostic disable-next-line
function QuickApp:T1(args)

api.post("/devices/3004", {["visible"]= true,})


--api.post("/mobile/push", {["data"] = {["deviceId"] = 22, ["actionName"] = "onReleased", ["args"] = {[1] = "button_ID_0_2", }, }, ["title"] = "device push title", ["service"] = "Device", ["category"] = "RUN_CANCEL", ["action"] = "RunAction", ["mobileDevices"] = {[1] = 38, }, ["message"] = "device push massage interactive \nrun/cancel device push button", })

  if (args["values"][1] == true) then
    self:updateView("T1", "value", "true")
    self:updateView("T1", "text", "T1🟩")
  elseif (args["values"][1] == false) then
    self:updateView("T1", "value", "false")
    self:updateView("T1", "text", "T1🟥")
  end
end

-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---@diagnostic disable-next-line
function QuickApp:T2(args)
  if (args["values"][1] == true) then
    self:updateView("T2", "value", "true")
    self:updateView("T2", "text", "T2🟩")
  elseif (args["values"][1] == false) then
    self:updateView("T2", "value", "false")
    self:updateView("T2", "text", "T2🟥")
  end
end





-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---slider 
---@diagnostic disable-next-line
function QuickApp:Slider1(ev)
  self:debug("Slider1:",ev.values[1])



end



-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---select 
---@diagnostic disable-next-line
function QuickApp:newOptions(event)
local newData = {{text='Auto3',type='option',value='auto'},{text='Manual1',type='option',value='manual'},{text='Eco1',type='option',value='eco'}}
newData[1].text = tostring(os.time())
self:updateView("modeSelector","options",newData)
end

-------------------------
---@diagnostic disable-next-line
function QuickApp:setManual(event)
print(event.values[1])
self:updateView("modeSelector","selectedItem","manual")
end

-------------------------
---@diagnostic disable-next-line
function QuickApp:setAuto(event)
print(event.values[1])
self:updateView("modeSelector","selectedItem","auto")
end

-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---label function setup
--color1 orange
--color2 green
--color3 red
--color4 turquoise
--&nbsp  space in label
--os.date("%H:%M")
--string.format("%02d:%02d",Time1H,Time1M)
--fmt(tostring(math.fmod (self.store.p1_basic_time[p_id], 60)))
--"..translation["setup profile"].."
function Info_name()
  local function fmt(v) 
    local val = string.format("%02d",v)
    return val
    end
  local line = ""
  line = ""..line..""..color1.."        "
  line = ""..line.."<br />"..color1.."       "
  line = ""..line.."<br />"..color1.."        "



  self:updateView("Info_name", "text",""..l_start.."<section align='left'><font size='"..Fontsize.."'><pre>"..line.."</pre></font></section>"..l_end.."")
end--function Info_name()








-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
------jgab eventlib handler and filters

local id = {} 
local check = false
for ind,val in pairs(id) do
  check = true
end ---forloop
--------------------------------------------
if (check == true) then
    Event.id='_'
    Event_std.tagColor='Orange'
    Event {type='device', id={id}, property='value', value='$value'}
    function Event:handler(event)
      --event.id
      --event.value
      --self:debug("Sensor ID: ",event.id,"value: ",event.value)
      --local var = ""..event.id..""


    end ---function eventlib
end--if (check == true) then



--[[
local x_id
local y_id
local id = {x_id,y_id} 
local x_val
local y_val 
--------------------------------------------
    Event.id='_'
    Event_std.tagColor='Orange'
    Event {type='device', id={id}, property='value', value='$value'}
    function Event:handler(event)
      if event.id == x_id then
        event.value = x_val
      elseif event.id == y_id then
        event.value = y_val
      end
      if (x_val == true and y_val== false) then
        ---Do_what_you_want()
      end
      --event.value
      --self:debug("Sensor ID: ",event.id,"value: ",event.value)
      --local var = ""..event.id..""
    end ---function eventlib
    Event_std:post({type='device', id=x_id, property='value', value=hub.getValue(x_id, "value")})  
    Event_std:post({type='device', id=y_id, property='value', value=hub.getValue(y_id, "value")})  
]]


-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------









    Event.id='_'
    Event_std.tagColor='Orange'
    Event {type='system'}
    function Event:handler(event)
      --event.id
      --event.value
   self:debug("User ID: ",event.id,"value: ",event.value, "Data: ", json.encode(event))
      
      --local var = ""..event.id..""


    end ---function eventlib



    Event.id='_'
    Event_std.tagColor='Orange'
    Event {type='user',id=2}
    function Event:handler(event)
      --event.id
      --event.value
      self:debug("User ID: ",event.id,"value: ",event.value, "Data: ", json.encode(event))
      
      --local var = ""..event.id..""


    end ---function eventlib

  --{type='user',id=<number>,value='action',data=<value>}
  --{type='system',value='action',data=<value>}










































































-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
----update Push User api
local push_user_id = {}  
local push_user_name = {}
local push_user_email = {}    
local push_user_api
function push_user_api()
        local var = api.get("/users")
        --local var2 = json.encode(var)
        --print("var",var2)
        for ind,val in ipairs(var)do
        --print("ind",ind)
        --print("val",json.encode(val))
        push_user_id[val.id] = val.id 
        push_user_name[push_user_id[val.id]] = val.name
        push_user_email[push_user_id[val.id]] = val.email
        --print("ID",push_user_id[val.id])
        --print("Name",push_user_name[val.id])
        --print("Email",push_user_email[val.id])
        end---- for
end
push_user_api() 
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
----update push user choice list on startup
  Update_push_user_List = {}
  if Push_user_choice ~= nil then 
  Push_user_choice = {}
  else
  Push_user_choice = self.store.push_user_List_selected
  end
---------------------------- 
  function Update_push_user_List_fun()
  local rownumber = 1
    for ind,val in pairs(push_user_id) do
        --print("ID",push_user_id[val])
        --print("Name",push_user_name[val])
        --print("Email",push_user_email[val])
        Update_push_user_List[rownumber] = {text = "ID:"..push_user_id[val].." Name: "..push_user_name[val].." Email: "..push_user_email[val].."", type = "option", value = ""..push_user_id[val]..""}
        --print("Update_push_user_List",json.encode(Update_push_user_List))
        rownumber = rownumber +1
    end
    self:updateView("Push_user_choice", "options", Update_push_user_List)
    --self:updateView("Push_user_choice", "selectedItems", push_user_List_selected)
  end 
Update_push_user_List_fun() 
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
-----Push user dropdown list handler
---@diagnostic disable-next-line
  function QuickApp:Push_user_choice(args)
    Push_user_choice = args.values[1]
    --print("Push_user_choice0", json.encode(Push_user_choice))
    Push_user_List_trigger = nil
    Push_user_List_trigger = {}
    for ind,val in ipairs(Push_user_choice) do
    Push_user_List_trigger[val] = val
    end---for 
    self.store.Push_user_List_trigger = Push_user_List_trigger
    self.store.push_user_List_selected = Push_user_choice
    self:updateView("Push_user_choice", "selectedItems", Push_user_choice)
  end
self:updateView("Push_user_choice", "selectedItems", Push_user_choice)
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
----update push device api
Push_device_id = {}  
Push_device_name = {}
function Push_device_api()
  --print("push_user_id2",json.encode(push_user_id))
  local rownumber = 1
  for ind,val in pairs(push_user_id) do ---for 1
      --print("ind1",ind)
      val = json.encode(val)
      local var = api.get("/devices?property=[lastLoggedUser,"..val.."]")
        for ind,val in ipairs(var)do   ---- for 2
          Push_device_id[val.id] = val.id 
          Push_device_name[val.id] = val.name 
          --print("Device ID",Push_device_id[val.id])
          --print("Device name",Push_device_name[val.id])
        end---- for 2
  end ---for 1
end---end function Push_device_api
Push_device_api() 
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
----update push device choice list on startup
  Update_push_device_List = {}
  if Push_device_choice ~= nil then 
  Push_device_choice = {}
  else
  Push_device_choice = self.store.push_device_List_selected
  end
---------------------------- 
  function Update_push_device_List_fun()
  local rownumber = 1
    for ind,val in pairs(Push_device_id) do
        --print("ID",Push_device_id[val])
        --print("Name",Push_device_name[val])
        --print("Email",push_device_email[val])
        Update_push_device_List[rownumber] = {text = "ID:"..Push_device_id[val].." Name: "..Push_device_name[val].."", type = "option", value = ""..Push_device_id[val]..""}
        --print("Update_push_device_List",json.encode(Update_push_device_List))
        rownumber = rownumber +1
    end
    self:updateView("Push_device_choice", "options", Update_push_device_List)
    --self:updateView("Push_device_choice", "selectedItems", push_device_List_selected)
  end 
Update_push_device_List_fun()  
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
-----Push device dropdown list handler
---@diagnostic disable-next-line
  function QuickApp:Push_device_choice(args)
    Push_device_choice = args.values[1]
    --print("Push_device_choice0", json.encode(Push_device_choice))
    Push_device_List_trigger = nil
    Push_device_List_trigger = {}
    for ind,val in ipairs(Push_device_choice) do
    Push_device_List_trigger[val] = val
    end---for 
    self.store.Push_device_List_trigger = Push_device_List_trigger
    self.store.push_device_List_selected = Push_device_choice
    self:updateView("Push_device_choice", "selectedItems", Push_device_choice)
  end
self:updateView("Push_device_choice", "selectedItems", Push_device_choice)
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
-----send Push notification function: User massage push
function Send_push_user(text)
  local text = (text or "User massage push")
  local ID = {}
  if Push_user_choice ~= nil then
    for ind,val in pairs(Push_user_choice) do
---@diagnostic disable-next-line
    ID = tonumber(val) 
---@diagnostic disable-next-line
    hub.alert('push', {[1] = ID, }, ''..text..'', false, '', false)
    end ---for
  end--if Push_user_choice ~= nil then
end ---function Send_push_user
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
-----send Push notification function: Email message
function Send_email_user(text)
  local text = (text or "Email message")
  local ID = 0
  if Push_user_choice ~= nil then
    for ind,val in pairs(Push_user_choice) do
---@diagnostic disable-next-line
    ID = tonumber(val) 
---@diagnostic disable-next-line
    hub.alert('email', {[1] = ID, }, ''..text..'', false, '', false)
    end ---for
  end--if Push_user_choice ~= nil then
end ---function Send_email_user
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
-----send Push notification function: Device push massage
function Send_simplePush_user(text)
  local text = (text or "device push massage")
  local deviceID = {}
  if Push_device_choice ~= nil then
    for ind,val in pairs(Push_device_choice) do
    ID = tonumber(val) 
---@diagnostic disable-next-line
    hub.alert('simplePush', {[1] = ID, }, ''..text..'', false, '', false)
    end ---for
  end--if Push_device_choice ~= nil then
end ---function Send_simplePush_user

-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
-----send Push notification function: device push massage interactive yes/no scene  name test
Scene_id = self:getVariable("Scene_id") 
---@diagnostic disable-next-line
function send_interactive_Push_user(text,title,Scene_id)
  --print("Push_user_choice",json.encode(Push_user_choice))
  local text_message = (text or "device push massage interactive yes/no scene  name test")
  local text_tittle = (title or "Interactive Push")
  local Scene_id = Scene_id or 11   ----
  local deviceID = {}
  if Push_device_choice ~= nil then
    for ind,val in pairs(Push_device_choice) do
    ID = tonumber(val) 
    api.post("/mobile/push", {["data"] = {["sceneId"] = Scene_id, }, ["title"] = ""..text_tittle.."", ["service"] = "Scene", ["category"] = "YES_NO", ["action"] = "Run", ["mobileDevices"] = {[1] = ID, }, ["message"] = ""..text_message.."", })
    end ---for ind,val in pairs(Push_device_choice) do
  end--if Push_device_choice ~= nil then
end ---function Send_simplePush_user

--api.post("/mobile/push", {["data"] = {["deviceId"] = 22, ["actionName"] = "onReleased", ["args"] = {[1] = "button_ID_0_2", }, }, ["title"] = "device push title", ["service"] = "Device", ["category"] = "RUN_CANCEL", ["action"] = "RunAction", ["mobileDevices"] = {[1] = 38, }, ["message"] = "device push massage interactive \nrun/cancel device push button", })


-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---label function setup

---@diagnostic disable-next-line
function info_push_user()
  local line = ""..color1.."Toggle Push User and/or Device ON/OFF"
  line = ""..line.."\n"..color1..""
  line = ""..line.."\n"..color1.."Choose user or device for push message below:"..color2.." "
  line = ""..line.."\n"..color1..""


  self:updateView("info_push_user","text","<table width= 350px border = 0px><td align =left><section align="..left_right.."><font size='"..Fontsize.."'><tt> "..line.."   </tt></font></section>")
end
info_push_user()

-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---label function setup

---@diagnostic disable-next-line
function info_push_device()
  local line = ""..color1.."Toggle Push User and/or Device ON/OFF"
  line = ""..line.."\n"..color1..""
  line = ""..line.."\n"..color1.."Choose user or device for push message below:"..color2.." "
  line = ""..line.."\n"..color1..""


  self:updateView("info_push_device","text","<table width= 350px border = 0px><td align =left><section align="..left_right.."><font size='"..Fontsize.."'><tt> "..line.."   </tt></font></section>")
end
info_push_device()

-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------






































-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------

local c0,t0 = os.clock(),os.time()
local kb = "0.0001"
local cpp = 0.0001
local kbc = "0.0001"
setInterval(function()
  --collectgarbage("collect")
  kbc = collectgarbage("count")
  collectgarbage("collect")
  kb = collectgarbage("count")
  local c1,T1=os.clock(),os.time()
  cpp = (c1-c0)/(T1-t0)

  c0,t0=c1,T1
  Setup_manual()
  -- kb is Kb used by the Lua interpreter
  -- cpp is the percentage of used cpu time over the last minute
 end, refresh_mem *1000)



-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
function Setup_manual()
  local function fmt(v) 
    local val = string.format("%02d",v)
    return val
    end
  local kb_val = string.format("%.2f",tonumber(kb))
  if kb_val > self.store.kb_val_max then
    self.store.kb_val_max = kb_val
  end
  local kbc_val = string.format("%.2f",tonumber(kbc))
  if kbc_val > self.store.kbc_val_max then
    self.store.kbc_val_max = kbc_val
  end
  local cpp_val = string.format("%.4f",tonumber(cpp)) 
  if cpp_val > self.store.cpp_val_max then
    self.store.cpp_val_max = cpp_val
  end




  local line = ""
  line = ""..line..""..color1.."<hr width=350px color="..color4.." size=50px />"
  line = ""..line.."<br />"..color1.."Updates every: "..color2..""..refresh_mem.." Sec"
  line = ""..line.."<br />"..color1.."Memory Used: "..color2..""..kb_val.." kb"
  line = ""..line.."<br />"..color1.."Memory Used Max: "..color2..""..self.store.kb_val_max.." kb"
  line = ""..line.."<br />"..color1.."Memory Used tot: "..color2..""..kbc_val.." kb"
  line = ""..line.."<br />"..color1.."Memory Used tot Max: "..color2..""..self.store.kbc_val_max.." kb"
  line = ""..line.."<br />"..color1.."Cpu Usage: "..color2..""..cpp_val.." %"
  line = ""..line.."<br />"..color1.."Cpu Usage Max: "..color2..""..self.store.cpp_val_max.." %"

  line = ""..line..""..color1.."<hr width=350px color="..color4.." size=50px />"
  line = ""..line.."<br />"..color1.."        "
  line = ""..line.."<br />"..color1.."        "
  line = ""..line.."<br />"..color1.."        "
  line = ""..line.."<br />"..color1.."        "
  line = ""..line.."<br />"..color1.."        "
  line = ""..line.."<br />"..color1.."        "
  line = ""..line.."<br />"..color1.."        "
  line = ""..line.."<br />"..color1.."        "

  

  line = ""..line.."<br />"..color1.."Last Time QA Restarted: "..start_date..""

  self:updateView("Setup_manual", "text",""..l_start.."<section align="..left_right.."><font size='"..Fontsize.."'><pre>"..line.."</pre></font></section>"..l_end.."")
end--function Setup_manual()
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------
Setup_manual()
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------
hub.setTimeout(15*1000, function()  
  Setup_manual()
end)
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------








-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------
---@diagnostic disable-next-line
function QuickApp:Restart(args)
  self:updateView("Restart", "value", "true")
  Restart()
end
-------------------------------
function Restart()
  hub.setTimeout(200, function()  
    self:updateView("Restart", "value", "false")
  end)
  hub.setTimeout(2*1000, function()  
    plugin.restart()
  end)
end
-------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------











---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------
------update label for lines between the "groups of functions in the QA view"  
local infoline = "<hr width=400px color="..color4.." size=2px />"
self:updateView("infoline1", "text",infoline)
self:updateView("infoline2", "text",infoline)
self:updateView("infoline3", "text",infoline)
self:updateView("infoline4", "text",infoline)
self:updateView("infoline5", "text",infoline)
self:updateView("infoline6", "text",infoline)
self:updateView("infoline7", "text",infoline)
self:updateView("infoline8", "text",infoline)
self:updateView("infoline9", "text",infoline)
self:updateView("infoline10", "text",infoline)
self:updateView("infoline11", "text",infoline)
self:updateView("infoline12", "text",infoline)
self:updateView("infoline13", "text",infoline)
self:updateView("infoline14", "text",infoline)
self:updateView("infoline15", "text",infoline)
self:updateView("infoline16", "text",infoline)
self:updateView("infoline17", "text",infoline)
self:updateView("infoline18", "text",infoline)
self:updateView("infoline19", "text",infoline)
self:updateView("infoline20", "text",infoline)
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------
---startup timer. 
self:debug("ID:"..quickapp_id.." Name; "..self.name.." has started in the room: "..self_room_name.."")
local endtime = os.clock()
print(""..quickapp_id.." Used: ", endtime-starttime,"sec to start")
    else---if check_qa_enabled == true then
    print("ID:"..quickapp_id.." Name; "..self.name.." is Disabled")
    end ---if check_qa_enabled == true then
end --oninit
---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------
