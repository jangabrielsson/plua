-- ** Device headers **
--%%name:Multi PositionSwitch
--%%type:com.fibaro.multiPositionSwitch
--%%proxy:true

--** Development hearders **
--%%debug=true
--%%desktop:true
--%%offline:false

local function f1(value) print("f1 postion: "..value) end

function QuickApp:updatePositions(tab)
  self.pmap = {}
  for _,v in ipairs(tab) do self.pmap[v.name]={action=v.action} v.action=nil end
  self:updateProperty("availablePositions", tab)
end

function QuickApp:getPosition() return fibaro.getValue(self.id,"position") end

function QuickApp:setPosition(value)
    self:debug("Set Postion Value:", value)
    if self.pmap[value or ""] then
        self.pmap[value].action(value)
        self:updateProperty('position',value)
    end
end

function QuickApp:turnOn()
  self:setPosition('A')
  self:updateProperty('value',true)
end

function QuickApp:toggle()
  if fibaro.getValue(self.id,'value') then self:turnOff()
  else self:turnOn() end
end

function QuickApp:turnOff()
  self:setPosition('D')
  self:updateProperty('value',false)
end

function QuickApp:onInit()
  self:debug("init")
  self:updatePositions{
    {label = "label A", name="A", action=f1},
    {label = "label B", name="B", action=f1},
    {label = "label C", name="C", action=f1},
    {label = "label D", name="D", action=f1},
  }
  self:debug("CurrentPosition", self:getPosition())
  --if self:getPosition()=="" then -- initialise 
    self:updateProperty("position","D") -- self:setPosition('D') at init
  --end
end