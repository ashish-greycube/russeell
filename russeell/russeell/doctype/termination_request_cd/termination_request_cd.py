# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate
from frappe import msgprint, _

class TerminationRequestCD(Document):
	def validate(self):
		self.get_visit_status()
		self.get_no_of_credit_note_for_advance()
		self.get_no_of_visit_for_si_qty_rear()
		# self.set_status_of_visit_and_visit_plan_for_advance()
		# self.set_status_of_visit_and_visit_plan_for_rear()

	def on_submit(self):
		self.set_status_of_visit_and_visit_plan_for_advance()
		self.set_status_of_visit_and_visit_plan_for_rear()

	def get_visit_status(self):
		no_of_visit_done = frappe.db.count('Visit CD', 
									 {'sales_order': self.so_reference, 'visit_status': ['in', ['Completed', 'Customer Cancelled']]})
		self.no_of_visit_done = no_of_visit_done

		no_of_pending_visit = frappe.db.count('Visit CD', 
										{'sales_order': self.so_reference, 'visit_status': ['not in', ['Completed', 'Customer Cancelled']]})
		self.no_of_pending_visit = no_of_pending_visit


#### For Advance Billing Payment Type
	def get_no_of_credit_note_for_advance(self):

		so_doc = frappe.get_doc('Sales Order', self.so_reference)

		if so_doc.custom_billing_type == None or so_doc.custom_billing_type == "Rear-Monthly" or so_doc.custom_billing_type == "Rear-Quaterly" or so_doc.custom_billing_type == "Rear-HalfYearly":
			print("inside if condition")
		else:
			# print(so_doc.custom_billing_type, 'so_doc.custom_billing_type')
			slot_start_date = ""
			slot_end_date = ""
			print('inside else consition')
			for billing_slot in so_doc.custom_billing_period_slot:
				if billing_slot.slot_start_date <= getdate(self.date) and billing_slot.slot_end_date >= getdate(self.date):

					######## validate slot dates ##########
					if not billing_slot.sales_invoice_ref and not billing_slot.sales_invoice_ref_1 and not billing_slot.sales_invoice_ref_2 and not billing_slot.sales_invoice_ref_3:
						frappe.throw(_("You cannot create Termination Request for {0} date as there is no Sales Invoice created for this billing slot").format(self.date))

					slot_start_date = billing_slot.slot_start_date
					slot_end_date = billing_slot.slot_end_date
					break

			if slot_start_date == "":
				frappe.throw(_("There is no contract exists for {0} date").format(self.date))
			print(slot_start_date, '---outside if')
			visit_count = frappe.db.count('Visit CD', filters={'sales_order': so_doc.name,
															'planned_visit_date': ['between', [slot_start_date, slot_end_date]],
															'visit_status': ['not in', ['Completed', 'Customer Cancelled']]})
			self.no_of_credit_note = visit_count
			self.fill_item_table_for_advance_billing(slot_start_date, slot_end_date)
			print(visit_count, '--visit_count advance')

	def fill_item_table_for_advance_billing(self, slot_start_date, slot_end_date):
		if slot_start_date and slot_end_date and len(self.tr_items) < 1:
			visit_list = frappe.db.get_all('Visit CD', filters={'sales_order': self.so_reference,
															'planned_visit_date': ['between', [slot_start_date, slot_end_date]],
															'visit_status': ['not in', ['Completed', 'Customer Cancelled']]},
															fields=['name', 'sales_invoice_reference'])
			
			if len(visit_list) > 0:
				for visit in visit_list:
					visit_doc = frappe.get_doc('Visit CD', visit.name)
					if len(visit_doc.service_list) > 0:
						for item in visit_doc.service_list:
							row = self.append('tr_items', {})
							row.item = item.item_code
							row.item_name = item.item_name
							row.qty = 1
							row.item_rate = item.rate
							row.sales_invoice_ref = visit_doc.sales_invoice_reference


	def set_status_of_visit_and_visit_plan_for_advance(self):
		so_doc = frappe.get_doc('Sales Order', self.so_reference)

		if so_doc.custom_billing_type == None or so_doc.custom_billing_type == "Rear-Monthly" or so_doc.custom_billing_type == "Rear-Quaterly" or so_doc.custom_billing_type == "Rear-HalfYearly":
			print("inside if condition")
		else:
			# print(so_doc.custom_billing_type, 'so_doc.custom_billing_type')
			slot_start_date=""
			custom_contract_end_date=""
			for billing_slot in so_doc.custom_billing_period_slot:
				if billing_slot.slot_start_date <= getdate(self.date) and billing_slot.slot_end_date >= getdate(self.date):

					print(billing_slot.no_of_visits, '---no_of_visits')
					slot_start_date = billing_slot.slot_start_date
					custom_contract_end_date = so_doc.custom_contract_end_date
					break
			
			if slot_start_date == "":
				frappe.throw(_("There is no contract exists for {0} date").format(self.date))

			visit_list = frappe.db.get_all('Visit CD', filters={'sales_order': so_doc.name,
															'planned_visit_date': ['between', [slot_start_date, custom_contract_end_date]],
															'visit_status': ['not in', ['Completed', 'Customer Cancelled']]},
															fields=['name', 'visit_status', 'visit_plan_reference'])

			if visit_list:
				for visit in visit_list:
					print(visit.name, 'visit.name advance')
					frappe.db.set_value('Visit CD', visit.name, 'visit_status', 'Terminated')
					
				frappe.db.set_value('Visit Plan CD', visit_list[0].visit_plan_reference, 'contract_status', 'Terminated')
			
