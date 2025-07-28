------------------ Selectable ------------------
local function mkKey(item) return tostring(item):gsub("[^%w]","") end
Selectable = Selectable
class 'Selectable'
function Selectable:__init(qa,id)
  local fun = nil
  assert(type(qa)=='userdata',"First argument must be the QuickApp (self)")
  assert(self.text,"Selectable:text(item) not defined")
  assert(self.value,"Selectable:value(item) not defined")
  for _,c in ipairs(qa.properties.uiCallbacks or {}) do
    if c.name==id then fun = c.callback break end
  end
  assert(fun,"Selectable "..tostring(id).." not found in uiCallbacks")
  self.id = id
  self.qa = qa
  self.fun = fun
  self.qa[fun] = function(_,event)
    if self.map == nil then
      return fibaro.warning(__TAG,"Selectable "..self.id.." not initialized")
    end
    self.key = tostring(event.values[1])
    self.item = self.map[self.key]
    if self.item == nil then
      return fibaro.warning(__TAG,"Selecable: Invalid value: "..self.key)
    end
    self._value = self:value(self.item)
    if self.selected then
      self:selected(self.item)
    end
  end
end
function Selectable:update(list)
  local r = {}
  for _,item in pairs(list) do
    if self.filter then 
      if self:filter(item) then table.insert(r,item) end
    else table.insert(r,item) end
  end
  if self.sort then
    local function sort(a,b) return self:sort(a,b) end
    table.sort(r,sort) 
  end
  self.list = r
  self.map = {}
  local options = {}
  for _,item in ipairs(self.list) do
    local value = mkKey(self:value(item))
    local name = self:text(item)
    self.map[value] = item
    table.insert(options,{text=name,type='option',value=value})
  end
  self.options = options
  --Get around bug that don't update the list if empty
  if next(options) == nil then options={{text="",type="option",value=""}} end
  self:_updateList("options",options)
  self:_updateList("selectedItem","")
end
function Selectable:select(value)
  value = mkKey(value)
  if not self.map[value] then 
    return fibaro.warning(__TAG,"Invalid value: "..value)
  end
  self:_updateList("selectedItem",value)
  self.qa[self.fun](self.qa,{values={value}})
  self:selected(self.map[value])
end

function Selectable:_updateList(prop,value)
  self.qa:updateView(self.id,prop,value)
end