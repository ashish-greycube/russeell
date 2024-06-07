# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class RusseellSetting(Document):
	def validate(self):
		if self.admin_fees_percentage <= 0 or self.sales_margin_percentage <= 0 or self.no_of_hours_in_a_month <= 0 or self.suggested_sales_markup_percentage <= 0:
			frappe.throw(_("values cann't be 0 or negative"))
