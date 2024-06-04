from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import flt

def validate_quotation_cost_section(self, method):
    # calculate_man_power_cost(self, method)
    # calculate_net_total_and_grand_total(self, method)
    # calculate_visit_hours(self, method)


    # calculate visit hours
    no_of_hours_in_a_month = frappe.db.get_single_value('Rsusseel Setting', 'no_of_hours_in_a_month')

    self.custom_total_hours = (self.custom_no_of_visits or 0) * (self.custom_visit_duration_hrs or 0)

    if self.custom_total_hours >= no_of_hours_in_a_month:
        self.custom_normal_hours_without_overtime = no_of_hours_in_a_month
        self.custom_overtime_hours = self.custom_total_hours - self.custom_normal_hours_without_overtime
    else:
        self.custom_normal_hours_without_overtime = self.custom_total_hours
        self.custom_overtime_hours = ""
    
    # calculate man power cost
    grand_total = 0
    for row in self.get('custom_man_power_cost'):
         row.normal_hour_total_cost = flt((row.qty * (row.cost_per_hour or 0) * (self.custom_total_hours or 0)),2)
         row.overtime_hour_total_cost = flt((row.qty * (row.overtime_per_hour or 0)),2)
         row.net_total = flt((row.normal_hour_total_cost + row.overtime_hour_total_cost),2)
         grand_total = grand_total + row.net_total
    
    self.custom_man_power_grand_total = grand_total

    # calculate net total and grand total
    
    consumption_table_grand_total = 0
    for row in self.get('custom_consumption_table'):
        row.total_cost = flt((row.qty * (row.valuation_rate or 0)),2)
        consumption_table_grand_total = consumption_table_grand_total + row.total_cost

    self.custom_consumption_tools_grand_total =  consumption_table_grand_total

    equipment_grand_total = 0
    for row in self.get('custom_equipments_cost'):
        row.net_total = flt((row.qty * (row.cost_per_hour or 0)),2)
        equipment_grand_total = equipment_grand_total + row.net_total
    
    self.custom_equipment_grand_total = equipment_grand_total

    vehicles_grand_total = 0
    for row in self.get('custom_vehicles_cost'):
        row.net_total = flt((row.qty * (row.cost_per_hour or 0)),2)
        vehicles_grand_total = vehicles_grand_total + row.net_total
    
    self.custom_vehicle_grand_total = vehicles_grand_total

    other_cost_grand_total = 0
    for row in self.get('custom_other_cost'):
        row.net_total =flt((row.qty * (row.cost_per_hour or 0)),2)
        other_cost_grand_total = other_cost_grand_total + row.net_total
    
    self.custom_other_cost_grand_total = other_cost_grand_total

    # calculate sub_total and admin fees
    admin_fees = frappe.db.get_single_value('Rsusseel Setting', 'admin_fees_percentage')
    sub_total = (self.custom_man_power_grand_total 
    + self.custom_consumption_tools_grand_total 
    + self.custom_equipment_grand_total 
    + self.custom_vehicle_grand_total
    + self.custom_other_cost_grand_total)

    self.custom_sub_grand_total = sub_total
    self.custom_admin_fees = (sub_total * (admin_fees or 0)) / 100

    # calculate estimated cost
    self.custom_total_estimated_cost = sub_total + self.custom_admin_fees

    sales_markup_percentage = frappe.db.get_single_value('Rsusseel Setting', 'suggested_sales_markup_percentage')
    self.custom_suggested_sales_rate =((self.custom_total_estimated_cost * (sales_markup_percentage or 0)) / 100)+self.custom_total_estimated_cost

@frappe.whitelist()
def get_default_warehouse_for_consumed_item(item_code,company):
    from erpnext.stock.get_item_details import get_item_warehouse
    item=frappe._dict({'name':item_code,'company':company})
    default_warehouse = get_item_warehouse(item,item,None,None)
    return default_warehouse

@frappe.whitelist()
def make_visit_pan(sale_order, date, contact_person, address, no_of_visit):
    # print(sale_order, '------sale_order')
    visit_plan = frappe.new_doc("Visit Plan CD")
    visit_plan.date = date,
    visit_plan.sales_order =  sale_order,
    visit_plan.contact_person = contact_person,
    visit_plan.address = address

    visit_plan.save()

    so_items = frappe.db.get_list("Sales Order Item", parent_doctype="Sales Order", filters={'parent': sale_order},fields=['item_code', 'item_name'],)

    for visit in range(int(no_of_visit)):
        visit = frappe.new_doc("Visit CD")
        visit.visit_plan_reference = visit_plan.name
        for item in so_items:
            visit.append("service_list",{"item_code": item.item_code, "item_name":item.item_name})
        visit.save()
        frappe.msgprint(_("Visit {0} is created").format(visit.name), alert=True)

    visit_details = frappe.db.get_list("Visit CD", filters={'visit_plan_reference': visit_plan.name}, fields=['name'])

    for plan in visit_details:
        visit_plan.append("visit_table",{"visit_no": plan.name})
        visit_plan.save()
    frappe.msgprint(_("Visit Plan {0} is created").format(visit_plan.name), alert=True)

    return visit.name, visit_plan.name
    # return visit_plan.name