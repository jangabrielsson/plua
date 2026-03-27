--%%name:ColorController
--%%type:com.fibaro.colorController
--%%description:Color controller template

-- Actions: turnOn, turnOff, setValue, setColor
-- color property format: "r,g,b,w"  eg. "200,10,100,255"
-- value property: integer 0-99 (brightness)

function QuickApp:turnOn()
    self:updateProperty("value", 99)
end

function QuickApp:turnOff()
    self:updateProperty("value", 0)
end

-- value: integer 0-99
function QuickApp:setValue(value)
    self:updateProperty("value", value)
end

-- r, g, b, w: integers 0-255
function QuickApp:setColor(r, g, b, w)
    local color = string.format("%d,%d,%d,%d", r or 0, g or 0, b or 0, w or 0)
    self:updateProperty("color", color)
    self:updateProperty("colorComponents", {red=r, green=g, blue=b, white=w})
end

function QuickApp:onInit()
    self:debug(self.name, self.id)
    self:updateProperty("colorComponents", {red=0, green=0, blue=0, white=0})
end
