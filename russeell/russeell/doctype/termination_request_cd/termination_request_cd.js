// // Copyright (c) 2024, GreyCube Technologies and contributors
// // For license information, please see license.txt

frappe.ui.form.on("Termination Request CD", {
	refresh: function (frm) {
        if (frm.doc.docstatus == 1 && frm.doc.no_of_credit_note !== 0 && frm.doc.termination_sales_invoice === undefined) {
            frm.add_custom_button(__("Return/Credit Note"), () => {
                make_credit_note(frm)
            });
        }
        else if(frm.doc.docstatus == 1 && frm.doc.no_of_visits_in_si_itemqty !== 0 && frm.doc.termination_sales_invoice === undefined){
            frm.add_custom_button(__("Sales Invoice"), () => {
                make_sales_invoice(frm)
            });
        }
    }
});

function make_credit_note(frm){
    frappe.call({
        method: "russeell.russeell.doctype.termination_request_cd.termination_request_cd.make_credit_note",
        args: {
            sales_order: frm.doc.so_reference,
            slot_date: frm.doc.date,
            si_item_qty: frm.doc.no_of_actual_visits_in_si
        },
        callback: function (r) {
            if(r.message){
                frm.set_value('termination_sales_invoice', r.message)
            }
        }
    })
}

function make_sales_invoice(frm) {
    frappe.call({
        method: "russeell.russeell.doctype.termination_request_cd.termination_request_cd.make_sales_invoice",
        args: {
            sales_order: frm.doc.so_reference,
            slot_date: frm.doc.date,
            si_item_qty: frm.doc.no_of_actual_visits_in_si
        },
        callback: function (r) {
            if(r.message){
                frm.set_value('termination_sales_invoice', r.message)
            }
        }
    })
}