#### For Rear Billing Payment Type

	def get_no_of_visit_for_si_qty_rear(self):

		so_doc = frappe.get_doc('Sales Order', self.so_reference)

		if so_doc.custom_billing_type == "Rear-Monthly" or so_doc.custom_billing_type == "Rear-Quaterly" or so_doc.custom_billing_type == "Rear-HalfYearly":
			# print(so_doc.custom_billing_type, 'so_doc.custom_billing_type')
			slot_start_date=""
			slot_end_date=""
			for billing_slot in so_doc.custom_billing_period_slot:
				if billing_slot.slot_start_date <= getdate(self.date) and billing_slot.slot_end_date >= getdate(self.date):

					print(billing_slot.no_of_visits, '---no_of_visits')
					slot_start_date = billing_slot.slot_start_date
					slot_end_date = billing_slot.slot_end_date
					print(slot_start_date, slot_end_date, '------dates')
					break

			if slot_start_date == "":
				frappe.throw(_("There is no contract exists for {0} date").format(self.date))

			no_of_completed_visit = frappe.db.count('Visit CD', 
											{'sales_order': so_doc.name, 
											'planned_visit_date': ['between', [slot_start_date, slot_end_date]],
											'visit_status': ['in', ['Completed', 'Customer Cancelled']]})
					
			print(no_of_completed_visit, 'no_of_completed_visit rear')
			self.no_of_visits_in_si_itemqty = no_of_completed_visit

			print('get_no_of_visit_for_si_qty_rear')

	def set_status_of_visit_and_visit_plan_for_rear(self):
		so_doc = frappe.get_doc('Sales Order', self.so_reference)

		if so_doc.custom_billing_type == "Rear-Monthly" or so_doc.custom_billing_type == "Rear-Quaterly" or so_doc.custom_billing_type == "Rear-HalfYearly":
			# print(so_doc.custom_billing_type, 'so_doc.custom_billing_type')
			slot_start_date=""
			custom_contract_end_date=""
			for billing_slot in so_doc.custom_billing_period_slot:
				if billing_slot.slot_start_date <= getdate(self.date) and billing_slot.slot_end_date >= getdate(self.date):

					print(billing_slot.no_of_visits, '---no_of_visits rear')
					slot_start_date = billing_slot.slot_start_date
					custom_contract_end_date = so_doc.custom_contract_end_date
					break

			if slot_start_date == "":
				frappe.throw(_("There is no contract exists for {0} date").format(self.date))

			visit_list = frappe.db.get_all('Visit CD', filters={'sales_order': so_doc.name,
															'planned_visit_date': ['between', [slot_start_date, custom_contract_end_date]],
															'visit_status': ['not in', ['Completed', 'Customer Cancelled']]},
															fields=['name', 'visit_status', 'visit_plan_reference'])
			print(visit_list, '---visit_list rear')
			if len(visit_list) > 0:
				for visit in visit_list:
					frappe.db.set_value('Visit CD', visit.name, 'visit_status', 'Terminated')
					
				frappe.db.set_value('Visit Plan CD', visit_list[0].visit_plan_reference, 'contract_status', 'Terminated')

		print('set_status_of_visit_and_visit_plan_for_rear')

