from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import flt, getdate, nowdate, add_to_date
from datetime import datetime  

def validate_quotation_cost_section(self, method):
  
    # calculate visit hours
    no_of_hours_in_a_month = frappe.db.get_single_value('Russeell Setting', 'no_of_hours_in_a_month')

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
         row.overtime_hour_total_cost = flt((row.qty * (row.overtime_per_hour or 0)),2) + flt(self.custom_overtime_hours)
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
    admin_fees = frappe.db.get_single_value('Russeell Setting', 'admin_fees_percentage')
    sub_total = (self.custom_man_power_grand_total 
    + self.custom_consumption_tools_grand_total 
    + self.custom_equipment_grand_total 
    + self.custom_vehicle_grand_total
    + self.custom_other_cost_grand_total)

    self.custom_sub_grand_total = sub_total
    self.custom_admin_fees = (sub_total * (admin_fees or 0)) / 100

    # calculate estimated cost
    self.custom_total_estimated_cost = sub_total + self.custom_admin_fees

    sales_markup_percentage = frappe.db.get_single_value('Russeell Setting', 'suggested_sales_markup_percentage')
    self.custom_suggested_sales_rate =((self.custom_total_estimated_cost * (sales_markup_percentage or 0)) / 100)+self.custom_total_estimated_cost


def check_contact_end_date(self, method):
    # Advance-Monthy
    if self.custom_billing_type == 'Advance-Monthy':
        monthy_end_dates = ''
        slot_date = self.custom_contract_start_date
        while monthy_end_dates < self.custom_contract_end_date:
                    monthy_end_dates = add_to_date(slot_date, months=1)
                    slot_date = monthy_end_dates

        if add_to_date(slot_date, days=-1) != self.custom_contract_end_date:
            frappe.throw(_("Slot end date is invalid"))

    # Advance-Quaterly
    if self.custom_billing_type == 'Advance-Quaterly':
        quaterly_end_dates = ''
        slot_date = self.custom_contract_start_date
        while quaterly_end_dates < self.custom_contract_end_date:
                    quaterly_end_dates = add_to_date(slot_date, months=3)
                    slot_date = quaterly_end_dates

        if add_to_date(slot_date, days=-1) != self.custom_contract_end_date:
            frappe.throw(_("Slot end date is invalid"))

    # Advance-HalfYearly
    if self.custom_billing_type == 'Advance-HalfYearly':
        halfyearly_end_dates = ''
        slot_date = self.custom_contract_start_date
        while halfyearly_end_dates < self.custom_contract_end_date:
                    halfyearly_end_dates = add_to_date(slot_date, months=6)
                    slot_date = halfyearly_end_dates

        if add_to_date(slot_date, days=-1) != self.custom_contract_end_date:
            frappe.throw(_("Slot end date is invalid"))

    # Advance-Yearly
    if self.custom_billing_type == 'Advance-Yearly':
        yearly_end_dates = ''
        slot_date = self.custom_contract_start_date
        while yearly_end_dates < self.custom_contract_end_date:
                    yearly_end_dates = add_to_date(slot_date, years=1)
                    slot_date = yearly_end_dates

        if add_to_date(slot_date, days=-1) != self.custom_contract_end_date:
            frappe.throw(_("Slot end date is invalid"))
    
