frappe.ui.form.on("Sales Order", {
    refresh: function (frm) {
        // console.log(frm.doc.custom_billing_period_slot[0].no_of_visits)
        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold" && frm.doc.custom_total_no_of_visits !== 0) {
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
                // console.log('condition!!!!!!!')
                frm.add_custom_button(__("Initial Sales Invoice"), () => {
                    make_sales_invoice(frm)
                })  
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