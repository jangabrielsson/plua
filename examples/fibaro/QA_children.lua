--%%name:Children
--%%type:com.fibaro.binarySwitch
--%%debug:false
--%%var:X=9
-- %%offline:true
-- %%desktop:true
--%%save:QA_children.fqa

local UI = [[
[
      {
        "components": [
          {
            "eventBinding": {
              "onLongPressDown": [
                {
                  "params": {
                    "actionName": "UIAction",
                    "args": [
                      "onLongPressDown",
                      "btn1"
                    ]
                  },
                  "type": "deviceAction"
                }
              ],
              "onLongPressReleased": [
                {
                  "params": {
                    "actionName": "UIAction",
                    "args": [
                      "onLongPressReleased",
                      "btn1"
                    ]
                  },
                  "type": "deviceAction"
                }
              ],
              "onReleased": [
                {
                  "params": {
                    "actionName": "UIAction",
                    "args": [
                      "onReleased",
                      "btn1"
                    ]
                  },
                  "type": "deviceAction"
                }
              ]
            },
            "name": "btn1",
            "style": {
              "weight": "1.0"
            },
            "text": "MyButton",
            "type": "button",
            "visible": true
          }
        ],
        "style": {
          "weight": "1.0"
        },
        "type": "horizontal"
      }
    ]
]]
---@class MyChild : QuickAppChild
MyChild = {}
class 'MyChild'(QuickAppChild)
function MyChild:__init(dev)
  QuickAppChild.__init(self,dev)
  self:debug("onInit",self.name,self.id)
end
function MyChild:turnOn() self:updateProperty("value",true) end
function MyChild:turnOff() self:updateProperty("value",false) end

function QuickApp:onInit()
  self:debug(self.name, self.id)

  -- Create children
  for i = 1,1 do 
    local child = self:createChildDevice({
      name="MyChild"..i,
      type="com.fibaro.binarySwitch",
      initialProperties = { uiView = (json.decode(UI)) }
    },MyChild)
    self:debug("Created child",child.name,child.id)
    --api.post("/plugins/"..child.id.."/variables",{ name='test', value="Foo"}) -- create var if not exist
  end
  local children = api.get("/devices?parentId="..self.id)
  for _,c in ipairs(children) do 
    print(c.name,c.id)

  end

  setInterval(function() 
    --setTimeout(function() end,10)
    -- print(json.encode(fibaro.plua.lib.getRuntimeState()))
  end,2000) 
end

function QuickApp:turnOn() print("ON") self:updateProperty("value",true) end
function QuickApp:turnOff() print("OFF") self:updateProperty("value",false) end
