--%%name:GenericDevice
--%%type:com.fibaro.genericDevice
--%%description:"My description"
--%%desktop:true

-- Generic device type have no default actions to handle 

function QuickApp:onInit()
    self:debug(self.name,self.id)
    if not api.get("/devices/"..self.id).enabled then
        self:debug(self.name,self.id,"Device is disabled")
        return
    end
end 