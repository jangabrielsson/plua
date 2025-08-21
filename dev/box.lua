local glyphsfat = {
  corner1 = '┏',
  corner2 = '┓',
  corner3 = '┛', 
  corner4 = '┗',
  horizontal = '━',
  vertical = '┃',
  hordown = '┳',
  horup = '┻',
  verthor1 = '┣',
  verthor2 = '┫',
  cross = '╋',
  space = ' ',
}

local glyphsthin = {
  corner1 = '┌',
  corner2 = '┐',
  corner3 = '┘',
  corner4 = '└',
  horizontal = '─',
  vertical = '│',
  verthor1 = '├',
  verthor2 = '┤',
  hordown = '┬',
  horup = '┴',
  cross = '┼',
  space = ' ',
}

local glyphsdouble = {
  corner1 = '╔',
  corner2 = '╗',
  corner3 = '╝',
  corner4 = '╚',
  horizontal = '═',
  vertical = '║',
  verthor1 = '╠',
  verthor2 = '╣',
  hordown = '╦',
  horup = '╩',
  cross = '╬',
  space = ' ',
}

local glyphs = { single = glyphsthin, double = glyphsdouble, fat = glyphsfat }

local function prbuff()
  local self,b = { len = 0 },{}
  self.b = b
  function self:add(g) b[#b+1] = g self.len = self.len + 1 end
  function self:print(...) for _,e in ipairs({...}) do self.len=self.len+#e b[#b+1] = e end end
  function self:tostring(del) return table.concat(b, del or "") end
  return self
end

local data = {
  { "Alice", 30, "Engineer" },
  { "Bobol", 25, "Designer" },
  { "Charlie", 35, "Teacher" }
}

local function printTable(data,form)
  form = form or {}
  local cellFormat = form.cellformat or tostring
  local glyph = glyphs[form.glyph or 'single'] or glyphs.single
  local pad = (form.cellpad or 0)
  local headers = form.columns or {}
  local hasHeaders = #headers > 0 and headers[1].name ~= nil
  
  local widths = {}
  local tab = {}
  
  local function renderRow(r,cellFormat)
    local row = {}
    tab[#tab+1] = row
    for i,content in ipairs(r) do
      local cell = {}
      row[#row+1] = cell
      local str,formats = cellFormat(content)
      cell.content = str
      cell.width = #str
      cell.formats = formats or {}
      cell.pad = pad
      if headers[i] and headers[i].width then widths[i] = headers[i].width
      else
        widths[i] = math.max(widths[i] or 0, cell.width + pad)
      end
    end
  end

  if hasHeaders then
    local headerRender = function(cell) return cell.name end
    renderRow(headers, headerRender)
  end

  for _,r in ipairs(data) do renderRow(r,cellFormat) end

  for i,row in ipairs(tab) do
    for j,cell in ipairs(row) do
      local width = widths[j]
      local left,right = 0,0
      if cell.pad > 0 then
        left = math.floor(0.5 + cell.pad / 2)
        right = cell.pad // 2
      end
      if cell.width < width then
        local pad = width - cell.width
        local align = headers[j] and headers[j].align or "left"
        if align == 'center' then
          left = math.floor(pad / 2)
          right = pad - left
        elseif align == 'right' then
          left = pad - right
        else -- left or default
          right = pad - left
        end
        cell.content = (' '):rep(left) .. cell.content .. (' '):rep(right)
      elseif cell.width > width then
        cell.content = cell.content:sub(1, width - 1) .. "…"
      end
    end
  end
  
  local headerBorders = form.headersBorders or 'all'
  local bodyBorders = form.bodyBorders or 'all'

  local line = {} for _,w in ipairs(widths) do line[#line+1] = glyph.horizontal:rep(w) end
  local linesp = {} for _,w in ipairs(widths) do linesp[#linesp+1] = (' '):rep(w) end

  local frames = {
    all = { verticalEdge = 'vertical', verticalMiddle = 'vertical' },
    frame = { verticalEdge = 'vertical', verticalMiddle = 'space' },
    none = { verticalEdge = 'space', verticalMiddle = 'space' }
  }

  local firstLineBorder = hasHeaders and headerBorders or bodyBorders

  local verticalEdge1 = glyph[frames[firstLineBorder].verticalEdge]
  local verticalMiddle1 = glyph[frames[firstLineBorder].verticalMiddle]

  local verticalEdge = glyph[frames[bodyBorders].verticalEdge]
  local verticalMiddle = glyph[frames[bodyBorders].verticalMiddle]

  local middleLine = ""
  if bodyBorders == 'all' then
    middleLine = glyph.verthor1..table.concat(line,glyph.cross)..glyph.verthor2.."\n"
  elseif bodyBorders == 'frame' then
     middleLine = glyph.vertical..table.concat(linesp,' ')..glyph.vertical.."\n"
  else
    middleLine = ''
  end

  local n = #tab
  local lines = {}

  local cross = bodyBorders == 'all' and headerBorders == 'all' and glyph.cross or 
  bodyBorders == 'all' and glyph.hordown or headerBorders == 'all' and glyph.horup or
  bodyBorders == 'frame' and glyph.horizontal or headerBorders == 'frame' and glyph.horizontal or glyph.space

  for i,row in ipairs(tab) do
    local m = #row
    local p = prbuff()
    p:add(i==1 and verticalEdge1 or verticalEdge)
    for j,cell in ipairs(row) do
      p:add(cell.content)
      if j < m then p:add(i == 1 and verticalMiddle1 or verticalMiddle) end
    end
    p:add(i == 1 and verticalEdge1 or verticalEdge)
    p:add('\n')
    if i == 1 then
      if firstLineBorder == 'all' or firstLineBorder == 'frame' then
        local hordown = firstLineBorder == 'all' and glyph.hordown or glyph.horizontal
        local line = glyph.corner1..table.concat(line,hordown)..glyph.corner2.."\n"
        lines[#lines+1] = line
      end
    elseif i == 2 then
      local l = ""
      if bodyBorders == 'all' or bodyBorders == 'frame' then
        if headerBorders == 'none' then
          l = glyph.corner1..table.concat(line,cross)..glyph.corner2.."\n"
        else l = glyph.verthor1..table.concat(line,cross)..glyph.verthor2.."\n" end
      elseif headerBorders ~= 'none' then
        if headerBorders == 'all' then
          l = glyph.corner4..table.concat(line,glyph.horup)..glyph.corner3.."\n"
        else l = glyph.corner4..table.concat(line,glyph.horizontal)..glyph.corner3.."\n" end
      end
      lines[#lines+1] = l
    else
      lines[#lines+1] = middleLine
    end
    lines[#lines+1] = p:tostring()
  end
  if bodyBorders == 'all' or bodyBorders == 'frame' then
    local horup = bodyBorders == 'all' and glyph.horup or glyph.horizontal
    local line = glyph.corner4..table.concat(line,horup)..glyph.corner3
    lines[#lines+1] = line
  end

  print("\n"..table.concat(lines))
end

local tab = {
  data=data,
  cellpad=2,
  glyph = 'fat', -- 'single', 'double', 'fat'
  headersBorders = 'all', -- 'all', 'frame', 'none'
  bodyBorders = 'none', -- 'all', 'frame', 'none'
  columns = {
    {name="Name", width=10, pad=1, align='left'},
    {name="Age", width=5, pad=1, align='right'},
    {name="Occupation", width=15, pad=1, align='center'}
  },
}

-- Example usage:
form = {
  data=data,
  cellpad=2,
  glyph = 'fat', -- 'single', 'double', 'fat'
  headersBorders = 'all', -- 'all', 'frame', 'none'
  bodyBorders = 'all', -- 'all', 'frame', 'none'
  columns = {
    {name="Name", width=10, pad=1, align='left'},
    {name="Age", width=5, pad=1, align='right'},
    {name="Occupation", width=15, pad=1, align='center'}
  },
}

printTable({{'A','B','C'}},form)

local borders = { 'all', 'frame', 'none' }
for _,h in ipairs(borders) do
  for _,b in ipairs(borders) do
    form.headersBorders = h
    form.bodyBorders = b
    printTable(data,form)
  end
end
