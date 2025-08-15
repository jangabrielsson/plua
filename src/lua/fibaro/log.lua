-- @module hc3emu2.log
---@description Logging system for HC3Emu2
---@author Jan Gabrielsson
---@license MIT
---
---This module provides logging functionality:
---- Colored console output
---- HTML to ANSI color conversion
---- Log level filtering
---- Timestamp formatting
---- Table formatting
---- Dark/light theme support
---
---@usage
---```lua
---local log = require("hc3emu2.log")
---log.init() -- Initialize with default colors
---log.LOGGER.DEBUG("TAG", "Debug message")
---log.LOGGER.ERROR("TAG", "Error message")
---log.setDark(true) -- Switch to dark theme
---```
local Emu = ...
local log
local fmt = string.format
local print = print

local function init(colors)
  colors = colors or {}
  local ANSICOLORMAP = {
    -- These work both on Zerobrane Studio console and VSCode terminal
    black="\027[30m",brown="\027[31m",green="\027[32m",orange="\027[33m",navy="\027[34m",
    purple="\027[35m",teal="\027[36m",grey="\027[37m", gray="\027[37m",red="\027[31;1m",
    tomato="\027[31;1m",neon="\027[32;1m",yellow="\027[33;1m",blue="\027[34;1m",magenta="\027[35;1m",
    cyan="\027[36;1m",white="\027[37;1m",darkgrey="\027[30;1m",
    reset = "\027[0m", -- Reset color
  }
  
  local COLORMAP = ANSICOLORMAP
  
  if not Emu.config.environment == 'zerobrane' then 
    ANSICOLORMAP.orange=nil 
    ANSICOLORMAP = setmetatable(ANSICOLORMAP, {__index=colors}) 
  end -- Set metatable to allow adding extra colors
  
  local function html2ansiColor(str, dfltColor) -- Allows for nested font tags and resets color to dfltColor
    dfltColor = COLORMAP[dfltColor]
    local st, p = { dfltColor }, 1
    return dfltColor..str:gsub("(</?font.->)", function(s)
      if s == "</font>" then
        p = p - 1; return st[p]
      else
        local color = s:match("color=\"?([#%w]+)\"?") or s:match("color='([#%w]+)'")
        if color then color = color:lower() end
        color = COLORMAP[color] or dfltColor
        p = p + 1; st[p] = color
        return color
      end
    end)..ANSICOLORMAP.reset
  end
  
  local function color(str)
    return str:gsub("(%%%b{})", function(s)
      return COLORMAP[s:sub(3,-2):match("(%w+)")] or ""
    end)
  end
  
  local logConfigDark = {
    timestampPattern = "[%d.%m.%Y][%H:%M:%S]",
    defaultColor = 'gray', -- Default color for log messages
    logPatterns = {
      DEBUG =   color("%{gray}%date[%{green }DEBUG  %{gray}][%tag]: %message%{reset}"),
      TRACE =   color("%{gray}%date[%{cyan  }TRACE  %{gray}][%tag]: %message%{reset}"),
      WARNING = color("%{gray}%date[%{orange}WARNING%{gray}][%tag]: %message%{reset}"),
      ERROR =   color("%{gray}%date[%{red   }ERROR  %{gray}][%tag]: %message%{reset}"),
      INFO =     color("%{gray}%date[%{yellow}INFO   %{gray}][%tag]: %message%{reset}"),
    }
  }
  
  local logConfigLight = {
    timestampPattern = "[%d.%m.%Y][%H:%M:%S]",
    defaultColor = 'black', -- Default color for log messages
    logPatterns = {
      DEBUG =   color("%{black}%date[%{green }DEBUG  %{black}][%tag]: %message%{reset}"),
      TRACE =   color("%{black}%date[%{blue  }TRACE  %{black}][%tag]: %message%{reset}"),
      WARNING = color("%{black}%date[%{orange}WARNING%{black}][%tag]: %message%{reset}"),
      ERROR =   color("%{black}%date[%{red   }ERROR  %{black}][%tag]: %message%{reset}"),
      INFO =     color("%{black}%date[%{navy  }INFO   %{black}][%tag]: %message%{reset}"),
    }
  }
  
  local logConfig = logConfigDark -- Default log config
  local function setDark(dark)
    if dark then logConfig = logConfigDark
    else logConfig = logConfigLight end
  end
  
  local transformTable
  local function convertHtml(str, dfltColor)
    str = str:gsub("<table (.-)>(.-)</table>",transformTable) -- Remove table tags
    str = str:gsub("(&nbsp;)", " ")  -- transform html space
    str = str:gsub("</?br>", "\n")    -- transform break line
    str = html2ansiColor(str, dfltColor) -- Convert html colors to ansi colors
    return str
  end
  
  local logFilter = {}
  
  local function LOG(typ, tag, str, time)
    if Emu.config.condensedLog then
      logConfig.timestampPattern = "[%d.%m][%H:%M:%S]"
      tag = #tag > 8 and tag:sub(-7) or tag
    end
    str = tostring(str)
    time = time or Emu.lib.userTime and Emu.lib.userTime() or os.time()
    local timeStr = os.date(logConfig.timestampPattern, time)
    tag = tag:upper()
    local pattern = logConfig.logPatterns[typ:upper()] or logConfig.logPatterns.DEBUG
    str = convertHtml(str,logConfig.defaultColor or "black")
    local outstr = pattern:gsub("%%date", timeStr):gsub("%%tag", tag)
    local i,j = outstr:find("%%message") -- str can contain % characters, so we need to find %%message
    if i then outstr = outstr:sub(1,i-1)..str..outstr:sub(j+1) end
    if Emu.config.nocolor then outstr = outstr:gsub("\027%[.-m","") end -- and remove colors if not wanted
    if next(logFilter) then -- Filter log messages
      for str,bol in pairs(logFilter) do if outstr:find(str) then return end end
    end
    print(outstr)
  end
  
  local LOGGER = {
    DEBUG = function(tag, str, time) LOG("DEBUG", tag, str, time) end,
    TRACE = function(tag, str, time) LOG("TRACE", tag, str, time) end,
    WARNING = function(tag, str, time) LOG("WARNING", tag, str, time) end,
    ERROR = function(tag, str, time) LOG("ERROR", tag, str, time) end,
    INFO = function(tag, str, time) LOG("INFO", tag, str, time) end
  }
  
  local function debugOutput(tag, str, typ, time) LOGGER[typ:upper()](tag, str, time) end
  
  local function colorStr(color,str) 
    if log.logInColor then
      return fmt("%s%s%s",COLORMAP[color],str,ANSICOLORMAP.reset) 
    else return str end
  end
  
  function transformTable(pref,str)
    local buff = {}
    local function out(b,str) table.insert(b,str) end
    str:gsub("<tr.->(.-)</tr>",function(row)
      local rowbuff = {}
      row:gsub("<td.->(.-)</td>",function(cell) 
        out(rowbuff,cell)
      end)
      out(buff,table.concat(rowbuff,"  "))
    end)
    return table.concat(buff,"\n")
  end
  

  log = {
    colors = { COLORMAP = COLORMAP },
    setDark = setDark,
    LOGGER = LOGGER,
    debugOutput = debugOutput,
    colorStr = colorStr,
    html2ansiColor = html2ansiColor,
    logInColor = true,
    logFilter = logFilter
  }
