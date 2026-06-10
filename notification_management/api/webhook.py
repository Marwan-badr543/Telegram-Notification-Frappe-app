import frappe
import json
from notification_management.notification_management.doctype.telegram_users_ids.telegram_users_ids import TelegramUsersIDs
from .send_notification import BotToken, send_telegram_notification


@frappe.whitelist(allow_guest=True)
def trigger_webhook():
    raw_data = frappe.local.request.get_data()
    if raw_data:
        payload = json.loads(raw_data)

        # print("="*100)
        # print(json.dumps(payload, indent=2))
        # print("="*100)

        UserIDs.manage_user_id(payload)

        action = DocumentAction(payload)
        action.take_an_action()

    return {"status": "success"}


class UserIDs:
    @staticmethod 
    def manage_user_id(payload):
        if payload.get("message",{}).get("from") and payload.get("message",{}).get("chat"):
            username = payload.get("message").get("from").get("username")
            first_name = payload.get("message").get("from").get("first_name")
            chat_id = payload.get("message").get("chat").get("id")
            if not TelegramUsersIDs.check_user_name_exists(username):
                TelegramUsersIDs.create_username(username, chat_id, first_name)


class DocumentAction:
    def __init__(self, payload:dict):
        self.payload = payload
        self.bot_token = BotToken.get_bot_token()
        self.chat_id = None
        self.doctype = None
        self.dt_name = None
        self.action = None
        frappe.set_user("Administrator")
        

    def take_an_action(self):
        self._get_action_data()
        print("before if ")
        if self.doctype and self.dt_name and self.action:
          print("if executed...")
          # if self._action_applying_possibility():
          self._apply_action()


    def _get_action_data(self):
        data = self.payload.get("callback_query", {}).get("data")
        sep_data = data.split(":")
        action = sep_data[0]
        doctype = sep_data[1]
        dt_name = sep_data[2]
        self.chat_id = self.payload.get("callback_query",{}).get("message",{}).get("chat",{}).get("id")

        self.action = action
        self.doctype = doctype
        self.dt_name = dt_name


    def _action_applying_possibility(self):
        doc_status = frappe.db.get_value(self.doctype, self.dt_name, "docstatus")
        if doc_status == 1:
            self.send_telegram_message("Submitted docs Can't be updated.")
            return False
        
        doc = frappe.get_doc(self.doctype, self.dt_name)
        if not doc.meta.is_submittable and self.action == "submit":
            self.send_telegram_message(f"Doctype {self.doctype} is not submitable.")
            return False
        return True

    def _apply_action(self):
        print("in apply action")
        doc = frappe.get_doc(self.doctype, self.dt_name)
        if self.action == "submit":
            doc.submit()
            self.send_telegram_message(f"Doc {self.dt_name} Submitted successfully.")

        elif self.action == "cancel":
            doc.cancel()   
            self.send_telegram_message(f"Doc {self.dt_name} Cancled successfully.")


    def send_telegram_message(self, message):
        print("in send message")
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            }
        send_telegram_notification(self.bot_token, payload)



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
