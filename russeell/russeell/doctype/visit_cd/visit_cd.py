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
		self.validate_planned_visit_date()
		self.validate_visit_status_with_si_status()

	def validate_planned_visit_date(self):
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
			elif changed_date:
				frappe.throw(_('You Cann`t Change Planned Visit Date'))
			else:
				pass

	def validate_visit_status_with_si_status(self):
		if self.visit_status == "Completed" or self.visit_status == "Customer Cancelled":
			so_doc = frappe.get_doc('Sales Order', self.sales_order)
			if so_doc.custom_billing_type != None and so_doc.custom_billing_type != "Rear-Monthly" and so_doc.custom_billing_type != "Rear-Quaterly" and so_doc.custom_billing_type != "Rear-HalfYearly":
				si = frappe.get_doc('Sales Invoice', self.sales_invoice_reference)
				if si.status != 'Paid':
					frappe.throw(_('You can`t change visit status until sales invoice not paid'))