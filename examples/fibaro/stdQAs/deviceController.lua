--%%name:DeviceController
--%%type:com.fibaro.deviceController
--%%description:"Device controller template"
--%%desktop:true

-- Device Controller is a little more advanced than other types. 
-- It can create child devices, so it can be used for handling multiple physical devices.
-- E.g. when connecting to a hub, some cloud service or just when you want to represent a single physical device as multiple endpoints.

-- Sample class for handling your binary switch logic. You can create as many classes as you need.
-- Each device type you create should have its class which inherits from the QuickAppChild type.

---@class MyBinarySwitch : QuickAppChild
MyBinarySwitch = {}
class 'MyBinarySwitch'(QuickAppChild)

-- __init is a constructor for this class. All new classes must have it.
function MyBinarySwitch:__init(device)
    -- You should not insert code before QuickAppChild.__init. 
    QuickAppChild.__init(self, device) 

    self:debug("MyBinarySwitch init")   
end

function MyBinarySwitch:turnOn()
    self:debug("child", self.id, "turned on")
    self:updateProperty("value", true)
end

function MyBinarySwitch:turnOff()
    self:debug("child", self.id, "turned off")
    self:updateProperty("value", false)
end 

function QuickApp:onInit()
    self:debug("QuickApp:onInit")

    -- Setup classes for child devices.
    -- Here you can assign how child instances will be created.
    -- If type is not defined, QuickAppChild will be used.
    self:initChildDevices({
        ["com.fibaro.binarySwitch"] = MyBinarySwitch,
    })

    -- Print all child devices.
    self:debug("Child devices:")
    for id,device in pairs(self.childDevices) do
        self:debug("[", id, "]", device.name, ", type of: ", device.type)
    end
end

-- Sample method to create a new child. It can be used in a button. 
function QuickApp:createChild()
    local child = self:createChildDevice({
        name = "child",
        type = "com.fibaro.binarySwitch",
    }, MyBinarySwitch)

    self:trace("Child device created: ", child.id)
end

-- Device controller type have no actions to handle
