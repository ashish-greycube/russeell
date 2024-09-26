from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import flt, getdate, nowdate, add_to_date
from datetime import datetime

def validate_quotation_cost_section(self, method):
  
    # calculate visit hours
    self.custom_total_no_of_visits =  (self.custom_no_of_visits or 0) * (self.custom_no_of_locations or 0)

    no_of_hours_in_a_month = frappe.db.get_single_value('Russeell Setting', 'no_of_hours_in_a_month')

    total_hours = (self.custom_total_no_of_visits or 0) * (self.custom_visit_duration_hrs or 0)

    # total_hours
    old_doc = self.get_doc_before_save()
    if old_doc and (old_doc.custom_total_hours == None or old_doc.custom_total_hours == 0):
        self.custom_total_hours = total_hours
        
    total_hours_changed = self.has_value_changed("custom_total_hours")
    if total_hours_changed and (self.custom_total_hours == 0 or self.custom_total_hours == None):
        self.custom_total_hours = total_hours

    # over-time hours
    if self.custom_total_hours and self.custom_total_hours >= no_of_hours_in_a_month:
        self.custom_normal_hours_without_overtime = no_of_hours_in_a_month
        self.custom_calculated_overtime_hours = self.custom_total_hours - self.custom_normal_hours_without_overtime
    else:
        self.custom_normal_hours_without_overtime = self.custom_total_hours
        self.custom_calculated_overtime_hours = ""
    
    # calculate man power cost
    grand_total = 0
    for row in self.get('custom_man_power_cost'):
         row.normal_hour_total_cost = flt((row.qty * (row.cost_per_hour or 0) * (self.custom_total_hours or 0)),2)
         row.overtime_hour_total_cost = flt((row.qty * (row.overtime_per_hour or 0)),2) * flt((self.custom_actual_overtime_hours or 0),2)
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
    self.custom_suggested_sales_amount =((self.custom_total_estimated_cost * (sales_markup_percentage or 0)) / 100)+self.custom_total_estimated_cost

    # validate item table

    if self.custom_quotation_type == 'Visit' or self.custom_quotation_type == 'Station':
        if len(self.items) > 1:
            frappe.throw(_('You cann`t add multiple items in Items table.'))

        default_uom = frappe.db.get_value('Item', self.items[0].item_code, 'is_stock_item')
        if default_uom == 1:
            frappe.throw(_('Only service items are allowed'))

    # print(self.custom_total_no_of_visits, '---custom_total_no_of_visits')
    # for item in self.items:
    #     if self.custom_total_no_of_visits and self.custom_total_no_of_visits > 0 and self.custom_suggested_sales_rate and self.custom_suggested_sales_rate > 0:
    #         frappe.msgprint(_("In row {0} of item table qty and rate should be {1} and {2} <br> Please check qty and rate if require")
    #                         .format(item.idx, self.custom_total_no_of_visits, flt((self.custom_suggested_sales_rate),2)))
        # if self.custom_suggested_sales_rate and self.custom_suggested_sales_rate > 0:
        #     item.rate = self.custom_suggested_sales_rate

def validate_item_rate(self, method):
    if self.custom_quotation_type == 'Visit' or self.custom_quotation_type == 'Station':
        for item in self.items:
            if self.custom_sales_qty:
                suggested_sales_rate = flt((self.custom_suggested_sales_amount / self.custom_sales_qty),2)
                if item.rate < suggested_sales_rate:
                    frappe.throw(_('Item rate cann`t be less than suggested sales rate'))
    


