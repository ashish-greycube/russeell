# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display

class VisitPlanCD(Document):
	def validate(self):
		self.set("address_display", get_address_display(self.customer_address))
