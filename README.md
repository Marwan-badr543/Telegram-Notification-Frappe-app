# Notification Management

Manage all Telegram notifications from one place in Frappe. Send real-time alerts to Telegram when documents are created, updated, submitted, cancelled, or deleted — with dynamic message templates, conditional filters, and inline keyboard actions.

## Features

- **Real-time alerts** — Trigger Telegram notifications on any DocType event (After Insert, On Update, On Submit, On Cancel, On Trash)
- **Dynamic message templates** — Compose messages using Jinja2 with access to all document fields (`{{ doc.name }}`, `{{ doc.grand_total }}`, etc.)
- **Conditional filtering** — Write single-line Python expressions to control when alerts fire (e.g., `doc.grand_total > 1000`)
- **Inline keyboard actions** — Add Submit/Cancel buttons so you can approve or reject documents directly from Telegram
- **Auto-registration** — Users who message the bot are automatically registered — no need to manually collect Chat IDs
- **Single bot token** — Configure one Telegram Bot Token for the entire site

## Installation

### Prerequisites

- A Frappe Bench environment (v15+)
- A Telegram account

### Steps

```bash
# Navigate to your bench directory
cd ~/frappe/bench

# Get the app
bench get-app https://github.com/YOUR_USERNAME/notification_management

# Install the app on your site
bench --site your-site.com install-app notification_management
```

## Configuration

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the prompts to create a new bot
3. BotFather will give you an **HTTP API token** — save it, you'll need it below

### 2. Set the Bot Token in Frappe

1. Go to **Telegram Bot Token** in the Awesome Bar (it's a Single DocType)
2. Paste your bot token (e.g., `8758948322:AAEUsvz91GlcXCTypw7zTjy72KZ8fM9ZnJI`)
3. Save

### 3. Set the Webhook

The Telegram Bot needs a webhook URL so it can forward user interactions (like button clicks) back to your Frappe site.

Replace `<YOUR_BOT_TOKEN>` and `<YOUR_SITE_URL>` and open this URL in your browser (or use `curl`):

```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_SITE_URL>/api/method/notification_management.api.webhook.trigger_webhook
```

**Example with ngrok (local development):**

```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR_NGROK_SUBDOMAIN>.ngrok-free.app/api/method/notification_management.api.webhook.trigger_webhook
```

You should see a JSON response like:
```json
{"ok": true, "result": true, "description": "Webhook was set"}
```

### 4. Create Alert Rules

Go to **Telegram Alert Setting** and create a new record:

| Field | Description |
|---|---|
| **Enabled** | Check to activate the alert |
| **Username** | Telegram username of the recipient (e.g., `@johndoe`) — leave empty if using Chat ID |
| **Chat ID** | Telegram Chat ID (leave empty and just enter Username — the system will auto-fill it when the user messages the bot) |
| **Tracked Doctype** | The DocType you want to watch (e.g., `Sales Invoice`) |
| **Event** | When to fire: After Insert / On Update / On Submit / On Cancel / On Trash |
| **Condition** | (Optional) Python expression — alert only fires if this returns `True` |
| **Message** | Jinja2 template for the Telegram message (e.g., `Invoice {{ doc.name }} has been submitted. Total: {{ doc.grand_total }}`) |
| **Telegram Keyboard** | (Optional) Add inline buttons like Submit/Cancel to act on the document from Telegram |

**Message template example:**
```jinja
Hi {{ user }},
Invoice {{ doc.name }} has been created.
Customer: {{ doc.customer }}
Grand Total: {{ doc.grand_total }}
Date: {{ current_date }}
```

**Condition example:**
```python
doc.grand_total > 5000 and doc.status == "Draft"
```

### 5. Start Receiving Notifications

1. Open Telegram and find your bot (the one you created in step 1)
2. Send any message to the bot — this registers your Chat ID automatically
3. Now create/update/submit a document of the tracked DocType in Frappe
4. You'll receive a Telegram notification instantly

## How It Works

```
Frappe Doc Event (e.g., on_submit)
        │
        ▼
dynamic_notify(doc, method)
        │
        ▼
Find matching Telegram Alert Settings (doctype + event + enabled)
        │
        ▼
For each matching alert:
  ├─ Evaluate condition (if any)
  ├─ Render message template (Jinja2)
  ├─ Build inline keyboard (if configured)
  └─ Send to Telegram Bot API
```

When you press an inline keyboard button in Telegram, the webhook receives the callback and performs the action (submit/cancel the document).

## Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/notification_management
pre-commit install
```

Pre-commit is configured to use the following tools:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app uses GitHub Actions for CI:

- **CI** — Installs the app and runs unit tests on every push to `develop`
- **Linters** — Runs Frappe Semgrep Rules and pip-audit on every pull request

## License

MIT
