frappe.ui.form.on("Sales Order", {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold" && frm.doc.custom_total_no_of_visits !== 0 && frm.doc.custom_visit_plan === undefined) {
            frm.add_custom_button(__("Visit Plan"), () => {
                make_visit_pan(frm)
            }
                , __("Create")
            );
        }

        if(frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold" 
            && frm.doc.custom_billing_period_slot.length > 0
            && frm.doc.custom_billing_period_slot[0].no_of_visits > 0 
            && !frm.doc.custom_billing_period_slot[0].sales_invoice_ref
            && frm.doc.custom_billing_type
            && frm.doc.custom_billing_type != "Rear-Monthly"
            && frm.doc.custom_billing_type != "Rear-Quaterly"
            && frm.doc.custom_billing_type != "Rear-HalfYearly"){
                
                frm.add_custom_button(__("Initial Sales Invoice"), () => {
                    frappe.db.get_list('Visit CD', {
                        fields: ['planned_visit_date', 'name'],
                        filters: {
                            sales_order: frm.doc.name
                        }
                    }).then(records => {
                        let visit_date=[]
                        records.forEach(visit => {
                            if (!visit.planned_visit_date){
                                visit_date.push(visit.name)
                            }
                        });
                        if(visit_date.length > 0){
                            frappe.throw(__('please add planned visit date in all visits'))
                        }
                        else{
                            make_sales_invoice(frm)
                        }
                    })
                }).css({'background-color':'#52c4e6','color':'white'});

            }

        if (frm.doc.docstatus == 1 && frm.doc.custom_visit_plan){
            frm.add_custom_button(__("Renew Contract"),() => {
					frm.trigger('create_renew_contract')
            });
        }
    },

    create_renew_contract: function(frm){
        console.log("Helloo")
        dialog = new frappe.ui.Dialog({
            title: __("Renew Contract"),
            fields: [
                {
                    fieldtype:'Date',
                    fieldname:'contract_start_date',
                    label: __('Contract Start Date'),
                    reqd: 1
                },
                {
                    fieldtype:'Select',
                    fieldname:'contract_period',
                    label: __('Contract Period'),
                    options:["",
                        "One Time", "3 Month Contract","Half Yearly","Yearly",
                        "2 Year", "3 Year", "4 Year", "5 Year"],
                    reqd: 1
                },
            ],
            primary_action_label: 'Renew',
            primary_action: function (values) {
                console.log(values)
                frappe.call({
                    method:"russeell.api.create_so_contract_renew",
                    args: {
                        so_name:frm.doc.name,
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

frappe.ui.form.on("Billing Period Slots CT", {
    no_of_visits: function(frm, cdt, cdn) {
        console.log("change no of visit")
        let row = locals[cdt][cdn]

        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold" 
            && frm.doc.custom_billing_period_slot.length > 0
            && row.no_of_visits > 0 
            && !row.sales_invoice_ref
            && frm.doc.custom_billing_type){
            if(frm.doc.custom_billing_type!= "Rear-Monthly"
                && frm.doc.custom_billing_type != "Rear-Quaterly"
                && frm.doc.custom_billing_type != "Rear-HalfYearly"){
                    console.log(row.slot_start_date, 'slot_start_date', frappe.datetime.get_today(), 'frappe.get_today')
                    if(row.slot_start_date < frappe.datetime.get_today()){
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
            else{
                if(row.slot_end_date  < frappe.datetime.get_today()){
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

    create_si: function(frm,cdt, cdn){
        let row = locals[cdt][cdn]
        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold" 
            && frm.doc.custom_billing_period_slot.length > 0
            && row.no_of_visits > 0 
            && !row.sales_invoice_ref
            && frm.doc.custom_billing_type){
                if(frm.doc.custom_billing_type!= "Rear-Monthly"
                    && frm.doc.custom_billing_type != "Rear-Quaterly"
                    && frm.doc.custom_billing_type != "Rear-HalfYearly"){
                        // console.log(row.slot_start_date, 'slot_start_date', frappe.datetime.get_today(), 'frappe.get_today')
                        if(row.slot_start_date < frappe.datetime.get_today()){
                            // console.log("Create SI", frm.name, cdt, cdn)
                            make_si_for_pervious_slots(frm, cdn, cdt)
                        }
                        else{frappe.msgprint(__('You Cann`t Create Past SI as criteria is not matched. <br> ex. existing si is present OR zero no. of visit OR no past slot dates'))}
                    }
                else{
                    if(row.slot_end_date  < frappe.datetime.get_today()){
                        // console.log("Create SI", frm.name, cdt, cdn)
                        make_si_for_pervious_slots(frm, cdn, cdt)
                    }
                    else{frappe.msgprint(__('You Cann`t Create Past SI as criteria is not matched. <br> ex. existing si is present OR zero no. of visit OR no past slot dates'))}
                }
            }
        else{
            frappe.msgprint(__('You Cann`t Create Past SI as criteria is not matched. <br> ex. existing si is present OR zero no. of visit OR no past slot dates'))
        }
    }
})

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

function make_si_for_pervious_slots(frm, cdn, cdt){
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