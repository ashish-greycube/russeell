frappe.ui.form.on("Sales Order", {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold" && frm.doc.custom_billing_period_slot.length > 0 && frm.doc.custom_visit_plan) {
            frm.remove_custom_button('Update Items');
            frm.add_custom_button(__("Update Items (visits)"), () => update_items_and_create_visit(frm)).css({ 'background-color': '#52c4e6', 'color': 'white' })
        }
        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold" && frm.doc.custom_total_no_of_visits !== 0 && frm.doc.custom_visit_plan === undefined) {
            frm.add_custom_button(__("Visit Plan"), () => {
                make_visit_pan(frm)
            }
                , __("Create")
            );
        }

        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold"
            && frm.doc.custom_billing_period_slot.length > 0
            && frm.doc.custom_billing_period_slot[0].no_of_visits > 0
            && !frm.doc.custom_billing_period_slot[0].sales_invoice_ref
            && frm.doc.custom_billing_type
            && frm.doc.custom_billing_type != "Rear-Monthly"
            && frm.doc.custom_billing_type != "Rear-Quaterly"
            && frm.doc.custom_billing_type != "Rear-HalfYearly") {

            frm.add_custom_button(__("Initial Sales Invoice"), () => {
                frappe.db.get_list('Visit CD', {
                    fields: ['planned_visit_date', 'name'],
                    filters: {
                        sales_order: frm.doc.name
                    }
                }).then(records => {
                    let visit_date = []
                    records.forEach(visit => {
                        if (!visit.planned_visit_date && visit.additional_visit == 0) {
                            visit_date.push(visit.name)
                        }
                    });
                    if (visit_date.length > 0) {
                        frappe.throw(__('please add planned visit date in all visits'))
                    }
                    else {
                        make_sales_invoice(frm)
                    }
                })
            }).css({ 'background-color': '#52c4e6', 'color': 'white' });

        }

        if (frm.doc.docstatus == 1 && frm.doc.custom_visit_plan) {
            frm.add_custom_button(__("Renew Contract"), () => {
                frm.trigger('create_renew_contract')
            });
        }
    },

    onload: function (frm) {
        console.log("Helloooo")
        if (frm.doc.items.length > 0) {
            console.log("Set Query!!!")
            frm.set_query('item', 'custom_cost_center_details', () => {
                return {
                    query: "russeell.api.get_service_item",
                    filters: {
                        parent: frm.doc.name
                    }
                };
            })
        }
    },

    create_renew_contract: function (frm) {
        console.log("Helloo")
        dialog = new frappe.ui.Dialog({
            title: __("Renew Contract"),
            fields: [
                {
                    fieldtype: 'Date',
                    fieldname: 'contract_start_date',
                    label: __('Contract Start Date'),
                    reqd: 1
                },
                {
                    fieldtype: 'Select',
                    fieldname: 'contract_period',
                    label: __('Contract Period'),
                    options: ["",
                        "One Time", "3 Month Contract", "Half Yearly", "Yearly",
                        "2 Year", "3 Year", "4 Year", "5 Year"],
                    reqd: 1
                },
            ],
            primary_action_label: 'Renew',
            primary_action: function (values) {
                console.log(values)
                frappe.call({
                    method: "russeell.api.create_so_contract_renew",
                    args: {
                        so_name: frm.doc.name,
                        contract_start_date: values.contract_start_date,
                        contract_period: values.contract_period
                    }
                })
                dialog.hide();
            }
        })
        dialog.show();
    }

})

frappe.ui.form.on("Cost Center List CT", {

    item_rate: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        if (row.item && row.item_rate) {
            frappe.call({
                method: "russeell.api.get_item_rates",
                args: {
                    item_code: row.item,
                    parent: frm.doc.name
                },
                callback: function (r) {
                    let item_rate_list = r.message
                    if (item_rate_list.includes(row.item_rate) === false) {
                        frappe.model.set_value(cdt, cdn, 'item_rate', '')
                        frappe.throw(__('You can not add item rate which is not present in item rate list {0}', [item_rate_list]))
                    }
                }
            })
        }
    }
})

