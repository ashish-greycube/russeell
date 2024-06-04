import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	custom_field = {
		"Quotation": [
			{
				"fieldname":'cost_center',
				"label":"Cost Center",
				"fieldtype":'Link',
				"insert_after":'custom_payment_type',
				"options":'Cost Center',
				"is_custom_field":1,
				"is_system_generated":0,
				"read_only":0
				
            },			
			{
				"fieldname": "project",
				"label":"Project",
				"fieldtype": "Link",
				"insert_after": 'cost_center',
				"options":'Project',
				"is_custom_field":1,
				"is_system_generated":0,
				"read_only":0
			},			
		]
	}
	
	print('Add Cost Center and Project fields in Quotation.....')
	create_custom_fields(custom_field, update=True)