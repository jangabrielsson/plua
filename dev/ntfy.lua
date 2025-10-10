--%%name:NTFY Notification Service
--%%type:com.fibaro.genericDevice
--%%save:ntfy.fqa

local http = net.HTTPClient()
local main 
local topic = "jdfhghdkfghhg",  -- for testing
math.randomseed(os.time())      -- Generate random response topic
local respTopic = ""
for i = 1, 50 do
	respTopic = respTopic .. string.char(math.random(97, 122))
end

function QuickApp:onInit()
    self:debug("NTFY Notification Service initialized", self.id)
    
    -- Configuration
    self.config = {
        server = "https://ntfy.sh",  -- Change to your server
        defaultTopic = topic or "my-alerts",
        defaultResponseTopic = respTopic or "my-responses",
        timeout = 10
    }

    self:setupListener()
    -- setTimeout(function() self:test() end,0)
end

-- Priority levels with descriptions
local PRIORITIES = {
    MIN = { value = 1, name = "min", description = "No vibration/sound, under fold in notifications" },
    LOW = { value = 2, name = "low", description = "No vibration/sound, in notification drawer" },
    DEFAULT = { value = 3, name = "default", description = "Normal vibration and sound" },
    HIGH = { value = 4, name = "high", description = "Long vibration, pop-over notification" },
    MAX = { value = 5, name = "max", description = "Very long vibration, urgent pop-over" },
    URGENT = { value = 5, name = "urgent", description = "Alias for max priority" }
}

-- Common emoji tags that convert to symbols
local EMOJI_TAGS = {
    -- Positive/Success
    ["+1"] = "👍", ["thumbsup"] = "👍",
    ["heavy_check_mark"] = "✅", ["checkmark"] = "✅", ["white_check_mark"] = "☑️",
    ["tada"] = "🎉", ["partying_face"] = "🥳",
    ["green_circle"] = "🟢", ["green_heart"] = "💚",
    
    -- Warnings/Alerts  
    ["warning"] = "⚠️", ["exclamation"] = "❗",
    ["rotating_light"] = "🚨", ["red_circle"] = "🔴",
    ["triangular_flag_on_post"] = "🚩", ["loudspeaker"] = "📢",
    
    -- Errors/Critical
    ["-1"] = "👎", ["thumbsdown"] = "👎",
    ["skull"] = "💀", ["x"] = "❌", ["cross_mark"] = "❌",
    ["no_entry"] = "⛔", ["no_entry_sign"] = "🚫",
    ["fire"] = "🔥", ["red_heart"] = "❤️",
    
    -- Technology/System
    ["computer"] = "💻", ["cd"] = "💿", ["floppy_disk"] = "💾",
    ["gear"] = "⚙️", ["wrench"] = "🔧", ["hammer"] = "🔨",
    ["electric_plug"] = "🔌", ["battery"] = "🔋",
    
    -- Home/IoT
    ["house"] = "🏠", ["door"] = "🚪", ["lock"] = "🔒", ["unlock"] = "🔓",
    ["key"] = "🔑", ["bell"] = "🔔", ["camera"] = "📷",
    ["thermometer"] = "🌡️", ["bulb"] = "💡",
    
    -- Communication
    ["email"] = "📧", ["phone"] = "📞", ["mobile_phone"] = "📱",
    ["speech_balloon"] = "💬", ["mega"] = "📣",
    
    -- Time/Calendar
    ["clock"] = "🕐", ["alarm_clock"] = "⏰", ["calendar"] = "📅",
    ["hourglass"] = "⏳", ["stopwatch"] = "⏱️",
    
    -- Weather
    ["sunny"] = "☀️", ["cloud"] = "☁️", ["rain"] = "🌧️",
    ["snow"] = "❄️", ["zap"] = "⚡", ["tornado"] = "🌪️",
    
    -- Transportation
    ["car"] = "🚗", ["truck"] = "🚚", ["train"] = "🚂",
    ["airplane"] = "✈️", ["rocket"] = "🚀",
    
    -- Medical/Health
    ["pill"] = "💊", ["syringe"] = "💉", ["hospital"] = "🏥",
    ["ambulance"] = "🚑", ["heart"] = "❤️",
    
    -- Finance/Money
    ["money"] = "💰", ["dollar"] = "💲", ["chart"] = "📊",
    ["credit_card"] = "💳", ["bank"] = "🏦",
    
    -- Misc Useful
    ["star"] = "⭐", ["sparkles"] = "✨", ["trophy"] = "🏆",
    ["gift"] = "🎁", ["balloon"] = "🎈", ["eyes"] = "👀",
    ["facepalm"] = "🤦", ["shrug"] = "🤷", ["thinking"] = "🤔"
}

