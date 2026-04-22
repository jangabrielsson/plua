---
name: quickapp-troubleshooting
description: Known gotchas, quirks, and behaviour differences when developing Fibaro HC3 QuickApps. Covers UI rendering issues (HTML in labels, new-views flag), property/variable edge cases, event handling surprises, and HC3 firmware behaviour differences. USE FOR: diagnosing unexpected QA behaviour on a real HC3, UI not rendering as expected, callbacks not firing, properties not updating.
---

# QuickApp Troubleshooting

Known issues and non-obvious behaviour specific to Fibaro HC3 QuickApps.

---

## UI Issues

### HTML in labels doesn't render — shows raw HTML instead

**Symptom:** `self:updateView("lbl", "text", "<b>Hello</b>")` shows the literal string `<b>Hello</b>` in the mobile app instead of rendered bold text.

**Cause:** The "new views" rendering mode does not support HTML in label text. When **Advanced → Use the new views in mobile application** is checked for the QA in the HC3 web UI, the mobile app renders labels as plain text.

**Fix:** In the HC3 web UI, open the QuickApp's settings → **Advanced** tab → uncheck **"Use the new views in mobile application"**. After unchecking, HTML tags in label text are rendered normally.

**Note:** The checkbox defaults to checked on newer firmware. If you are distributing a QA that uses HTML formatting, document this requirement for end users. Alternatively, avoid HTML and use plain Unicode characters for formatting (e.g. `●`, `▸`, `✔`).

### Supported HTML tags in label text

The HC3 mobile app only renders a limited subset of HTML. Unsupported tags are either stripped or shown as raw text.

| Tag / Attribute | Purpose |
|---|---|
| `<b>` | Bold text |
| `<i>` | Italic text |
| `<font color="...">` | Text colour (e.g. `red`, `green`, `#ff6600`) |
| `<font size="...">` | Text size |
| `<table>`, `<tr>`, `<td>` | Structured / tabular layouts |
| `<br>` | Line break |
| `<span>` | Generic inline styling |
| `<section align="...">` | Block-level alignment (e.g. `align="center"`) |
| `<code>`, `<tt>` | Monospaced / code text |

**Table attributes are not supported.** Do not use `border=`, `cellpadding=`, `style=`, or `bgcolor=` on `<table>`, `<tr>`, or `<td>`. To colour a cell's content, wrap the text in a `<font color="...">` tag inside the `<td>`.

```lua
-- Correct: colour applied via font tag inside the cell
"<table><tr><td><font color='green'>ON</font></td></tr></table>"

-- Wrong: attribute on td is ignored
"<table><tr><td style='color:green'>ON</td></tr></table>"
```

**Newlines inside HTML strings add blank lines.** The HC3 label renderer treats each `\n` in the HTML string as a visible blank line offset at the top of the table. Always concatenate HTML tags without newlines:

```lua
-- Correct: no newlines between tags
return table.concat(rows, "")

-- Wrong: each \n adds a blank line above the table
return table.concat(rows, "\n")
```

**Best practice:** Stick to these tags. Avoid `<div>`, `<p>`, `<ul>`, `<li>`, CSS classes, or JavaScript — they are not supported and will produce unexpected output.

---

## Header / Variable Declaration Issues

### `--%%var:` string values must use Lua string literal syntax

**Symptom:** `self:getVariable("city")` returns `""` even though `--%%var:city=London` is declared at the top of the file.

**Cause:** The value part of `--%%var:` is evaluated as a Lua expression. `London` is an identifier — it resolves to the global variable `London`, which is `nil`, so the variable ends up unset.

**Fix:** Wrap string values in Lua string quotes:
```lua
--%%var:city="London"       -- correct: Lua string literal
--%%var:apiKey="abc123"     -- correct
--%%var:pollInterval=300    -- correct: number literal, no quotes needed
--%%var:city=London         -- WRONG: evaluates global 'London' → nil
```

### Using `~/.plua/config.lua` to keep secrets out of source code

Because `--%%var:` values are evaluated as Lua expressions at startup, you can reference any global that is already defined — including values loaded from `~/.plua/config.lua`, which plua loads automatically before running any script.

This lets you store API tokens, IPs, and passwords in one place on the developer machine and reference them by name in the QA header, so secrets never appear in source code or version control:

```lua
-- ~/.plua/config.lua
return {
    Hue_user = "AqlHjZVly4IRgcDmzr5YfJh...",
    Hue_ip   = "192.168.50.56",
    myApiKey = "sk-proj-...",
}

-- In your QA file header (config fields are globals inside plua)
--%%var:HueUser=config.Hue_user
--%%var:HueIP=config.Hue_ip
--%%var:ApiKey=config.myApiKey
```

