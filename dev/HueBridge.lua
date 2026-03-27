--%%name:Hue Bridge
--%%type:com.fibaro.deviceController
--%%var:HueUser=config.Hue_user
--%%var:HueIP=config.Hue_ip
--%%var:pollInterval=30
--%%var:hueChildMap={}
--%%u:{label="statusLbl",text="Connecting..."}
--%%u:{{button="refreshBtn",text="Refresh",onReleased="onRefresh"},{button="syncBtn",text="Sync Lights",onReleased="onSync"}}

-- Philips Hue V2 (CLIP v2) integration.
-- Creates a QuickAppChild for each Hue light and keeps its value in sync.
-- Child types: com.fibaro.binarySwitch (on/off), com.fibaro.multilevelSwitch (dimmer),
--              com.fibaro.colorController (colour/colour-temp).

-----------------------------------------------------------------------
-- Child class — shared by all Hue light types
-----------------------------------------------------------------------
class 'HueLight'(QuickAppChild)

function HueLight:__init(device)
    QuickAppChild.__init(self, device)
    self.hueId = nil  -- set by parent after init
end

function HueLight:onInit()
    self:debug("HueLight ready:", self.name, self.id)
end

-- Called by parent to reflect latest Hue state
function HueLight:update(light)
    local on = light.on and light.on.on or false
    if light.dimming then
        local bri = math.floor(light.dimming.brightness + 0.5)
        self:updateProperty("value", on and bri or 0)
    else
        self:updateProperty("value", on)
    end
end

-- Fibaro action handlers
function HueLight:turnOn()
    self.parent:setLight(self.hueId, {on = {on = true}})
    self:updateProperty("value", self.type == "com.fibaro.binarySwitch" and true or 100)
end

function HueLight:turnOff()
    self.parent:setLight(self.hueId, {on = {on = false}})
    self:updateProperty("value", self.type == "com.fibaro.binarySwitch" and false or 0)
end

function HueLight:setValue(val)
    val = tonumber(val) or 0
    self.parent:setLight(self.hueId, {
        on      = {on = val > 0},
        dimming = {brightness = math.min(100, math.max(0, val))},
    })
    self:updateProperty("value", val)
end

-----------------------------------------------------------------------
-- Helpers
-----------------------------------------------------------------------
local function lightFibaroType(light)
    if light.color then return "com.fibaro.colorController" end
    if light.dimming then return "com.fibaro.multilevelSwitch" end
    return "com.fibaro.binarySwitch"
end

local function lightInitialValue(ftype)
    return ftype == "com.fibaro.binarySwitch" and false or 0
end

-----------------------------------------------------------------------
-- Parent QA
-----------------------------------------------------------------------

-- Low-level HTTP wrapper for Hue CLIP v2
function QuickApp:hueReq(method, path, body, onSuccess, onError)
    local url = "https://" .. self.hueIP .. "/clip/v2" .. path
    local opts = {
        options = {
            method  = method,
            headers = {["hue-application-key"] = self.hueUser},
            checkCertificate = false,
        },
        success = function(resp)
            if resp.status >= 200 and resp.status < 300 then
                local ok, data = pcall(json.decode, resp.data)
                if ok then (onSuccess or function() end)(data)
                else self:error("JSON decode failed:", resp.data) end
            else
                self:error(string.format("Hue %s %s → %d", method, path, resp.status))
                if onError then onError(resp.status) end
            end
        end,
        error = function(err)
            self:error("Hue request error:", tostring(err))
            if onError then onError(err) end
        end,
    }
    if body then
        opts.options.data = json.encode(body)
        opts.options.headers["Content-Type"] = "application/json"
    end
    net.HTTPClient():request(url, opts)
end

-- Control a single light
function QuickApp:setLight(hueId, body)
    self:hueReq("PUT", "/resource/light/" .. hueId, body)
end

-- Update Fibaro children from Hue light list
function QuickApp:updateChildren(lights)
    for _, light in ipairs(lights) do
        local childId = self.hueToChild[light.id]
        if childId then
            local child = self.childDevices[childId]
            if child then child:update(light) end
        end
    end
end

-- Build/repair children on startup
function QuickApp:syncChildren(lights)
    local stored = self:getVariable("hueChildMap")
    self.hueToChild = (stored ~= "" and json.decode(stored)) or {}

    self:initChildDevices({
        ["com.fibaro.binarySwitch"]    = HueLight,
        ["com.fibaro.multilevelSwitch"] = HueLight,
        ["com.fibaro.colorController"] = HueLight,
    })

    -- Wire hueId onto already-existing children
    for hueId, childId in pairs(self.hueToChild) do
        local child = self.childDevices[childId]
        if child then child.hueId = hueId end
    end

    -- Create children for lights we haven't seen before
    local changed = false
    for _, light in ipairs(lights) do
        local hueName = light.metadata and light.metadata.name or ("Light " .. light.id)
        if not self.hueToChild[light.id] then
            local ftype = lightFibaroType(light)
            self:debug("Creating child:", hueName, ftype)
            local child = self:createChildDevice({
                name = hueName,
                type = ftype,
                initialProperties = {value = lightInitialValue(ftype)},
            }, HueLight)
            child.hueId = light.id
            self.hueToChild[light.id] = child.id
            changed = true
        else
            -- Rename existing child if Hue name has changed
            local child = self.childDevices[self.hueToChild[light.id]]
            if child and child.name ~= hueName then
                self:debug("Renaming child", child.id, "->", hueName)
                api.put("/devices/" .. child.id, {name = hueName})
            end
        end
    end

    if changed then
        self:setVariable("hueChildMap", json.encode(self.hueToChild))
    end

    self:updateChildren(lights)
    self:updateView("statusLbl", "text",
        string.format("Lights: %d  updated %s", #lights, os.date("%H:%M:%S")))
end

-- Regular poll — just updates values, no structural changes
function QuickApp:poll()
    self:hueReq("GET", "/resource/light", nil, function(resp)
        local lights = resp.data or {}
        self:updateChildren(lights)
        self:updateView("statusLbl", "text",
            string.format("Lights: %d  polled %s", #lights, os.date("%H:%M:%S")))
    end)
end

-- Button: manual refresh (value update only)
function QuickApp:onRefresh()
    self:poll()
end

-- Button: full sync (create missing children)
function QuickApp:onSync()
    self:hueReq("GET", "/resource/light", nil, function(resp)
        self:syncChildren(resp.data or {})
    end)
end

function QuickApp:onInit()
    self:debug(self.name, self.id)

    self.hueUser = self:getVariable("HueUser")
    self.hueIP   = self:getVariable("HueIP")

    if self.hueUser == "" or self.hueIP == "" then
        self:error("HueUser and/or HueIP variables not set")
        return
    end

    -- Initial fetch: create/reconnect children, then start polling
    self:hueReq("GET", "/resource/light", nil, function(resp)
        self:syncChildren(resp.data or {})

        local interval = math.max(5, tonumber(self:getVariable("pollInterval")) or 30)
        setInterval(function() self:poll() end, interval * 1000)
    end)
end
