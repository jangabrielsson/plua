---
name: hc3-write-safety
description: Non-obvious HC3 write-path hazards learned from direct experimentation. Covers silent data loss on PUT /api/devices/{id} and PUT /api/panels/climate/{id} (top-level fields merge but array-valued properties like quickAppVariables / parameters / schedules fully replace, so partial submissions wipe siblings); silent value coercion on the setVariable action endpoint (numeric-looking strings become numbers and break the HC3 UI edit affordance); silent enum coercion on climate zone mode (invalid values become "Manual"); cache-only writes on Z-wave configuration parameters (PUT updates HC3's stored copy without transmitting to the device, producing a misleading success); silent action failures via HC3's HTTP-202-with-jsonrpc-error-envelope shape; and the read-modify-write + post-write-verify pattern that defends against most of them. USE FOR: writing to HC3 state via REST from QA code or external callers, or when deciding whether to use a direct api.put() / api.post() call vs a guarded helper.
paths: "**/*.lua"
---

# HC3 Write-Path Safety

HC3's REST API has several write behaviours that are not in the Swagger
documentation and will silently corrupt data, fail to take effect, or
report success on a no-op if the caller doesn't know about them. Every
item below was confirmed by direct experimentation, not by reading
docs. Most were discovered while hardening the HC3_mcp server (see
`northernRough/HC3_mcp`).

If you're writing from a QuickApp via `api.put` / `api.post`, or from
an external caller, the patterns and gotchas below apply directly.
Where the HC3_mcp tools (`modify_device`, `update_climate_zone`,
`update_location_settings`, `set_quickapp_variable`, `modify_scene`)
are available, they wrap these hazards with read-modify-write and
post-write verification — direct `api.put()` / `api.post()` calls skip
the guards.

---

## 1. `PUT /api/devices/{id}` — top-level merges, nested `properties.*` arrays fully replace

Top-level fields (`name`, `roomID`, `enabled`, `visible`, etc.) are
merged: submitting one doesn't affect the others. So this is safe:

```lua
api.put("/devices/42", { name = "Living Room Light", roomID = 3 })
```

**But** array-valued fields under `properties.*` are replaced wholesale:

- `properties.quickAppVariables`
- `properties.categories`
- `properties.uiCallbacks`

Submitting a partial array destroys every entry not in the submission.
This PUT looks like "update one variable" but wipes every other
quickAppVariable on the device:

```lua
-- DANGEROUS — wipes all other quickAppVariables
api.put("/devices/42", {
  properties = { quickAppVariables = { { name = "myVar", value = "new" } } }
})
```

**Safe pattern:** read the full array, modify in place, write back the
full array. Or use `set_quickapp_variable` / `modify_device` from the
HC3_mcp server, which do this for you.

```lua
local dev = api.get("/devices/42")
local vars = dev.properties.quickAppVariables
for _, v in ipairs(vars) do
  if v.name == "myVar" then v.value = "new" break end
end
api.put("/devices/42", { properties = { quickAppVariables = vars } })
```

`properties.parameters`, `properties.associations` and
`properties.multichannelAssociations` are array-valued *and* have their
own additional silent-write trap — see section 7.

## 2. `PUT /api/panels/climate/{id}` — same shape as devices

Climate zones have the same top-level-merge / nested-property-replace
semantics. Because climate zones hold weekly schedules (`monday`,
`tuesday`, ... as nested objects each containing `morning`/`day`/
`evening`/`night`), a naive partial write can wipe the entire weekly
schedule.

Safe pattern: read the full zone, deep-merge at the object level
(preserving sibling schedule entries), then PUT the merged object.
`update_climate_zone` in the HC3_mcp server does this.

Top-level fields (`name`, `active`, `mode`) merge cleanly.

## 3. `PUT /api/panels/location/{id}` — flat, top-level merge

Location objects are flat (no nested `properties` wrapper). Top-level
fields merge, so partial writes are safe here. Read-only fields on the
location record: `id`, `created`, `modified` — HC3 rejects or ignores
attempts to change them. The `update_location_settings` MCP tool rejects
these at the tool boundary.

## 4. HC3 silently coerces invalid enum values

Submitting an invalid string for a typed enum does not error. HC3
silently substitutes a default.

Confirmed example: climate zone `topLevel.mode`:

```lua
-- submits "NonsenseMode", HC3 silently stores "Manual"
api.put("/panels/climate/7", { mode = "NonsenseMode" })
```

**Implication:** always refetch and verify after a write if the value is
in a constrained domain. Don't trust HC3's 200 OK.

A side-effect to know: flipping a climate zone from `Schedule` to
`Manual` (including via silent coercion) sets `properties.handTimestamp`
to a non-zero value. To return the zone to `Schedule`, write
`properties.handTimestamp = 0` — do not try to write `mode = "Schedule"`
at top level, which HC3 rejects.

## 5. `POST /api/devices/{id}/action/setVariable` — silent number coercion

Calling `setVariable` via the action endpoint (e.g. via `fibaro.call`
or `control_device` in the MCP) coerces numeric-looking string values
(`"3.0"`, `"12"`) to numbers while leaving the variable's declared
`type: "string"` metadata untouched. The stored `value` becomes
`3` (number) while the UI still thinks this is a string-typed row.

Consequence: **the HC3 web UI edit affordance disappears for that row**
and stays gone until the variable is deleted and recreated via the UI.
The variable is still readable from QA code, but has become unmanageable
from the UI.

**Defensive patterns:**

- From inside QA code: always wrap with `tostring()` if the variable is
  declared `string` and the value might look numeric:
  ```lua
  self:setVariable("allowableSpread", tostring(val))
  ```
  This is why `quickapp-patterns` examples use `tostring()` — it's
  defending against this coercion, not just type hygiene.
- From outside HC3 (MCP, external REST): use `set_quickapp_variable`
  from the HC3_mcp server, which reads the declared type and coerces
  correctly, or write directly via `PUT /api/devices/{id}` with the
  full `properties.quickAppVariables` array (see section 1).
- Never use `control_device` with `action: "setVariable"` — the HC3_mcp
  fork hard-rejects this call at the tool boundary for exactly this
  reason.

## 6. `POST /api/plugins/updateProperty` — undocumented, avoid

This endpoint does not appear in HC3's Swagger documentation. Its
behaviour is not guaranteed stable across firmware versions. The
`hc3-rest-api` skill lists it for completeness but do not rely on it.

Use `PUT /api/devices/{id}` for property writes — it's the documented
endpoint and goes through the same merge/replace semantics documented
in section 1. `modify_device` in HC3_mcp wraps the documented path.

## 7. Z-wave mesh-config writes are cache-only — do not use REST

`PUT /api/devices/{id}` with `{ properties = { parameters = [...] } }`
updates HC3's stored copy of a Z-wave device's configuration
parameters, **but does not transmit the new value to the physical
device over the mesh**. The post-write verify will report success
(HC3's cached array matches what you submitted) and the HC3 web UI
will display the new value. The physical device behaves on the old.

**Confirmed live on firmware 5.202.54** against a Zooz ZEN52 double
relay. PUT-set parameter 2 (LED indicator mode) from default `1` to
`0`. HC3 stored the new value, web UI showed `0`, but the unit's
indicator LED continued lighting whenever a load was on (the `1`
behaviour). The cached entry stored only `{id, size, value}` — no
`lastReportedValue` or `lastSetValue` field — consistent with "never
transmitted, nothing to track".

Compounding the trap: the dedicated Z-wave action endpoints that
*should* transmit are not implemented on this firmware:

```lua
-- All return HTTP 202 with body
-- {"jsonrpc":"2.0","error":{"code":-3,"message":"not implemented"},...}
api.post("/devices/4753/action/getParameter", { args = { 2 } })
api.post("/devices/4753/action/setParameter", { args = { 2, 0, 1 } })
api.post("/devices/4753/action/reconfigure",  { args = {} })
```

**Verdict on firmware 5.x:** there is no working REST path to set
Z-wave configuration parameters. Set them via the HC3 web UI (which
uses a native protocol), or by re-including the device with the
desired parameters preset.

The same precautionary reasoning extends to
`properties.associations` and `properties.multichannelAssociations`
— they are structurally the same "write-to-HC3, expected-to-push-
downstream" pattern as `parameters`, and HC3's broader Z-wave action
surface is broken on this firmware. Treat as cache-only until proven
otherwise. The HC3_mcp `modify_device` tool hard-rejects all three
fields at the tool boundary.

## 8. Action POSTs can fail silently — check the response body

HC3 action endpoints (POST `/api/devices/{id}/action/{name}`,
`/api/scenes/{id}/action/{verb}`, `/api/alarms/v1/partitions/{id}/actions/...`,
`/api/panels/sprinklers/{id}/actions/...`, etc.) return HTTP 202
**Accepted** even when the action fails. The failure shape is a
JSON-RPC envelope in the response body:

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "error": { "code": -3, "message": "not implemented" },
  "endTimestampMillis": ...,
  "startTimestampMillis": ...
}
```

`api.post` and `fibaro.call` will both happily ignore that envelope
and return as if the call succeeded. A successful action returns the
same envelope shape with `error: null`.

**Defensive pattern:**

```lua
local res = api.post("/devices/4753/action/setParameter", { args = { 2, 0, 1 } })
if type(res) == "table" and res.error ~= nil then
  error("HC3 action failed: " .. tostring(res.error.code) .. " " ..
        tostring(res.error.message))
end
```

The HC3_mcp server's central HTTP layer applies this check on every
response since `bcc643f`, so action failures surface as real errors
rather than silent successes.

## 9. The safe pattern, summarised

For any non-trivial write to HC3:

1. **Fetch current state** — `api.get("/devices/42")` or equivalent.
2. **Modify in memory** — merge at the object level, preserving
   sibling keys; for arrays, modify the full array in place.
3. **PUT the full merged object.**
4. **Refetch and verify** — compare submitted keys against stored
   values. Throw if they don't match.
5. **For action POSTs**, also inspect the response body for a
   non-null JSON-RPC `error` (section 8).

All the HC3_mcp write tools (`modify_device`, `update_climate_zone`,
`update_location_settings`, `modify_scene`, `set_quickapp_variable`) do
this for you. Prefer them over raw `api.put` / `api.post` wherever the
MCP is available.
