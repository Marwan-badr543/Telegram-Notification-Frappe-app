# Copyright (c) 2026, Marwan Badr and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TelegramUsersIDs(Document):
	
	@staticmethod
	def check_user_name_exists(username):
		return frappe.db.exists("Telegram Users IDs", {"username": username})

	@staticmethod
	def create_username(username, chat_id, first_name):
		telegram_user = frappe.get_doc({
			"doctype": "Telegram Users IDs",
			"username": username,
			"chat_id": chat_id,
			"first_name": first_name
		})	

		telegram_user.insert(ignore_permissions=True)

	@staticmethod
	def get_chat_id(username):
		return frappe.db.get_value("Telegram Users IDs", {"username": username}, "chat_id", as_dict=True)
		