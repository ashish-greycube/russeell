# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display

class VisitCD(Document):
	def validate(self):
		print(self.name,self.visit_plan_reference and (self.visit_date or self.assign_to),self.visit_plan_reference ,self.visit_date , self.assign_to)
		self.set("address_display", get_address_display(self.customer_address))
		if self.visit_date!=None or self.assign_to!=None:
			visit_plan = frappe.get_doc("Visit Plan CD", self.visit_plan_reference)
			visit_plan.run_method("set_missing_values")	
			visit_plan.save(ignore_permissions=True)