frappe.ui.form.on("Billing Period Slots CT", {
    no_of_visits: function (frm, cdt, cdn) {
        console.log("change no of visit")
        let row = locals[cdt][cdn]

        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold"
            && frm.doc.custom_billing_period_slot.length > 0
            && row.no_of_visits > 0
            && !row.sales_invoice_ref
            && frm.doc.custom_billing_type) {
            if (frm.doc.custom_billing_type != "Rear-Monthly"
                && frm.doc.custom_billing_type != "Rear-Quaterly"
                && frm.doc.custom_billing_type != "Rear-HalfYearly") {
                console.log(row.slot_start_date, 'slot_start_date', frappe.datetime.get_today(), 'frappe.get_today')
                if (row.slot_start_date < frappe.datetime.get_today()) {
                    // frm.set_df_property("custom_billing_period_slot", "hidden", 0, row.name, "create_si");
                    frm.set_df_property('custom_billing_period_slot', 'hidden', 0, frm.docname, 'create_si', row.name)
                    console.log('visible button')
                    // row.add_custom_button(__("Create SI", () => {
                    //     console.log('inside button')
                    //     frappe.call({
                    //         method: "russeell.api.make_sales_invoice",
                    //         args: {
                    //             sales_order: frm.doc.name,
                    //             slot_start_date: row.slot_start_date,
                    //             slot_end_date: row.slot_end_date,
                    //             no_of_visits: row.no_of_visits
                    //         },
                    //         callback: function (r) {
                    //             console.log(r.message)
                    //         }
                    //     })
                    // }))
                }
            }
            else {
                if (row.slot_end_date < frappe.datetime.get_today()) {
                    row.add_custom_button(__("Create SI", () => {
                        frappe.call({
                            method: "russeell.api.make_sales_invoice",
                            args: {
                                sales_order: frm.doc.name,
                                slot_start_date: row.slot_start_date,
                                slot_end_date: row.slot_end_date,
                                no_of_visits: row.no_of_visits
                            },
                            callback: function (r) {
                                console.log(r.message)
                            }
                        })
                    }))
                }
            }
        }
    },

    create_si: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn]
        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold"
            && frm.doc.custom_billing_period_slot.length > 0
            && row.no_of_visits > 0
            && !row.sales_invoice_ref
            && frm.doc.custom_billing_type) {
            if (frm.doc.custom_billing_type != "Rear-Monthly"
                && frm.doc.custom_billing_type != "Rear-Quaterly"
                && frm.doc.custom_billing_type != "Rear-HalfYearly") {
                // console.log(row.slot_start_date, 'slot_start_date', frappe.datetime.get_today(), 'frappe.get_today')
                if (row.slot_start_date < frappe.datetime.get_today()) {
                    // console.log("Create SI", frm.name, cdt, cdn)
                    make_si_for_pervious_slots(frm, cdn, cdt)
                }
                else { frappe.msgprint(__('You Cann`t Create Past SI as criteria is not matched. <br> ex. existing si is present OR zero no. of visit OR no past slot dates')) }
            }
            else {
                if (row.slot_end_date < frappe.datetime.get_today()) {
                    // console.log("Create SI", frm.name, cdt, cdn)
                    make_si_for_pervious_slots(frm, cdn, cdt)
                }
                else { frappe.msgprint(__('You Cann`t Create Past SI as criteria is not matched. <br> ex. existing si is present OR zero no. of visit OR no past slot dates')) }
            }
        }
        else {
            frappe.msgprint(__('You Cann`t Create Past SI as criteria is not matched. <br> ex. existing si is present OR zero no. of visit OR no past slot dates'))
        }
    }
})

