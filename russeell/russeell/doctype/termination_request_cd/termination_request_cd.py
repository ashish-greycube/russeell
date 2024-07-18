# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class TerminationRequestCD(Document):
	def validate(self):
		self.get_visit_status()
		# self.get_no_of_credit_note_for_advance()

	def get_visit_status(self):
		no_of_visit_done = frappe.db.count('Visit CD', {'sales_order': self.so_reference, 'visit_status': ['in', ['Completed', 'Customer Cancelled']]})
		# print(no_of_visit_done, '---no_of_visit_done--')

		self.no_of_visit_done = no_of_visit_done

		no_of_pending_visit = frappe.db.count('Visit CD', {'sales_order': self.so_reference, 'visit_status': ['not in', ['Completed', 'Customer Cancelled']]})
		# print(no_of_pending_visit, '---no_of_pending_visit--')

		self.no_of_pending_visit = no_of_pending_visit

	def get_no_of_credit_note_for_advance(self):

		print(self.so_reference, '----self.so_reference')

		so_doc = frappe.get_doc('Sales Order', self.so_reference)

		if so_doc.custom_billing_type != None or so_doc.custom_billing_type != "Rear-Monthly" or so_doc.custom_billing_type != "Rear-Quaterly" or so_doc.custom_billing_type != "Rear-HalfYearly":
			print(so_doc.custom_billing_type, 'so_doc.custom_billing_type')
			for billing_slot in so_doc.custom_billing_period_slot:
				if billing_slot.slot_start_date <= getdate(self.date):

					print(billing_slot.no_of_visits, '---no_of_visits')
					slot_start_date = billing_slot.slot_start_date
					slot_end_date = billing_slot.slot_end_date

					visit_list = frappe.db.get_all('Visit CD', filters={'sales_order': so_doc.name,
														 			'planned_visit_date': ['between', [slot_start_date, slot_end_date]],
																	'visit_status': ['not in', ['Completed', 'Customer Cancelled']]},
																	fields=['name'])
					
					print(visit_list, '---visit_list-----')

					total = len([ele for ele in visit_list if isinstance(ele, dict)])

					# for visit in visit_list:
					# 	total = frappe.db.count("Visit CD", dict(name=visit.name))
					# visit_count = frappe.db.count(visit_list)

					print(str(total), '-----visit_count')
