# ntfy Publishing Options Documentation

## Overview
This document captures all available options for publishing messages to ntfy topics, based on the official ntfy documentation at https://docs.ntfy.sh/publish/

## Core Message Properties

### Required
- **topic** (string): Target topic name for the message

### Basic Message Content
- **message** (string): Main body of the notification (max 4,096 bytes)
- **title** (string): Message title (overrides default topic URL)

### Message Appearance
- **priority** (integer): Message urgency level
  - `1` = min (no vibration/sound, under fold)
  - `2` = low (no vibration/sound, in drawer)  
  - `3` = default (normal vibration/sound)
  - `4` = high (long vibration, pop-over)
  - `5` = max/urgent (very long vibration, pop-over)

- **tags** (array[string]): Tags that may convert to emojis or display as text
  - Examples: `["warning", "skull", "backup"]`
  - Emoji tags: `warning` → ⚠️, `skull` → 💀, `checkmark` → ✅

- **icon** (string): URL to notification icon (JPEG/PNG only)

## Formatting & Content
- **markdown** (boolean): Enable Markdown formatting in message body
- **template** (string): Template processing options
  - Pre-defined: `"github"`, `"grafana"`, `"alertmanager"`
  - Custom template name (from server template directory)
  - `"yes"` = enable inline Go templating

## Scheduling & Delivery
- **delay** (string): Schedule message for later delivery
  - Duration: `"30m"`, `"3h"`, `"2 days"`
  - Natural language: `"tomorrow, 10am"`, `"Tuesday, 7am"`
  - Unix timestamp: `"1639194738"`
  - Min delay: 10 seconds, Max delay: 3 days

## User Interactions

### Click Action
- **click** (string): URL to open when notification is tapped
  - Web URLs: `"https://example.com"`
  - Mail: `"mailto:user@example.com"`
  - Maps: `"geo:0,0?q=location"`
  - Deep links: `"ntfy://ntfy.sh/topic"`, `"twitter://user?screen_name=..."`

### Action Buttons (max 3)
Array of action objects with different types:

#### View Action
```json
{
  "action": "view",
  "label": "Open Dashboard", 
  "url": "https://example.com/dashboard",
  "clear": true
}
```

#### HTTP Action  
```json
{
  "action": "http",
  "label": "Trigger API",
  "url": "https://api.example.com/endpoint",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer token",
    "Content-Type": "application/json"
  },
  "body": "{\"action\": \"execute\"}",
  "clear": false
}
```

#### Broadcast Action (Android only)
```json
{
  "action": "broadcast", 
  "label": "Take Picture",
  "intent": "io.heckel.ntfy.USER_ACTION",
  "extras": {
    "cmd": "photo",
    "camera": "front"  
  },
  "clear": true
}
```

## Attachments
- **attach** (string): URL of external file to attach
- **filename** (string): Override filename for attachment display

## Notifications & Forwarding
- **email** (string): E-mail address to forward notification
  - Rate limited (16/hour by default on ntfy.sh: 5/day)
- **call** (string): Phone number for text-to-speech call
  - Format: `"+12223334444"` or `"yes"` for first verified number
  - Requires authentication and verified phone number

## Advanced Options
- **cache** ("yes"|"no"): Whether to cache message server-side (default: "yes")
- **firebase** ("yes"|"no"): Forward to Firebase Cloud Messaging (default: "yes")  
- **unifiedpush** ("0"|"1"): UnifiedPush mode (disables Firebase, enables base64 for binary)

## Authentication
When server has access control enabled:

### Basic Auth
```json
{
  "auth": {
    "username": "testuser",
    "password": "secret"
  }
}
```

### Token Auth  
```json
{
  "auth": {
    "token": "tk_AgQdq7mVBoFD37zQVN29RhuMzNIz2"
  }
}
```

## HTTP Headers vs JSON
All options can be sent either as:
1. **HTTP Headers**: `X-Title`, `X-Priority`, `X-Tags`, etc.
2. **JSON Body**: When POSTing to root URL (`https://ntfy.sh/`)
3. **Query Parameters**: URL-encoded in GET requests

### Header Examples
```bash
curl -H "X-Title: Alert" -H "X-Priority: 4" -d "Message" ntfy.sh/topic
```

### JSON Example  
```bash
curl ntfy.sh -d '{
  "topic": "alerts",
  "message": "Server down", 
  "title": "Critical Alert",
  "priority": 5,
  "tags": ["warning", "skull"],
  "email": "admin@example.com"
}'
```

### GET/Webhook Example
```bash
curl "ntfy.sh/topic/publish?message=Alert&priority=high&tags=warning"
```

## Rate Limits (ntfy.sh defaults)
- **Requests**: 60/visitor burst, then 1 per 5 seconds
- **Daily messages**: 250/day  
- **E-mails**: 5/day (16/hour burst, then 1/hour)
- **Attachment size**: 2 MB max, 20 MB total per visitor
- **Bandwidth**: 200 MB/day for attachments

## Complete Example
```json
{
  "topic": "home-security",
  "message": "Motion detected in living room. Camera footage attached.",
  "title": "🏠 Security Alert", 
  "priority": 4,
  "tags": ["warning", "camera", "motion"],
  "markdown": false,
  "icon": "https://myserver.com/security-icon.png",
  "click": "https://myserver.com/cameras/living-room",
  "attach": "https://myserver.com/footage/20231201-1430.mp4",
  "filename": "living-room-motion.mp4",
  "email": "security@example.com",
  "actions": [
    {
      "action": "view",
      "label": "View Live Feed", 
      "url": "https://myserver.com/live/living-room",
      "clear": false
    },
    {
      "action": "http",
      "label": "Disable Alarm",
      "url": "https://myserver.com/api/alarm/disable", 
      "method": "POST",
      "headers": {
        "Authorization": "Bearer security-token"
      },
      "clear": true
    }
  ],
  "cache": "yes",
  "firebase": "yes"
}
```

## Template Variables (when using templating)
When `template` is set, you can use Go template syntax in `message` and `title`:
- Variables: `{{.field}}`  
- Conditionals: `{{if eq .status "firing"}}...{{else}}...{{end}}`
- Loops: `{{range .items}}...{{end}}`
- Functions: String, math, date, encoding functions available

Example with GitHub webhook:
```json
{
  "topic": "github-notifications",
  "template": "github",
  "message": "{{.pull_request.title}}",
  "title": "[{{.repository.name}}] {{.action}} PR"
}
```