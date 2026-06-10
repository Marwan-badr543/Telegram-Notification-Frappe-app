import frappe 
import json
import requests

logger = frappe.logger("notification_management")

def dynamic_notify(doc, method=None, *args, **kwargs):
    # event_name = method or kwargs.get("method") or kwargs.get("method_name")
    
    # if not event_name:
    #     return

    # print(f"DEBUG: dynamic_notify triggered for {doc.doctype} - {doc.name} on event: {event_name}")

    # frappe.enqueue(
    #         method="notification_management.notification_management.api.main.process_alert",
    #         queue="short",
    #         timeout=300,
    #         doctype_name=doc.doctype,
    #         doc_name=doc.name,
    #         method_name=method 
    #     )
    process_alert(doc.doctype, doc.name, method_name=method)

def process_alert(tracked_doctype, tracked_doc_name, method_name):
        tracked_doc_object = frappe.get_doc(tracked_doctype, tracked_doc_name)
        alert_docs = AlertDoc.get_alert_docs(tracked_doctype, method_name)
        if alert_docs:
            for alert_doc in alert_docs:
                send_message(alert_doc, tracked_doc_object)


class AlertDoc:
    # Explicit mapping to bridge Frappe runtime hooks with UI Select field options
    EVENT_MAPPING = {
            "after_insert": "After Insert",
            "on_update": "On Update",
            "on_submit": "On Submit",
            "on_cancel": "On Cancel",
            "on_trash": "On Trash"
        }
    @staticmethod
    def get_alert_docs(doctype_name, method):
        """
        Retrieves active Telegram Alert Configurations matching the current doctype and hook event.
        """
        # Translate the runtime hook method to the exact database UI string
        db_event_name = AlertDoc.EVENT_MAPPING.get(method, method)

        alert_names = frappe.get_all(
            "Telegram Alert Setting",
            filters={
                "tracked_doctype": doctype_name,
                "event": db_event_name,
                "enabled": 1
            },
            pluck="name"
        )
        return [frappe.get_doc("Telegram Alert Setting", name) for name in alert_names]
    

def send_message(alert_doc, tracked_doc_object):
    if alert_doc.condition:
        is_condition_met = UserCondition.evaluate_user_condition(alert_doc, tracked_doc_object)
        if not is_condition_met:
            return
        
    bot_token = BotToken.get_bot_token()
    if not bot_token:
        return
    
    chat_id = ChatID.get_chat_id(alert_doc)
    if not chat_id:
        return

    if not alert_doc.message:
        return
    message = MessageTemplate.get_formatted_message(alert_doc, tracked_doc_object)


    keyboard = InlineKeyboard.get_inline_keyboards(alert_doc, tracked_doc_object)
    if keyboard:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "reply_markup": json.dumps(keyboard)
            }
    else:
        payload = {
            "chat_id": chat_id,
            "text": message,
            }
    
    send_telegram_notification(bot_token, payload)



class ChatID:
    @staticmethod
    def get_chat_id(doc):
        if doc.chat_id:
            return doc.chat_id
        if doc.username:
            username = doc.username.strip("@")
            return ChatID._get_chat_id_using_username(username)
        frappe.log_error("Telegram Notification Skipped","Neither a Chat ID nor a username exists in this document.")
        return None

    @staticmethod
    def _get_chat_id_using_username(username):
        return frappe.db.get_value("Telegram Users IDs", {"username": username}, "chat_id")


class BotToken:
    @staticmethod
    def get_bot_token():
        bot_token = frappe.cache().get_value("telegram_bot_token")
        if not bot_token:
            bot_token = BotToken._get_bot_token_from_db()
            if bot_token:
                frappe.cache().set_value("telegram_bot_token", bot_token)    
        return bot_token

    @staticmethod
    def _get_bot_token_from_db():
        bot_token = frappe.db.get_single_value("Telegram Bot Token", "bot_token")
        if not bot_token:
            frappe.log_error("Telegram Notification Skipped","Bot token not exist in Telegram Bot Token Doctype, Please set it.")
        return bot_token


class InlineKeyboard:
    @staticmethod
    def get_inline_keyboards(doc, tracked_doc):
        if doc.telegram_keyboard:
            keyboards_list = []
            for r in doc.telegram_keyboard:
                inline_Key = {"text": r.action,
                              "callback_data": f"{r.callback_data}:{tracked_doc.doctype}:{tracked_doc.name}",
                              }
                keyboards_list.append(inline_Key)

            keyboard = {
                "inline_keyboard": [keyboards_list]
                }

            return keyboard
        return None


class UserCondition:
    @staticmethod
    def evaluate_user_condition(alert_doc, tracked_doc):
        if alert_doc.condition and ("\n" in alert_doc.condition or "\r" in alert_doc.condition):
            frappe.log_error(
                title="Telegram Alert Condition Denied",
                message=f"Alert: {alert_doc.name}\nError: Multi-line conditions are strictly prohibited."
            )
            return False        
        eval_context = {
                "doc": tracked_doc,                    
                "user": frappe.session.user,                    
                "current_date": frappe.utils.today(),                    
                "frappe": frappe._dict({       
                    "db": frappe._dict({
                        "get_value": frappe.db.get_value,
                        "exists": frappe.db.exists
                    })
                })
            }
        try:
            result = frappe.safe_eval(alert_doc.condition, None, eval_context)
            return bool(result)
        except Exception as e:
            frappe.log_error(
            title="Telegram Alert Condition Evaluation Failed",
            message=f"Alert: {alert_doc.name}\nCondition: {alert_doc.condition}\nError: {str(e)}"
            )
            return False 
        
    
class MessageTemplate:
    @staticmethod
    def get_formatted_message(doc, tracked_doc):
        message_template = doc.message
        try:
            context = {
                "doc": tracked_doc,
                "user": frappe.session.user,
                "current_date": frappe.utils.today()
            }            
            rendered_message = frappe.render_template(message_template, context)
            return rendered_message
        except Exception as e:
            frappe.log_error(
                        title="Telegram Message Rendering Failed",
                        message=f"Template: {message_template}\nError: {str(e)}"
                    )
            return message_template



def send_telegram_notification(bot_token, payload):  
    print("in send telegram notification ....")  
    print(f"bot token is {bot_token}")
    print(f"payload is {payload}")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = payload

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status() 
        return {"status": "success", "response": response.json()}
    except requests.exceptions.RequestException as e:
        frappe.log_error(message=str(e), title="Telegram Notification Error")
        return {"status": "failed", "error": str(e)}



# @frappe.whitelist(allow_guest=True)
# def send_telegram_notification(message:str):
#     bot_token = "8758948322:AAEUsvz91GlcXCTypw7zTjy72KZ8fM9ZnJI"
#     chat_id = "1131578960"
    
#     url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
#     keyboard = {
#         "inline_keyboard": [
#           [
#                 {"text": "Approve here ✅", "callback_data": "approve_request"},
#                 {"text": "Reject ❌", "callback_data": "reject_request"}
#         ]]
#     }
#     payload = {
#         "chat_id": chat_id,
#         "text": message,
#         "reply_markup": json.dumps(keyboard)
#     }
#     try:
#         response = requests.post(url, data=payload)
#         response.raise_for_status() 
#         return {"status": "success", "response": response.json()}
#     except requests.exceptions.RequestException as e:
#         frappe.log_error(message=str(e), title="Telegram Notification Error")
#         return {"status": "failed", "error": str(e)}        