The child QA then reads them normally:
```lua
self.hueUser = self:getVariable("HueUser")
```

> **Note:** This trick only works when running under plua locally. When the QA is uploaded to a real HC3, the variables are baked in with the resolved values at upload time — so the HC3 device will have the correct values without needing access to `config.lua`.

---

## Property & Variable Issues

### `self:getVariable()` returns `""` for undeclared variables — never `nil`

`self:getVariable()` always returns `""` (empty string) when the variable is not declared — both on a real HC3 and in plua offline mode. It never returns `nil`.

**Common mistake:** checking `if val == nil` — this is always false.

**Correct guard:**
```lua
local val = self:getVariable("myVar")
if val == "" then val = "defaultValue" end
```

---

## Event Handling Issues

### UI callback not called after `updateView`

**Symptom:** Calling `self:updateView("switch1", "value", "true")` programmatically does not trigger the `onReleased`/`onChanged` handler.

**Cause:** `updateView` only updates the visual state of the element — it does not fire the associated Lua callback. The callback only fires when the user interacts with the element in the UI.

**Fix:** If you need to react to a programmatic value change, call your handler directly:
```lua
self:updateView("switch1", "value", "true")
self:mySwitch({ values = {"true"} })  -- call handler manually if needed
```

### `onChanged` for a slider receives value as a string, not a number

**Symptom:** Comparing `event.values[1] > 50` always fails or behaves oddly.

**Cause:** Slider callback values arrive as strings.

**Fix:**
```lua
function QuickApp:handleSlider(event)
    local val = tonumber(event.values[1])
end
```

---

## HC3 Firmware / Platform Differences

### `fibaro.call()` vs `api.post()` action timing

**Symptom:** `fibaro.call(id, "turnOn")` appears to have no effect when called immediately after creating a child device.

**Cause:** Device actions sent immediately after creation may be dropped if the device is not yet fully initialised on the HC3. This is a firmware timing issue.

**Fix:** Add a short delay:
```lua
setTimeout(function()
    fibaro.call(childId, "turnOn")
end, 500)
```

### `self:updateProperty()` takes one property at a time — no table form

`self:updateProperty` signature is `(propertyName, value)`. There is no batch/table form.

```lua
-- CORRECT — one call per property
self:updateProperty("value", temp)
self:updateProperty("unit", "C")

-- WRONG — does not work
self:updateProperty({ value = temp, unit = "C" })
```

---

### `self:updateProperty("value", ...)` does not persist across QA restart

**Symptom:** After restarting the QA the `value` property reverts to its previous state.

**Cause:** `updateProperty` writes to the HC3's in-memory device state. The HC3 persists this to disk periodically, but a restart before the write can result in the old value being loaded.

**Fix:** Use QuickApp variables (`self:setVariable`) for state you need to survive restarts:
```lua
self:setVariable("lastValue", tostring(val))
api.post("/plugins/updateProperty", { deviceId = self.id, propertyName = "value", value = val })
```

---

## plua-specific Differences from a Real HC3

| Behaviour | Real HC3 | plua emulation |
|-----------|----------|----------------|
| `self:getVariable()` on undeclared var | Returns `""` | Returns `""` — same behaviour |
| `fibaro.sleep()` | Supported | Not recommended; use `setTimeout` |
| Multi-file QA projects | Supported | Supported via `--%%file:` header |
| Push notifications | Sent to mobile app | Logged only, not sent |
| Alarm partition callbacks | Fire on real arm/disarm events | Simulated only |

---

## UTF-8 / Non-ASCII Character Issues

### `string.sub`, `#str`, `//` truncate inside multi-byte characters

**Symptom:** A QA that handles non-ASCII text (Polish `ł`, German `ü`, accented French, Cyrillic, emoji, etc.) works on a real HC3 but fails in plua with errors like:

```
invalid UTF-8 code
attempt to ... (a nil value)
[plua] WARNING: invalid UTF-8 in error message -- replaced N byte(s) with '?'.
First bad lead byte 0xC4 at position 4 (run length=1). Likely cause: a string was
sliced mid-codepoint (string.sub byte vs char).
```

**Cause:** Lua's `string` library is **byte-based**, not character-based:

| Operation | Counts | Behaviour on `"łabc"` (5 bytes: `C4 82 61 62 63`) |
|---|---|---|
| `#str` | bytes | `5` (not `4`) |
| `string.sub(str, 1, 2)` | bytes | `"\xC4\x82"` (a valid 2-byte char — fine here) |
| `string.sub(str, 1, 1)` | bytes | `"\xC4"` (half a character — **invalid UTF-8**) |
| `str // 3` (truncate operator) | bytes | `"\xC4\x82a"` (works because boundary is lucky) |
| `str // 1` | bytes | `"\xC4"` (broken) |

