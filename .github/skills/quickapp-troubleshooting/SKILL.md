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
