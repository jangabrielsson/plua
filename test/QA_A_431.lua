--%%name:QA A
--%%type:com.fibaro.binarySensor
--%%project:431
--%%u:{button="button1",text="btn",visible=true,onLongPressDown="",onLongPressReleased="",onReleased="foo"}
--%%u:{slider="slider",text="",min="0",max="100",visible=true,onChanged="bar"}

-- Binary sensor type have no actions to handle
-- To update binary sensor state, update property "value" with boolean
-- Eg. self:updateProperty("value", true) will set sensor to breached state

-- To update controls you can use method self:updateView(<component ID>, <component property>, <desired value>). Eg:  
-- self:updateView("slider", "value", "55") 
-- self:updateView("button1", "text", "MUTE") 
-- self:updateView("label", "text", "TURNED ON") 

-- This is QuickApp inital method. It is called right after your QuickApp starts (after each save or on gateway startup). 
-- Here you can set some default values, setup http connection or get QuickApp variables.
-- To learn more, please visit: 
--    * https://manuals.fibaro.com/home-center-3/
--    * https://manuals.fibaro.com/home-center-3-quick-apps/

function QuickApp:foo(ev)
   self:debug("foo",json.encode(ev))
end

function QuickApp:bar(ev)
   self:debug("bar",json.encode(ev))
end

function QuickApp:onInit() 
end