@frappe.whitelist()
def make_sales_invoice(sales_order, slot_date, si_item_qty, termination_req, cost_center):
	termination = frappe.get_doc('Termination Request CD', termination_req)
	# print(sales_order, slot_date, si_item_qty)
	doc = frappe.get_doc('Sales Order', sales_order)
	si = frappe.new_doc("Sales Invoice")
	si.customer = doc.customer
	si.due_date = nowdate()
	si.custom_business_unit = doc.custom_business_unit
	si.cost_center = cost_center
	si.custom_city = doc.custom_city
	si.territory = doc.territory
	si.project = doc.project

	# si.custom_slot_start_date = getdate(slot_start_date)
	# si.custom_slot_end_date = getdate(slot_end_date)
	cost_center_doc = frappe.get_doc("Cost Center", cost_center)
	for item in termination.tr_items:
		row = si.append('items', {})
		row.item_code = item.item
		print(item.amount)
		row.qty = item.qty
		row.rate = flt((item.item_rate),2)
		# print(row.qty, row.rate)
		row.sales_order = sales_order
		# row.so_detail=item.name
		row.cost_center=cost_center
		row.custom_business_unit=cost_center_doc.custom_business_unit or ''
		row.territory=cost_center_doc.custom_territory
		row.custom_city=cost_center_doc.custom_city

	si.run_method("set_missing_values")
	si.run_method("calculate_taxes_and_totals")
	si.run_method("set_payment_schedule")
	si.run_method("set_po_nos")
	si.run_method("set_use_serial_batch_fields")

	si.submit()

	print(si.name, '---si.name')
	frappe.db.set_value('Sales Order', doc.name, 'status', 'Closed')
	frappe.db.set_value('Termination Request CD', termination.name, 'termination_sales_invoice', si.name)
	# termination.update({'termination_sales_invoice': si.name})
	frappe.msgprint(_("Sales Invoice {0} Created").format(si.name), alert=True)

	return si.name

@frappe.whitelist()
def make_credit_note(termination_req, sales_order, slot_date, si_item_qty, cost_center):
	termination = frappe.get_doc('Termination Request CD', termination_req)

	unique_si_ref = []
	for si in termination.tr_items:
		if si.sales_invoice_ref not in unique_si_ref:
			unique_si_ref.append(si.sales_invoice_ref)

	# print(unique_si_ref, "==============unique_si_ref=============")

	if len(unique_si_ref) > 0:
		credit_notes = []
		for si_ref in unique_si_ref:
			si = _make_credit_note(termination_req, sales_order, slot_date, si_item_qty, cost_center, si_ref)
			credit_notes.append(si)

		# print(credit_notes, "============credit_notes=================")
		frappe.db.set_value('Sales Order', sales_order, 'status', 'Closed')
		frappe.db.set_value('Termination Request CD', termination.name, 'termination_sales_invoice', ", ".join((ele if ele!=None else '') for ele in credit_notes))
		frappe.msgprint(_("Credit Notes {0} Created").format(", ".join((ele if ele!=None else '') for ele in credit_notes)), alert=True)

@frappe.whitelist()
def _make_credit_note(termination_req, sales_order, slot_date, si_item_qty, cost_center, si_ref):
	doc = frappe.get_doc('Sales Order', sales_order)
	termination = frappe.get_doc('Termination Request CD', termination_req)

	si = frappe.new_doc("Sales Invoice")
	si.customer = doc.customer
	si.due_date = nowdate()
	si.custom_business_unit = doc.custom_business_unit
	si.cost_center = cost_center
	si.custom_city = doc.custom_city
	si.territory = doc.territory
	si.project = doc.project
	si.is_return=1

	for billing_slot in doc.custom_billing_period_slot:
		if billing_slot.slot_start_date <= getdate(slot_date) and billing_slot.slot_end_date >= getdate(slot_date):
				main_si_ref = billing_slot.sales_invoice_ref

	si.return_against=si_ref,
	cost_center_doc = frappe.get_doc("Cost Center", cost_center)
	for item in termination.tr_items:
		if item.sales_invoice_ref == si_ref or (item.sales_invoice_ref == None and si_ref == main_si_ref):
			row = si.append('items', {})
			row.item_code = item.item
			row.rate = flt((item.item_rate),2)
			row.qty = -int(item.qty)
			# print(-int(si_item_qty) , '----int(si_item_qty)')
			row.sales_order = sales_order
			# row.so_detail=item.name
			row.cost_center=cost_center
			row.custom_business_unit=cost_center_doc.custom_business_unit or ''
			row.territory=cost_center_doc.custom_territory
			row.custom_city=cost_center_doc.custom_city
			# row.asset = "ACC-ASS-2024-00001" or ""
		# print(sales_order, slot_date, si_item_qty)

	si.submit()

	# print(si.name, '---si.name')
	
	# termination.update({'termination_sales_invoice': si.name})
	# frappe.msgprint(_("Sales Invoice {0} Created").format(si.name), alert=True)
	return si.name