end

local extraColors = {
  aqua = "\027[38;5;14m",
  aquamarine1 = "\027[38;5;122m",
  aquamarine3 = "\027[38;5;79m",
  black = "\027[38;5;0m",
  blue = "\027[38;5;12m",
  blue1 = "\027[38;5;21m",
  blue3 = "\027[38;5;20m",
  blueviolet = "\027[38;5;57m",
  cadetblue = "\027[38;5;73m",
  chartreuse1 = "\027[38;5;118m",
  chartreuse2 = "\027[38;5;112m",
  chartreuse3 = "\027[38;5;76m",
  chartreuse4 = "\027[38;5;64m",
  cornflowerblue = "\027[38;5;69m",
  cornsilk1 = "\027[38;5;230m",
  cyan1 = "\027[38;5;51m",
  cyan2 = "\027[38;5;50m",
  cyan3 = "\027[38;5;43m",
  darkblue = "\027[38;5;18m",
  darkcyan = "\027[38;5;36m",
  darkgoldenrod = "\027[38;5;136m",
  darkgreen = "\027[38;5;22m",
  darkkhaki = "\027[38;5;143m",
  darkmagenta = "\027[38;5;91m",
  darkolivegreen1 = "\027[38;5;192m",
  darkolivegreen2 = "\027[38;5;155m",
  darkolivegreen3 = "\027[38;5;149m",
  darkorange = "\027[38;5;208m",
  darkorange3 = "\027[38;5;166m",
  darkred = "\027[38;5;88m",
  --darkseagreen = "\027[38;5;108m",
  darkseagreen1 = "\027[38;5;193m",
  darkseagreen2 = "\027[38;5;157m",
  darkseagreen3 = "\027[38;5;150m",
  darkseagreen4 = "\027[38;5;71m",
  darkslategray1 = "\027[38;5;123m",
  darkslategray2 = "\027[38;5;87m",
  darkslategray3 = "\027[38;5;116m",
  darkturquoise = "\027[38;5;44m",
  darkviolet = "\027[38;5;128m",
  deeppink1 = "\027[38;5;199m",
  deeppink2 = "\027[38;5;197m",
  deeppink3 = "\027[38;5;162m",
  deeppink4 = "\027[38;5;125m",
  deepskyblue1 = "\027[38;5;39m",
  deepskyblue2 = "\027[38;5;38m",
  deepskyblue3 = "\027[38;5;32m",
  deepskyblue4 = "\027[38;5;25m",
  dodgerblue1 = "\027[38;5;33m",
  dodgerblue2 = "\027[38;5;27m",
  dodgerblue3 = "\027[38;5;26m",
  fuchsia = "\027[38;5;13m",
  gold1 = "\027[38;5;220m",
  gold3 = "\027[38;5;178m",
  green = "\027[38;5;2m",
  green1 = "\027[38;5;46m",
  green3 = "\027[38;5;40m",
  green4 = "\027[38;5;28m",
  greenyellow = "\027[38;5;154m",
  grey = "\027[38;5;8m",
  grey0 = "\027[38;5;16m",
  grey100 = "\027[38;5;231m",
  grey11 = "\027[38;5;234m",
  grey15 = "\027[38;5;235m",
  grey19 = "\027[38;5;236m",
  grey23 = "\027[38;5;237m",
  grey27 = "\027[38;5;238m",
  grey3 = "\027[38;5;232m",
  grey30 = "\027[38;5;239m",
  grey35 = "\027[38;5;240m",
  grey37 = "\027[38;5;59m",
  grey39 = "\027[38;5;241m",
  grey42 = "\027[38;5;242m",
  grey46 = "\027[38;5;243m",
  grey50 = "\027[38;5;244m",
  grey53 = "\027[38;5;102m",
  grey54 = "\027[38;5;245m",
  grey58 = "\027[38;5;246m",
  grey62 = "\027[38;5;247m",
  grey63 = "\027[38;5;139m",
  grey66 = "\027[38;5;248m",
  grey69 = "\027[38;5;145m",
  grey7 = "\027[38;5;233m",
  grey70 = "\027[38;5;249m",
  grey74 = "\027[38;5;250m",
  grey78 = "\027[38;5;251m",
  grey82 = "\027[38;5;252m",
  grey84 = "\027[38;5;188m",
  grey85 = "\027[38;5;253m",
  grey89 = "\027[38;5;254m",
  grey93 = "\027[38;5;255m",
  honeydew2 = "\027[38;5;194m",
  hotpink = "\027[38;5;206m",
  hotpink2 = "\027[38;5;169m",
  hotpink3 = "\027[38;5;168m",
  indianred = "\027[38;5;167m",
  indianred1 = "\027[38;5;204m",
  khaki1 = "\027[38;5;228m",
  khaki3 = "\027[38;5;185m",
  coral = "\027[38;5;210m",
  lightcoral = "\027[38;5;210m",
  lightcyan1 = "\027[38;5;195m",
  lightcyan3 = "\027[38;5;152m",
  lightgoldenrod1 = "\027[38;5;227m",
  lightgoldenrod2 = "\027[38;5;222m",
  lightgoldenrod3 = "\027[38;5;179m",
  lightgreen = "\027[38;5;120m",
  lightpink1 = "\027[38;5;217m",
  lightpink3 = "\027[38;5;174m",
  lightpink4 = "\027[38;5;95m",
  lightsalmon1 = "\027[38;5;216m",
  lightsalmon3 = "\027[38;5;173m",
  lightseagreen = "\027[38;5;37m",
  lightskyblue1 = "\027[38;5;153m",
  lightskyblue3 = "\027[38;5;110m",
  lightslateblue = "\027[38;5;105m",
  lightslategrey = "\027[38;5;103m",
  lightsteelblue = "\027[38;5;147m",
  lightblue = "\027[38;5;147m",
  lightsteelblue1 = "\027[38;5;189m",
  lightsteelblue3 = "\027[38;5;146m",
  lightyellow3 = "\027[38;5;187m",
  lime = "\027[38;5;10m",
  magenta = "\027[38;5;201m",
  magenta2 = "\027[38;5;200m",
  magenta3 = "\027[38;5;164m",
  maroon = "\027[38;5;1m",
  mediumorchid = "\027[38;5;134m",
  mediumorchid1 = "\027[38;5;207m",
  mediumorchid3 = "\027[38;5;133m",
  mediumpurple = "\027[38;5;104m",
  mediumpurple1 = "\027[38;5;141m",
  mediumpurple2 = "\027[38;5;140m",
  mediumpurple3 = "\027[38;5;98m",
  mediumpurple4 = "\027[38;5;60m",
  mediumspringgreen = "\027[38;5;49m",
  mediumturquoise = "\027[38;5;80m",
  mediumvioletred = "\027[38;5;126m",
  mistyrose1 = "\027[38;5;224m",
  mistyrose3 = "\027[38;5;181m",
  navajowhite1 = "\027[38;5;223m",
  navajowhite3 = "\027[38;5;144m",
  navy = "\027[38;5;4m",
  navyblue = "\027[38;5;17m",
  olive = "\027[38;5;3m",
  orange = "\027[38;5;214m",
  orange3 = "\027[38;5;172m",
  orange4 = "\027[38;5;94m",
  orangered1 = "\027[38;5;202m",
  orchid = "\027[38;5;170m",
  orchid1 = "\027[38;5;213m",
  orchid2 = "\027[38;5;212m",
  palegreen1 = "\027[38;5;156m",
  palegreen3 = "\027[38;5;114m",
  paleturquoise1 = "\027[38;5;159m",
  paleturquoise4 = "\027[38;5;66m",
  palevioletred1 = "\027[38;5;211m",
  pink = "\027[38;5;218m",
  pink3 = "\027[38;5;175m",
  plum1 = "\027[38;5;219m",
  plum2 = "\027[38;5;183m",
  plum3 = "\027[38;5;176m",
  plum4 = "\027[38;5;96m",
  purple0 = "\027[38;5;93m",
  purple3 = "\027[38;5;56m",
  purple4 = "\027[38;5;55m",
  purple5 = "\027[38;5;129m",
  purples = "\027[38;5;5m",
  red = "\027[38;5;9m",
  red1 = "\027[38;5;196m",
  red3 = "\027[38;5;160m",
  rosybrown = "\027[38;5;138m",
  royalblue1 = "\027[38;5;63m",
  salmon1 = "\027[38;5;209m",
  sandybrown = "\027[38;5;215m",
  seagreen1 = "\027[38;5;85m",
  seagreen2 = "\027[38;5;83m",
  seagreen3 = "\027[38;5;78m",
  silver = "\027[38;5;7m",
  skyblue = "\027[38;5;117m",
  skyblue2 = "\027[38;5;111m",
  skyblue3 = "\027[38;5;74m",
  slateblue1 = "\027[38;5;99m",
  slateblue3 = "\027[38;5;62m",
  springgreen1 = "\027[38;5;48m",
  springgreen2 = "\027[38;5;47m",
  springgreen3 = "\027[38;5;41m",
  springgreen4 = "\027[38;5;29m",
  steelblue = "\027[38;5;67m",
  steelblue1 = "\027[38;5;81m",
  steelblue3 = "\027[38;5;68m",
  tan = "\027[38;5;180m",
  teal = "\027[38;5;6m",
  thistle1 = "\027[38;5;225m",
  thistle3 = "\027[38;5;182m",
  turquoise2 = "\027[38;5;45m",
  turquoise4 = "\027[38;5;30m",
  violet = "\027[38;5;177m",
  wheat1 = "\027[38;5;229m",
  wheat4 = "\027[38;5;101m",
  white = "\027[38;5;15m",
  yellow = "\027[38;5;11m",
  yellow1 = "\027[38;5;226m",
  yellow2 = "\027[38;5;190m",
  yellow3 = "\027[38;5;184m",
  yellow4 = "\027[38;5;106m",
  floralwhite = "\027[38;5;230m", 
  darkseagreen = "\027[38;5;108m", 
  darkslateblue = "\027[38;5;60m", 
  gainsboro = "\027[38;5;188m", 
  slategray = "\027[38;5;102m", 
  darkslategray = "\027[38;5;58m", 
  lemonchiffon = "\027[38;5;187m", 
  khaki = "\027[38;5;143m", 
  lightgoldenrodyellow = "\027[38;5;186m", 
  lavenderblush = "\027[38;5;225m", 
  lavender = "\027[38;5;189m", 
  slateblue = "\027[38;5;62m", 
  deepskyblue = "\027[38;5;39m",
}
extraColors.brown = extraColors.sandybrown
extraColors.lightred = extraColors.red
extraColors.salmon = extraColors.lightpink1
extraColors.buttermilk = extraColors.yellow

init(extraColors)
log.colors.EXTRA = extraColors -- Expose extra colors for use in other modules
return log