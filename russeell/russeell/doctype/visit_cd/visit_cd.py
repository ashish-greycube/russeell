# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display
from frappe import _
from frappe.utils import getdate
from russeell.api import set_count_of_visits_in_a_slot

class VisitCD(Document):
	def on_update(self):
		self.set("address_display", get_address_display(self.customer_address))
		if self.planned_visit_date!=None or self.assign_to!=None:
			visit_plan = frappe.get_doc("Visit Plan CD", self.visit_plan_reference)
			visit_plan.run_method("set_missing_values")	
			visit_plan.save(ignore_permissions=True)
			
	def validate(self):
		if self.planned_visit_date:

			# validate planned visit date
			so_doc = frappe.get_doc('Sales Order', self.sales_order)
			planned_visit = getdate(self.planned_visit_date)
			if planned_visit < so_doc.custom_contract_start_date or planned_visit > so_doc.custom_contract_end_date:
				frappe.throw(_("Planned Visit Date Must be between {0} and {1}"
				   ).format(so_doc.custom_contract_start_date, so_doc.custom_contract_end_date))
				
			# count visit 
			changed_date = self.has_value_changed("planned_visit_date")   # will return true or false
			old_doc = self.get_doc_before_save()
			if changed_date and old_doc.planned_visit_date == None:
				set_count_of_visits_in_a_slot(self.sales_order, self.planned_visit_date)
				print("Date Change From {0} to {1}".format(changed_date, self.planned_visit_date))
			else:
				frappe.throw(_('You Cann`t Change Planned Visit Date'))

			# old_doc = self.get_doc_before_save()
			# print(old_doc.planned_visit_date, type(old_doc.planned_visit_date), '------old doc planned_visit_date')
			# if old_doc.planned_visit_date == self.planned_visit_date:
			# 	print("Date is not changed!")
			# else: 
			# 	print("Date Change From {0} to {1}".format(old_doc.planned_visit_date, self.planned_visit_date),)

			# print(self.planned_visit_date, type(old_doc.planned_visit_date), '-------new doc planned_visit_date')

		# if self.assign_to:
		# 	old_doc = self.get_doc_before_save()
		# 	if old_doc.assign_to == self.assign_to:
		# 		print("assign_to is not changed!")
		# 	else: 
		# 		print("assign_to Change From {0} to {1}".format(old_doc.assign_to, self.assign_to))