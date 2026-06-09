# Copyright (c) 2026, Marwan Badr and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TelegramBotToken(Document):
	def validate(self):
		if not self.bot_token:
			frappe.throw("Bot Token can not be None.")