def validate_so_billing_period(self, method):
    print('validate_so_billing_period------')
    start_date = self.custom_contract_start_date
    if start_date != None and self.custom_contract_end_date != None:
        # print(start_date, '---start_date')

        # Advance-Onetime
        if self.custom_billing_type == 'Advance-Onetime':
            row = self.append('custom_billing_period_slot', {})
            row.slot_start_date = start_date
            row.slot_end_date = self.custom_contract_end_date

        # Advance-Monthy
        if self.custom_billing_type == 'Advance-Monthy':
            monthy_end_dates = []
            slot_date = start_date
            while slot_date <= self.custom_contract_end_date:
                slot_end_date = add_to_date(slot_date, months=1)
                monthy_end_dates.append(slot_end_date)
                slot_date = slot_end_date
            print(monthy_end_dates, '-----monthy_end_dates')

            slot_start_date = start_date
            for slot in monthy_end_dates:
                if slot <= self.custom_contract_end_date:
                    row = self.append('custom_billing_period_slot', {})
                    row.slot_start_date = slot_start_date
                    row.slot_end_date = add_to_date(slot, days=-1) 
                    slot_start_date = slot

        # Advance-Quaterly
        if self.custom_billing_type == 'Advance-Quaterly':
            quaterly_end_dates = []
            slot_date = start_date
            while slot_date <= self.custom_contract_end_date:
                slot_end_date = add_to_date(slot_date, months=3)
                print(slot_date, 'slot_date',slot_end_date,'slot_end_date')
                quaterly_end_dates.append(slot_end_date)
                slot_date = slot_end_date
            print(quaterly_end_dates, '-----quaterly_end_dates')

            slot_start_date = start_date
            for slot in quaterly_end_dates:
                if slot <= self.custom_contract_end_date:
                    row = self.append('custom_billing_period_slot', {})
                    row.slot_start_date = slot_start_date
                    row.slot_end_date = slot
                    slot_start_date = add_to_date(slot, days=1) 
                
        # Advance-HalfYearly
        if self.custom_billing_type == 'Advance-HalfYearly':
            halfyearly_end_dates = []
            slot_date = start_date
            while slot_date <= self.custom_contract_end_date:
                slot_end_date = add_to_date(slot_date, months=6)
                halfyearly_end_dates.append(slot_end_date)
                slot_date = slot_end_date
            print(halfyearly_end_dates, '-----halfyearly_end_dates')

            slot_start_date = start_date
            for slot in halfyearly_end_dates:
                if slot <= self.custom_contract_end_date:
                    row = self.append('custom_billing_period_slot', {})
                    row.slot_start_date = slot_start_date
                    row.slot_end_date = slot
                    slot_start_date = add_to_date(slot, days=1)

        # Advance-Yearly
        if self.custom_billing_type == 'Advance-Yearly':
            yearly_end_dates = []
            slot_date = start_date
            while slot_date <= self.custom_contract_end_date:
                slot_end_date = add_to_date(slot_date, years=1)
                yearly_end_dates.append(slot_end_date)
                slot_date = slot_end_date
            print(yearly_end_dates, '-----yearly_end_dates')

            slot_start_date = start_date
            for slot in yearly_end_dates:
                if slot <= self.custom_contract_end_date:
                    row = self.append('custom_billing_period_slot', {})
                    row.slot_start_date = slot_start_date
                    row.slot_end_date = slot
                    slot_start_date = add_to_date(slot, days=1)
                       
    # today = getdate(nowdate())
    # after_10_days = add_to_date(today, days=10, as_string=True)
    # print(after_10_days, '------after_10_days')
    # after_2_month = add_to_date(datetime.now(), months=2)
    # print(after_2_month, '---------after_2_month') 

# will use when we auto create si    
def get_si_validity_range(self):
    so = self.items[0].sales_order
    visit_list = frappe.db.get_all('Visit CD',
                              filters={'sales_order':so, 
                                       'visit_date': ('between', [self.custom_slot_start_date, self.custom_slot_end_date])},
                                fields=['name','sales_invoice_reference', 'visit_status'])
    
    for visit in visit_list:
        if visit.visit_status == "Completed" or visit.visit_status == "Customer Cancelled":
            visit.sales_invoice_reference = self.name
            visit.save()

def get_no_of_visits_in_a_slot(self):
    frappe.db.count('Visit CD', filters={'sales_invoice_reference':self.name})

@frappe.whitelist()
def get_default_warehouse_for_consumed_item(item_code,company):
    from erpnext.stock.get_item_details import get_item_warehouse
    item=frappe._dict({'name':item_code,'company':company})
    default_warehouse = get_item_warehouse(item,item,None,None)
    return default_warehouse

@frappe.whitelist()
def make_visit_plan(sale_order, customer, address, no_of_visit, contact_person):
    visit_plan = frappe.new_doc("Visit Plan CD")
    visit_plan.date = frappe.utils.nowdate(),
    visit_plan.sales_order =  sale_order,
    visit_plan.customer = customer

    if contact_person == '':
        visit_plan.contact_person = ''
    else:
        visit_plan.contact_person = contact_person,
    
    if address == '':
        visit_plan.customer_address = ''
    else:
        visit_plan.customer_address = address
   
    visit_plan.save(ignore_permissions=True)

    so_items = frappe.db.get_list("Sales Order Item", parent_doctype="Sales Order", filters={'parent': sale_order},fields=['item_code', 'item_name'],)

    for visit in range(int(no_of_visit)):
        visit = frappe.new_doc("Visit CD")
        visit.visit_plan_reference = visit_plan.name
        visit.customer_name = customer
        visit.contact_person = visit_plan.contact_person
        visit.customer_address =  visit_plan.customer_address
        visit.sales_order = visit_plan.sales_order

        for item in so_items:
            visit.append("service_list",{"item_code": item.item_code, "item_name":item.item_name})
        visit.save(ignore_permissions=True)
        frappe.msgprint(_("Visit {0} is created").format(visit.name), alert=True)

    visit_details = frappe.db.get_list("Visit CD", filters={'visit_plan_reference': visit_plan.name}, fields=['name'], order_by="creation asc")

    for vp in visit_details:
        visit_plan.append("visit_table",{"visit_no": vp.name})
        visit_plan.save(ignore_permissions=True)
    frappe.msgprint(_("Visit Plan {0} is created").format(visit_plan.name), alert=True)

    return visit_plan, visit
    # return visit_plan.name