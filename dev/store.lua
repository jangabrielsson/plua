
function QuickApp:onInit()
    local qa = self
    self.store = setmetatable({}, { 
    __index = function(t, k) return self:internalStorageGet(k) end,
    __newindex = function(t, k, v) self:internalStorageSet(k, v) end,
    __pairs = function(self) return pairs(qa:internalStorageGet()) end
    })

    if self.store.x == nil then
        self.store.x = {
            a = 1,
            b = 2,
            c = 3
        }
        self.store.a = 99
    end


    print(json.encode(self.store.x))
    for k,v in pairs(self.store) do
        print(k,v)
    end
end 