# Sales Order
def check_contact_end_date(self, method):

    # CSD & CED not be none & CED not less than CSD & 1 year 
    contract_start_date = self.custom_contract_start_date
    contract_end_date = self.custom_contract_end_date

    print(self.custom_billing_type, '-----self.custom_billing_type')

    if self.custom_billing_type == '':
        print('not custom_billing_type')

    if contract_start_date != None and contract_end_date != None:

        if contract_end_date < contract_start_date:
             frappe.throw(_('Contract end date must be greater than Contract start date'))

        contract_year_last_date = add_to_date(contract_start_date, years=1)
        if add_to_date(contract_year_last_date, days=-1) < contract_end_date:
            frappe.throw(_('Contract cann`t be more than a year, contract dates should be between {0} and {1}'
                           ).format(contract_start_date, add_to_date(contract_year_last_date, days=-1)))

        if self.custom_billing_type != 'Advance-Onetime':    

            month_frequency = ''
            if self.custom_billing_type == 'Advance-Monthy' or self.custom_billing_type == 'Rear-Monthly':
                month_frequency = 1

            if self.custom_billing_type == 'Advance-Quaterly' or self.custom_billing_type == 'Rear-Quaterly':
                month_frequency = 3

            if self.custom_billing_type == 'Advance-HalfYearly' or self.custom_billing_type == 'Rear-HalfYearly':
                month_frequency = 6

            if self.custom_billing_type == 'Advance-Yearly':
                month_frequency = 12

            slot_end_dates = ''
            slot_start_date = contract_start_date
            while slot_end_dates < contract_end_date:
                        slot_end_dates = add_to_date(slot_start_date, months=month_frequency)
                        slot_start_date = slot_end_dates

            last_slot_end_date = add_to_date(slot_start_date, days=-1)
            if last_slot_end_date != self.custom_contract_end_date:
                frappe.throw(_("Slot end date is invalid it should be {0}".format(last_slot_end_date)))

def validate_cost_center_table(self, method):
    if len(self.custom_cost_center_details) > 0 and self.custom_total_no_of_visits > 0:
        total_visit = 0
        for row in self.custom_cost_center_details:
            total_visit = total_visit + row.qty
        
        if total_visit != self.custom_total_no_of_visits:
            frappe.throw(_("Total of cost center qty must be equal to total no of visit"))
        
    
def set_so_billing_period_slots(self, method):

    contract_start_date = self.custom_contract_start_date
    contract_end_date = self.custom_contract_end_date

    if contract_start_date != None and contract_end_date != None:

        month_frequency = ''

        if self.custom_billing_type == 'Advance-Monthy' or self.custom_billing_type == 'Rear-Monthly':
            month_frequency = 1

        if self.custom_billing_type == 'Advance-Quaterly' or self.custom_billing_type == 'Rear-Quaterly':
            month_frequency = 3

        if self.custom_billing_type == 'Advance-HalfYearly' or self.custom_billing_type == 'Rear-HalfYearly':
            month_frequency = 6

        if self.custom_billing_type == 'Advance-Yearly':
            month_frequency = 12

        if self.custom_billing_type == 'Advance-Onetime':
            row = self.append('custom_billing_period_slot', {})
            row.slot_start_date = contract_start_date
            row.slot_end_date = contract_end_date
        else:
            monthy_end_dates = []
            slot_date = contract_start_date
            while slot_date <= contract_end_date:
                slot_end_date = add_to_date(slot_date, months=month_frequency)
                monthy_end_dates.append(slot_end_date)
                slot_date = slot_end_date
            print(monthy_end_dates, '-----monthy_end_dates')

            slot_start_date = contract_start_date
            for slot in monthy_end_dates:
                    row = self.append('custom_billing_period_slot', {})
                    row.slot_start_date = slot_start_date
                    row.slot_end_date = add_to_date(slot, days=-1) 
                    slot_start_date = slot

# will use when we auto create si    
# def get_si_validity_range(self):
#     so = self.items[0].sales_order
#     visit_list = frappe.db.get_all('Visit CD',
#                               filters={'sales_order':so, 
#                                        'planned_visit_date': ('between', [self.custom_slot_start_date, self.custom_slot_end_date])},
#                                 fields=['name','sales_invoice_reference', 'visit_status'])
    
#     for visit in visit_list:
#         if visit.visit_status == "Completed" or visit.visit_status == "Customer Cancelled":
#             visit.sales_invoice_reference = self.name
#             visit.save()