function update_items_and_create_visit(frm) {
    let dialog = undefined
    let table_fields = [
        {
            fieldtype: "Link",
            fieldname: "cost_center",
            label: __("Cost Center"),
            options: "Cost Center",
            read_only: 0,
            reqd: 1,
            in_list_view: 1,
        },
        {
            fieldtype: "Link",
            fieldname: "item_code",
            label: __("Item Code"),
            options: "Item",
            read_only: 0,
            reqd: 1,
            in_list_view: 1,
            get_query: function () {
                if (frm.doc.custom_no_of_visits > 0) {
                    return {
                        "filters": {
                            "customer": undefined,
                            "is_sales_item": 1,
                            "has_variants": 0,
                            "is_stock_item": 0
                        },
                    };
                }
                else {
                    return {
                        "filters": {
                            "customer": undefined,
                            "is_sales_item": 1,
                            "has_variants": 0
                        },
                    }
                }
            },
            onchange: function () {
                const me = this;

				frm.call({
					method: "erpnext.stock.get_item_details.get_item_details",
					args: {
						doc: frm.doc,
						args: {
							item_code: this.value,
							set_warehouse: frm.doc.set_warehouse,
							customer: frm.doc.customer,
							currency: frm.doc.currency,
							is_internal_customer: frm.doc.is_internal_customer,
							conversion_rate: frm.doc.conversion_rate,
							price_list: frm.doc.selling_price_list,
							price_list_currency: frm.doc.price_list_currency,
							plc_conversion_rate: frm.doc.plc_conversion_rate,
							company: frm.doc.company,
							order_type: frm.doc.order_type,
							ignore_pricing_rule: frm.doc.ignore_pricing_rule,
							doctype: frm.doc.doctype,
							name: frm.doc.name,
							qty: me.doc.qty || 1,
							uom: me.doc.uom,
							pos_profile: cint(frm.doc.is_pos) ? frm.doc.pos_profile : "",
							tax_category: frm.doc.tax_category,
							child_doctype: frm.doc.doctype + " Item",
						},
					},
					callback: function (r) {
						if (r.message) {
							console.log(r.message, "=======================message========")
							const { qty, price_list_rate: rate, uom, conversion_factor } = r.message;

							const row = dialog.fields_dict.visit_items.df.data.find(
								(doc) => doc.idx == me.doc.idx
							);
							if (row) {
								Object.assign(row, {
									conversion_factor: me.doc.conversion_factor || conversion_factor,
									uom: me.doc.uom || uom,
									qty: me.doc.qty || qty,
									rate: me.doc.rate || rate,
								});
								dialog.fields_dict.visit_items.grid.refresh();
							}
						}
					},
				});
            }
        },
        {
            fieldtype: "Date",
            fieldname: "delivery_date",
            label: __("Delivery Date"),
            read_only: 0,
            reqd: 1,
            in_list_view: 1
        },
        {
            fieldtype: "Int",
            fieldname: "qty",
            label: __("Qty"),
            read_only: 0,
            reqd: 1,
            in_list_view: 1,
            default: 1
        },
        {
            fieldtype: "Currency",
            fieldname: "rate",
            label: __("Rate"),
            read_only: 0,
            reqd: 1,
            in_list_view: 1,
            // fetch_from: "item_code.item_rate"
        },
        {
            fieldtype: "Link",
            fieldname: "uom",
            label: __("UOM"),
            options: "UOM",
            read_only: 0,
            reqd: 1,
            in_list_view: 1,
            // fetch_from: "item_code.stock_uom"
        },
        {
            fieldtype: "Float",
			fieldname: "conversion_factor",
			label: __("Conversion Factor"),
        },
        {
            fieldtype: "Check",
            fieldname: "is_additional_visit",
            label: __("Is Additional Visit"),
            read_only: 1,
            hidden: 1,
            default: 1,
            in_list_view: 0,
        }
    ]

    let dialog_field = [
        {
            label: "Items",
            fieldname: "visit_items",
            fieldtype: "Table",
            cannot_add_rows: false,
            cannot_delete_rows: false,
            in_place_edit: false,
            reqd: 1,
            data: [],
            get_data: () => {
                return [];
            },
            fields: table_fields,
        }
    ]

    dialog = new frappe.ui.Dialog({
        title: __("Select Cost Center Wise Items"),
        fields: dialog_field,
        primary_action_label: 'Update',
        primary_action: function (values) {
            console.log(values, "======= values=====")
            const cost_center_items = values.visit_items
            
            console.log(cost_center_items, "============cost_center_items=======")

            let items_details = values.visit_items
            frm.doc.items.forEach(item => {
                items_details.unshift(item)
            });

            frappe.call({
                method: "russeell.api.set_additional_visit_details",
                args: {
                    sales_order: frm.doc.name,
                    additional_visit_details: items_details,
                },
                callback: function (r) {
                    console.log(r.message, "==========")
                    // frm.save("Update");
                    frm.reload_doc();
                }
            })
            dialog.hide()
            refresh_field("items");
        }
    })
    dialog.show()
    dialog.$wrapper.find('.modal-content').css("width", "900px");

}

function make_visit_pan(frm) {
    frappe.call({
        method: "russeell.api.make_visit_plan",
        args: {
            sale_order: frm.doc.name,
            customer: frm.doc.customer,
            contact_person: frm.doc.contact_person || '',
            address: frm.doc.customer_address || '',
            no_of_visit: frm.doc.custom_total_no_of_visits
        },
        callback: function (r) {
            console.log(r.message)
        }
    })
}

function make_sales_invoice(frm) {
    let slot_start_date = frm.doc.custom_billing_period_slot[0].slot_start_date
    let slot_end_date = frm.doc.custom_billing_period_slot[0].slot_end_date
    let no_of_visits = frm.doc.custom_billing_period_slot[0].no_of_visits
    frappe.call({
        method: "russeell.api.make_sales_invoice",
        args: {
            sales_order: frm.doc.name,
            slot_start_date: slot_start_date,
            slot_end_date: slot_end_date,
            no_of_visits: no_of_visits
        },
        callback: function (r) {
            console.log(r.message)
        }
    })
}

function make_si_for_pervious_slots(frm, cdn, cdt) {
    let row = locals[cdt][cdn]
    frappe.call({
        method: "russeell.api.make_sales_invoice",
        args: {
            sales_order: frm.doc.name,
            slot_start_date: row.slot_start_date,
            slot_end_date: row.slot_end_date,
            no_of_visits: row.no_of_visits
        },
        callback: function (r) {
            console.log(r.message)
        }
    })
}