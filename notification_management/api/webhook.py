import frappe
import json
from notification_management.notification_management.doctype.telegram_users_ids.telegram_users_ids import TelegramUsersIDs


@frappe.whitelist(allow_guest=True)
def trigger_webhook():
    print("webhook -------------------------------")
    raw_data = frappe.local.request.get_data()
    if raw_data:
        payload = json.loads(raw_data)

        print("="*100)
        print(json.dumps(payload, indent=2))
        print("="*100)

        UserIDs.manage_user_id(payload)

    return {"status": "success"}


class UserIDs:
    @staticmethod 
    def manage_user_id(payload):
        if payload.get("message") and payload.get("message").get("from") and payload.get("message").get("chat"):
            username = payload.get("message").get("from").get("username")
            chat_id = payload.get("message").get("chat").get("id")
            first_name = payload.get("message").get("from").get("first_name")

            if not TelegramUsersIDs.check_user_name_exists(username):
                TelegramUsersIDs.create_username(username, chat_id, first_name)


class DocumentAction:
    def __init__(self, payload:dict):
        self.payload = payload
        
    def get_action_data(self):
        pass




# https://api.telegram.org/bot8758948322:AAEUsvz91GlcXCTypw7zTjy72KZ8fM9ZnJI/setWebhook?url=https://rightly-renewed-crawdad.ngrok-free.app/api/method/notification_management.api.webhook.trigger_webhook 

d = {
  "update_id": 553493981,
  "callback_query": {
    "id": "4860094627891439109",
    "from": {
      "id": 1131578960,
      "is_bot": False,
      "first_name": "\u0645\u0631\u0648\u0627\u0646",
      "username": "Marwan408",
      "language_code": "ar"
    },
    "message": {
      "message_id": 117,
      "from": {
        "id": 8758948322,
        "is_bot": True,
        "first_name": "Frappe Bot",
        "username": "marwan_frappe_bot"
      },
      "chat": {
        "id": 1131578960,
        "first_name": "\u0645\u0631\u0648\u0627\u0646",
        "username": "Marwan408",
        "type": "private"
      },
      "date": 1781021058,
      "text": "after insert\n\ndocname : ACC-SINV-2026-00011\nuser : Administrator\ncurrentdate : 2026-06-09",
      "reply_markup": {
        "inline_keyboard": [
          [
            {
              "text": "Submit",
              "callback_data": "submit:Sales Invoice:ACC-SINV-2026-00011"
            },
            {
              "text": "Cancel",
              "callback_data": "cancel:Sales Invoice:ACC-SINV-2026-00011"
            }
          ]
        ]
      }
    },
    "chat_instance": "31227151496650532",
    "data": "cancel:Sales Invoice:ACC-SINV-2026-00011"
  }
}

#############################################################

{
    "update_id": 553493896,
    "message": {
        "message_id": 29,
        "from": {
            "id": 1131578960,
            "is_bot": False,
            "first_name": "مروان",
            "username": "Marwan408",
            "language_code": "ar"
        },
        "chat": {
            "id": 1131578960,
            "first_name": "مروان",
            "username": "Marwan408",
            "type": "private"
        },
        "date": 1780662265,
        "text": "raw data"
    }
}