-- Helper function to get priority info
function QuickApp:getPriorityInfo(priority)
    for name, info in pairs(self.PRIORITIES) do
        if info.value == priority or info.name == priority then
            return info
        end
    end
    return self.PRIORITIES.DEFAULT
end

-- Helper function to get available emoji for a tag
function QuickApp:getEmojiForTag(tag)
    return self.EMOJI_TAGS[tag] or tag
end

-- Get all available emoji tags
function QuickApp:getAvailableEmojis()
    local emojis = {}
    for tag, emoji in pairs(self.EMOJI_TAGS) do
        table.insert(emojis, {tag = tag, emoji = emoji})
    end
    table.sort(emojis, function(a, b) return a.tag < b.tag end)
    return emojis
end

--[[
Send ntfy notification with full options support

Parameters (all optional except message):
{
    topic = "alerts",                    -- Target topic (uses default if not set)
    message = "Alert message",           -- Required: message content
    title = "Alert Title",               -- Message title
    priority = 4,                        -- 1=min, 2=low, 3=default, 4=high, 5=max
    tags = {"warning", "skull"},         -- Array of tags/emojis
    click = "https://example.com",       -- URL to open on click
    attach = "https://example.com/file", -- External attachment URL
    filename = "report.pdf",             -- Attachment filename override
    markdown = true,                     -- Enable markdown formatting
    icon = "https://example.com/icon",   -- Notification icon URL
    delay = "30m",                       -- Schedule delivery (30m, 1h, tomorrow 10am)
    email = "user@example.com",          -- Forward to email
    actions = {                          -- Action buttons (max 3)
        {
            action = "view",
            label = "Open Dashboard", 
            url = "https://dashboard.com",
            clear = false
        },
        {
            action = "http",
            label = "Execute Action",
            url = "https://api.example.com/action",
            method = "POST",
            headers = { Authorization = "Bearer token" },
            body = '{"key": "value"}',
            clear = true
        },
        {
            action = "fibaro",
            label = "Fibaro action",
            headers = { Authorization = "Bearer token" },
            callback = function() print("Fibaro action executed") end,
            clear = true
        }
    },
    cache = "yes",                       -- Cache message server-side
    firebase = "yes",                    -- Forward to Firebase
    auth = {                             -- Authentication (if required)
        token = "tk_xxxxx"               -- Access token
        -- OR username = "user", password = "pass"
    }
}
--]]

