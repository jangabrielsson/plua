--%%name:ColorController
--%%type:com.fibaro.colorController
--%%description:Color controller template
--%%desktop:true

-- Color controller type should handle actions: turnOn, turnOff, setValue, setColor
-- To update color controller state, update property color with a string in the following format: "r,g,b,w" eg. "200,10,100,255"
-- To update brightness, update property "value" with integer 0-99

function QuickApp:turnOn()
    self:debug("color controller turned on")
    self:updateProperty("value", 99)
end

function QuickApp:turnOff()
    self:debug("color controller turned off")
    self:updateProperty("value", 0)    
end

-- Value is type of integer (0-99)
function QuickApp:setValue(value)
    self:debug("color controller value set to: ", value)
    self:updateProperty("value", value)    
end

-- Color is type of table, with format [r,g,b,w]
-- Eg. relaxing forest green, would look like this: [34,139,34,150]
function QuickApp:setColor(r,g,b,w)
    local color = string.format("%d,%d,%d,%d", r or 0, g or 0, b or 0, w or 0) 
    self:debug("color controller color set to: ", color)
    self:updateProperty("color", color)
    self:setColorComponents({red=r, green=g, blue=b, white=w})
end

function QuickApp:setColorComponents(colorComponents)
    local cc = self.properties.colorComponents
    local isColorChanged = false
    for k,v in pairs(colorComponents) do
        if cc[k] and cc[k] ~= v then
            cc[k] = v
            isColorChanged = true
        end
    end
    if isColorChanged == true then
        self:updateProperty("colorComponents", cc)
        self:setColor(cc["red"], cc["green"], cc["blue"], cc["white"])
    end
end

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
    self:updateProperty("colorComponents", {red=0, green=0, blue=0, warmWhite=0})
end 