When the resulting half-character is later fed to `utf8.codes`, `utf8.len`, JSON encoders, or anything that validates UTF-8, you get a hard error. On a real HC3 the same code may *appear* to work because the firmware sometimes round-trips strings through normalisation that hides the corruption — but the bug is in the QA, not the platform.

**Fix:** Use the `utf8` library for character-aware operations, or build a codepoint array once and slice that:

```lua
-- Wrong: byte-based slice cuts ł in half
local prefix = string.sub(label, 1, n)

-- Right: utf8-aware slice
local function utf8sub(s, i, j)
  local n = utf8.len(s) or #s
  if i < 0 then i = math.max(n + i + 1, 1) end
  j = j or n
  if j < 0 then j = n + j + 1 end
  if i > j then return "" end
  local bi = utf8.offset(s, i)
  local bj = utf8.offset(s, j + 1)
  return s:sub(bi, bj and bj - 1 or -1)
end
local prefix = utf8sub(label, 1, n)

-- Right (alternative): work on a codepoint array
local chars = {}
for _, cp in utf8.codes(label) do
  chars[#chars + 1] = utf8.char(cp)
end
local prefix = table.concat(chars, "", 1, n)

-- Length in characters, not bytes:
local nchars = utf8.len(label)
```

**Tip:** When `utf8.codes(s)` itself throws on `s`, pass the lax flag to skip validation: `utf8.codes(s, true)`. This is fine for read-only iteration but does not fix the underlying truncation — track it down at the point where the string was sliced.

**plua diagnostic:** plua's `error()` shim sanitises invalid UTF-8 in error messages and prints a `[plua] WARNING: invalid UTF-8 in error message …` line that includes the position and lead byte of the first bad sequence. Use that hint to find the slice site in your code (often a `string.sub` call computing widths or wrapping lines).

### `%S` / `%s` truncates UTF-8 strings — `gmatch("%S+")` returns a half character

**Symptom:** Iterating words of a UTF-8 string with `gmatch("%S+")` (or splitting on `%s`) returns a token that ends with a stray lead byte and triggers `'utf-8' codec can't decode byte 0xc4 …: invalid continuation byte` when later printed, JSON-encoded, or sent to HC3.

```lua
local line = "TOPą"          -- bytes: 54 4F 50 C4 85
for word in line:gmatch("%S+") do
  print(word)                -- prints "TOP?" — token is 54 4F 50 C4 (broken)
end
```

**Cause:** Lua's `%s` character class is implemented via the C library's `isspace()`, which is **locale-dependent and byte-based**. On many systems (and on the HC3) `isspace(0x85)` returns true (byte `0x85` is the ISO-8859 NEL — Next Line — control character). The continuation byte of `ą` (`C4 85`) therefore *matches* `%s`, so `%S+` stops one byte too early and emits the orphan `C4`.

The same trap affects byte `0xA0` (NBSP), and also `%w`, `%a`, `%p` etc. — they all delegate to locale-dependent C predicates and can misclassify UTF-8 continuation bytes.

**Fix:** Replace locale classes with **explicit ASCII character sets** when tokenising UTF-8 text:

```lua
-- Wrong: %S can stop inside a multi-byte char
for word in line:gmatch("%S+") do ... end

-- Right: explicit ASCII whitespace set
for word in line:gmatch("[^ \t\r\n]+") do ... end

-- Splitting on whitespace
for part in line:gmatch("[^%s]+") do ... end       -- still uses %s, still broken
for part in line:gmatch("[^ \t\r\n\f\v]+") do ... end  -- safe
```

**Rule of thumb:** In any pattern that runs over text that may contain non-ASCII characters, prefer explicit byte sets (`[^ \t\r\n]`, `[%w_]` is usually OK because `0x80+` rarely matches `isalnum`, but verify) over the shortcut classes `%s`, `%S`, `%a`, `%A`, `%w`, `%W`, `%p`, `%P`. The `%d` / `%D` and `%x` / `%X` classes are safe — they are not locale-dependent.

**plua diagnostic:** because the broken token only shows the problem when it crosses a UTF-8 boundary (print, JSON, HTTP), the `[plua] WARNING: invalid UTF-8 …` line described above will fire. The "lead byte" it reports (e.g. `0xC4` for `ą`, `0xC5` for `ł`) plus the position is your fastest route to the offending pattern.