local REF = 0
local refs = {}
local function fibaroActions(self,actions)
    assert(type(actions) == "table", "Actions must be a table")
    local result = {}
    for _,a in ipairs(actions) do
        assert(type(a) == "table", "Each action must be a table")
        if a.action == 'fibaro' then
            REF = REF+1
            local ref = "fibaro_"..tostring(os.time()).."_"..tostring(REF)
            local timeout = a.timeout or 60  -- seconds
            local callback = a.callback
            if not callback then
                local deviceId,actionName,args = a.deviceId,a.actionName,a.args or {}
                assert(deviceId,"Fibaro action requires either a callback or deviceId and actionName")
                assert(actionName,"Fibaro action requires either a callback or deviceId and actionName")
                callback = function() fibaro.call(deviceId, actionName, table.unpack(args)) end
            end
            local act = {
                action = "http",
                label = a.label or "Fibaro HC3",
                url = "https://ntfy.sh/"..self.config.defaultResponseTopic,
                headers = a.headers or nil,
                method = "POST",
                body = json.encode({ref=ref}),
                clear = a.clear==true
            }
            refs[ref] = {action=callback,timer=setTimeout(function() refs[ref] = nil end, timeout*1000)} -- Expire
            result[#result+1] = act
        else result[#result+1] = a end
    end
    return result
end

function QuickApp:send(options)
    if not options or not options.message then
        self:error("Message is required")
        return false
    end
    
    local topic = options.topic or self.config.defaultTopic
    local url = self.config.server
    local headers = {
        ["Content-Type"] = "application/json"
    }
    
    -- Build JSON payload
    local payload = {
        topic = topic,
        message = options.message
    }
    
    -- Add optional fields
    if options.title then payload.title = options.title end
    if options.priority then payload.priority = options.priority end
    if options.tags then payload.tags = options.tags end
    if options.click then payload.click = options.click end
    if options.attach then payload.attach = options.attach end
    if options.filename then payload.filename = options.filename end
    if options.markdown then payload.markdown = options.markdown end
    if options.icon then payload.icon = options.icon end
    if options.delay then payload.delay = options.delay end
    if options.email then payload.email = options.email end
    if options.actions then payload.actions = fibaroActions(self,options.actions) end
    
    -- Add advanced options
    if options.cache then
        headers["X-Cache"] = options.cache
    end
    if options.firebase then
        headers["X-Firebase"] = options.firebase
    end
    
    -- Authentication
    if options.auth then
        if options.auth.token then
            headers["Authorization"] = "Bearer " .. options.auth.token
        elseif options.auth.username and options.auth.password then
            local auth = api.get("base64Encode", options.auth.username .. ":" .. options.auth.password)
            headers["Authorization"] = "Basic " .. auth
        end
    end
    
    local success = false
    
    http:request(url, {
        options = {
            method = "POST",
            headers = headers,
            data = json.encode(payload),
            timeout = self.config.timeout * 1000
        },
        success = function(response)
            if response.status >= 200 and response.status < 300 then
                self:debug("Notification sent successfully to topic:", topic)
                success = true
            else
                self:error("Failed to send notification. Status:", response.status, "Response:", response.data)
            end
        end,
        error = function(error)
            self:error("HTTP request failed:", error)
        end
    })
    
    return success
end

-- Convenience methods for common notification types
function QuickApp:sendSimple(topic, message, title)
    return self:send({
        topic = topic,
        message = message,
        title = title
    })
end

function QuickApp:sendAlert(message, title)
    return self:send({
        message = message,
        title = title or "Alert",
        priority = 4,
        tags = {"warning"}
    })
end

function QuickApp:sendCritical(message, title)
    return self:send({
        message = message,
        title = title or "Critical Alert", 
        priority = 5,
        tags = {"rotating_light", "skull"},
        email = "admin@example.com"  -- Configure your admin email
    })
end

function QuickApp:sendWithAction(message, title, actionLabel, actionUrl)
    return self:send({
        message = message,
        title = title,
        priority = 3,
        actions = {
            {
                action = "view",
                label = actionLabel,
                url = actionUrl,
                clear = false
            }
        }
    })
end

function QuickApp:test()
    --self:sendSimple(topic, "Hello from Fibaro HC3!", "Test Notification")

    self:send({
        topic = topic,
        message = "Security system armed. All sensors active.\n\nLast armed: " .. os.date(),
        title = "🏠 Security Status",
        priority = 3,
        tags = {"house", "lock", "checkmark"},
        markdown = true,
        icon = "https://play-lh.googleusercontent.com/Ha6TwnW_Zh2duKOOQooPaEJDHJag3AuBrIojd0W78XaQ2HBvOSEDSxN8AmGRCk3C76w=w128-h128",-- Ignored on iOS
        actions = {
            {
                action = "fibaro", 
                label = "Fibaro test",
                url = "https://myhome.example.com/api/disarm",
                callback = function() self:debug("Fibaro action executed") end
                --alt.
                -- deviceId = 123,
                -- actionName = "disarm", -- QuickApp method
                -- args = { param1, ...}
            }
        }
    })
end

function QuickApp:setupListener()
    local ws = net.WebSocketClientTls()
    local url = "wss://ntfy.sh/" .. self.config.defaultResponseTopic .. "/ws"
    ws:addEventListener("connected", function()
      print("[Listener] connected to", url)
    end)
    
    ws:addEventListener("dataReceived", function(data)
      -- Only close after receiving echo message (not welcome message)
      print("[Listener] Received from server:", data)
      local _,resp = pcall(json.decode, data)
      if resp and resp.event == "message" and resp.topic == self.config.defaultResponseTopic then
          local _,msg = pcall(json.decode, resp.message)
          local ref = msg.ref
          if not refs[ref] then
              self:debug("Ignoring expired or unknown action ref:", ref)
              return
          end
          clearTimeout(refs[ref].timer)
          local action = refs[ref].action
          refs[ref] = nil
          local stat,res = pcall(action)
          if not stat then
              self:error("Error executing Fibaro action for ref:", ref, "Error:", res)
          else
              self:debug("Fibaro action executed successfully for ref:", ref)
          end
      end
    end)
    
    ws:addEventListener("disconnected", function()
      print("[Client] Disconnected.")
      setTimeout(function() self:setupListener() end, 10*1000) -- Reconnect after 10s
    end)
    
    ws:addEventListener("error", function(err)
      print("[Client] Error:", err)
    end)
    
    ws:connect(url)
    
end