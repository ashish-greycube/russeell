# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ManPowerCD(Document):
	
	def validate(self):
		self.calculate_cost()

	def calculate_cost(self):
		no_of_hours_in_a_month = frappe.db.get_single_value('Russeell Setting', 'no_of_hours_in_a_month')
		total_cost_per_month = 0
		for row in self.get("man_power_detail"):
			total_cost_per_month = total_cost_per_month + row.cost_per_month
		if no_of_hours_in_a_month != 0:
			total_cost_per_hour = total_cost_per_month /no_of_hours_in_a_month
		else:
			total_cost_per_hour=0

		self.total_cost_per_month = total_cost_per_month
		self.total_cost_per_hour = total_cost_per_hour