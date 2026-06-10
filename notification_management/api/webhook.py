import frappe
import json
from notification_management.notification_management.doctype.telegram_users_ids.telegram_users_ids import TelegramUsersIDs
from .send_notification import BotToken, send_telegram_notification


@frappe.whitelist(allow_guest=True)
def trigger_webhook():
    raw_data = frappe.local.request.get_data()
    if raw_data:
        payload = json.loads(raw_data)

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
        if self.doctype and self.dt_name and self.action:
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
        doc = frappe.get_doc(self.doctype, self.dt_name)
        if self.action == "submit":
            doc.submit()
            self.send_telegram_message(f"Doc {self.dt_name} Submitted successfully.")

        elif self.action == "cancel":
            doc.cancel()   
            self.send_telegram_message(f"Doc {self.dt_name} Cancled successfully.")


    def send_telegram_message(self, message):
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            }
        send_telegram_notification(self.bot_token, payload)


