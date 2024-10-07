# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display
from frappe import _
from frappe.utils import getdate, nowdate
from russeell.api import set_count_of_visits_in_a_slot
from erpnext.stock.get_item_details import get_conversion_factor

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
		self.make_material_issue_stock_entry()
		self.set_actual_date_on_visit_completed()

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
		if (self.visit_status == "Completed" or self.visit_status == "Customer Cancelled") and self.sales_order:
			so_doc = frappe.get_doc('Sales Order', self.sales_order)
			if so_doc.custom_billing_type != None and so_doc.custom_billing_type != "Rear-Monthly" and so_doc.custom_billing_type != "Rear-Quaterly" and so_doc.custom_billing_type != "Rear-HalfYearly":
				si = frappe.get_doc('Sales Invoice', self.sales_invoice_reference)
				if si.status != 'Paid':
					frappe.throw(_('You can`t change visit status until sales invoice not paid'))


	def make_material_issue_stock_entry(self):
		if self.visit_status == 'Completed' and len(self.consumption) > 0 and self.stock_entry_reference == None and self.sales_order:
			so_doc = frappe.get_doc('Sales Order', self.sales_order)
			stock_entry = frappe.new_doc("Stock Entry")
			stock_entry.purpose = 'Material Issue'
			stock_entry.stock_entry_type='Material Issue'
			stock_entry.company=frappe.db.get_value('Sales Order', self.sales_order, 'company')
			stock_entry.set_stock_entry_type()

			for cm_item_data in self.consumption:
					details = frappe.db.get_value("Item", cm_item_data.get("item_code"), ["stock_uom", "name"], as_dict=1)
					row = stock_entry.append('items', {})
					row.item_code = cm_item_data.item_code
					row.qty = cm_item_data.qty
					row.s_warehouse = cm_item_data.warehouse
					row.stock_uom = details.stock_uom
					row.conversion_factor = get_conversion_factor(cm_item_data.get("item_code"), details.stock_uom).get("conversion_factor") or 1.0
					row.custom_business_unit = so_doc.custom_business_unit
					row.territory = so_doc.territory
					row.cost_center = self.cost_center
					row.custom_city = so_doc.custom_city
					row.project = so_doc.project
				
			stock_entry.set_missing_values()
			stock_entry.flags.ignore_permissions = True
			stock_entry.save()
			frappe.msgprint(_('Stock Entry {0} Created').format(stock_entry.name), alert=True)
			print(stock_entry.name, '--------stock_entry.name')
			self.stock_entry_reference = stock_entry.name
			# frappe.db.set_value('Visit CD', self.name, 'stock_entry_reference', stock_entry.name)
			return stock_entry.name
		
	def set_actual_date_on_visit_completed(self):
		if not self.actual_visit_date and self.visit_status == "Completed":
			self.actual_visit_date =  getdate(nowdate())