def set_count_of_visits_in_a_slot(so, planned_visit_date):
    doc = frappe.get_doc('Sales Order', so)

    for slot in doc.custom_billing_period_slot:
        visit_date = getdate(planned_visit_date)
        # print(type(slot.slot_start_date), '-----slot.slot_start_date' , type(visit_date), '-----------planned_visit_date')
        if visit_date >= slot.slot_start_date and visit_date <= slot.slot_end_date:
            print(slot.no_of_visits, '-----no_of_visits', slot.slot_start_date, '-slot_start_date', slot.slot_end_date, '--slot_end_date')
            visits = slot.no_of_visits + 1
            frappe.db.set_value('Billing Period Slots CT', slot.name, 'no_of_visits', visits)
            # print(slot.no_of_visits, '-------after increaing')
            break

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

    frappe.db.set_value('Sales Order', sale_order, 'custom_visit_plan', visit_plan.name)

    so_items = frappe.db.get_list("Sales Order Item", parent_doctype="Sales Order", filters={'parent': sale_order},fields=['item_code', 'item_name'],)

    so = frappe.get_doc("Sales Order", sale_order)

    if len(so.custom_cost_center_details) > 0:
        for cost_center in so.custom_cost_center_details:
            for visit in range(int(cost_center.qty)):
                visit = frappe.new_doc("Visit CD")
                visit.visit_plan_reference = visit_plan.name
                visit.customer_name = customer
                visit.contact_person = visit_plan.contact_person
                visit.customer_address =  visit_plan.customer_address
                visit.sales_order = visit_plan.sales_order
                visit.cost_center = cost_center.cost_center

                for item in so_items:
                    visit.append("service_list",{"item_code": item.item_code, "item_name":item.item_name})
                visit.save(ignore_permissions=True)

    visit_details = frappe.db.get_list("Visit CD", filters={'visit_plan_reference': visit_plan.name}, fields=['name'], order_by="creation asc")

    for vp in visit_details:
        visit_plan.append("visit_table",{"visit_no": vp.name})
        visit_plan.save(ignore_permissions=True)
    frappe.msgprint(_("Visit Plan {0} and {1} visits are created").format(visit_plan.name, no_of_visit), alert=True)

    return visit_plan, visit

@frappe.whitelist()
def make_sales_invoice(sales_order, slot_start_date, slot_end_date, no_of_visits):
    doc = frappe.get_doc('Sales Order', sales_order)

    si = frappe.new_doc("Sales Invoice")
    si.customer = doc.customer
    si.custom_slot_start_date = getdate(slot_start_date)
    si.custom_slot_end_date = getdate(slot_end_date)
    si.due_date = nowdate()
    si.custom_business_unit = doc.custom_business_unit
    si.cost_center = doc.cost_center
    si.custom_city = doc.custom_city
    si.territory = doc.territory
    si.project = doc.project


    visit_list = frappe.db.get_all('Visit CD', filters={'sales_order': sales_order,
                                                        'planned_visit_date': ['between', [slot_start_date, slot_end_date]]},
                                                fields=['name', 'cost_center'])
    if len(visit_list) > 0:
        
        for visit in visit_list:
            item = doc.items[0]
            row = si.append('items', {})
            row.item_code = item.item_code
            row.rate = item.rate
            # uom = frappe.db.get_value('Item', item.item_code, 'stock_uom')
            row.qty = 1
            row.sales_order = sales_order
            row.so_detail=item.name

            row.custom_business_unit = doc.custom_business_unit
            row.cost_center = visit.cost_center
            row.custom_city = doc.custom_city
            row.territory = doc.territory
            row.project = doc.project        
            # row.uom=uom
    
    # else:
    #     for item in doc.items:
    #         row = si.append('items', {})
    #         row.item_code = item.item_code
    #         row.rate = item.rate
    #         # uom = frappe.db.get_value('Item', item.item_code, 'stock_uom')
    #         row.qty = 1
    #         row.sales_order = sales_order
    #         row.so_detail=item.name

    #         row.custom_business_unit = doc.custom_business_unit
    #         row.cost_center = visit.cost_center
    #         row.custom_city = doc.custom_city
    #         row.territory = doc.territory
    #         row.project = doc.project 
   
    si.run_method("set_missing_values")
    si.run_method("calculate_taxes_and_totals")
    si.run_method("set_payment_schedule")
    si.run_method("set_po_nos")
    si.run_method("set_use_serial_batch_fields")

    si.save(ignore_permissions=True)
    print(si.name, '---si.name')
    frappe.msgprint(_("Sales Invoice {0} Created").format(si.name), alert=True)

    # add si ref in visit
    billing_slot = frappe.db.get_all('Billing Period Slots CT', filters={'slot_start_date': slot_start_date,'slot_end_date': slot_end_date,
                                                                         'parent':sales_order},
                                                                fields=['name','sales_invoice_ref'])
    
    if len(billing_slot) > 0:
        for bi_slot in billing_slot:
            frappe.db.set_value('Billing Period Slots CT', bi_slot.name, 'sales_invoice_ref', si.name)

    visit_list = frappe.db.get_all('Visit CD', filters={'sales_order': sales_order,
                                                        'planned_visit_date': ['between', [slot_start_date, slot_end_date]]},
                                                fields=['name'])

    if len(visit_list) > 0:
        
        for visit in visit_list:
            frappe.db.set_value('Visit CD', visit.name, 'sales_invoice_reference', si.name)
    doc.add_comment("Comment", "Sales Invoice {0} Created".format(si.name))
    return si.name

