# Copyright (c) 2026, Marwan Badr and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TelegramAlertSetting(Document):
	def before_validate(self):
		if self.telegram_keyboard:
			for r in self.telegram_keyboard:
				r.callback_data = frappe.scrub(r.action)
