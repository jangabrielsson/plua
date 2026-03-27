--%%name:GenericDevice
--%%type:com.fibaro.genericDevice
--%%description:Generic device template

-- No required actions or properties.
-- Define your own methods and call self:updateProperty as needed.

function QuickApp:onInit()
    self:debug(self.name, self.id)
end