def create_si_for_advance_billing_type(calender_date=None):
   
    print('-------------------create_si_for_advance_billing_type----------------------')
    if calender_date==None:
        calender_date = getdate(nowdate())
    billing_period_slots_list = frappe.db.get_all('Billing Period Slots CT', parent_doctype='Sales Order',
                                                  filters={'slot_start_date': ['=',calender_date],
                                                           'sales_invoice_ref': ['=','']}, 
                                                        fields=['parent', 'slot_start_date', 'slot_end_date', 'no_of_visits'])
    print(billing_period_slots_list, '---billing_period_slots_list')

    if len(billing_period_slots_list) > 0:
        for billing_slot in billing_period_slots_list:
            print(billing_slot, '----billing_slot')

            so_list = frappe.db.get_all('Sales Order',
                                filters={'custom_billing_type': ['not in', [None, 'Rear-Monthly', 'Rear-Quaterly', 'Rear-HalfYearly']],
                                         'name': billing_slot.parent,
                                         'docstatus': 1,
                                         'status': ['not in', ['Closed', 'On Hold']]},
                                fields=['name'])
            if len(so_list) > 0:
                for so in so_list:

                    # si_item = frappe.db.get_all('Sales Invoice Item',
                    #                             parent_doctype='Sales Invoice', 
                    #                             filters={'sales_order': so.name}, fields=['parent'])
                    
                    print(so.name,'--so.name--', billing_slot.slot_start_date, '--billing_slot.slot_start_date--'
                          ,billing_slot.slot_end_date, '--billing_slot.slot_end_date--',billing_slot.no_of_visits, '--billing_slot.no_of_visits--')
                    
                    # if len(si_item) > 0 and frappe.db.exists("Sales Invoice", {"name": si_item[0].parent, 
                    #                                                            "custom_slot_start_date": billing_slot.slot_start_date}):
                    #     print('in if condition')
                    #     break
                    # else:
                    from russeell.api import make_sales_invoice
                    # print('in else condition')
                    make_sales_invoice(so.name, billing_slot.slot_start_date, billing_slot.slot_end_date, billing_slot.no_of_visits)  


def create_si_for_rear_billing_type(calender_date=None):
    print('-------------------create_si_for_rear_billing_type----------------------')
    if calender_date==None:
        calender_date = getdate(nowdate())    

    billing_period_slots_list = frappe.db.get_all('Billing Period Slots CT', parent_doctype='Sales Order',
                                                  filters={'slot_end_date': ['=',calender_date],
                                                           'sales_invoice_ref': ['=','']}, 
                                                        fields=['parent', 'slot_start_date', 'slot_end_date', 'no_of_visits'])

    if len(billing_period_slots_list) > 0:
        for billing_slot in billing_period_slots_list:

            so_list = frappe.db.get_all('Sales Order',
                                filters={'custom_billing_type': ['in', ['Rear-Monthly', 'Rear-Quaterly', 'Rear-HalfYearly']],
                                         'name': billing_slot.parent,
                                         'docstatus': 1,
                                         'status': ['not in', ['Closed', 'On Hold']]},
                                fields=['name'])
            if len(so_list) > 0:
                for so in so_list:
                    
                    from russeell.api import make_sales_invoice
                    make_sales_invoice(so.name, billing_slot.slot_start_date, billing_slot.slot_end_date, billing_slot.no_of_visits)