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
    },
    onload: function(frm){
        frm.set_query('item', 'tr_items', () => {
            return {
                query: "russeell.api.get_service_item",
                filters: {
                    parent : frm.doc.so_reference
                } 
            };
        })
    },
});

frappe.ui.form.on("Termination Request Items CT", {
    item: function(frm, cdt, cdn){
        let row = locals[cdt][cdn]
        frappe.db.get_doc('Sales Order', frm.doc.so_reference)
            .then(so => {
            // console.log(so)
            so.items.forEach((item) => {
                if(row.item === item.item_code){
                    frappe.model.set_value(cdt, cdn, 'item_rate', item.rate)
                }
            })
        })    
    }
})

function make_credit_note(frm){
    if(!frm.doc.cost_center){
        console.log("cost center")
        frappe.throw(__("Please Select Cost Center First"))
    }
    else{
        console.log("elsee")
        frappe.call({
            method: "russeell.russeell.doctype.termination_request_cd.termination_request_cd.make_credit_note",
            args: {
                termination_req: frm.doc.name,
                sales_order: frm.doc.so_reference,
                slot_date: frm.doc.date,
                si_item_qty: frm.doc.no_of_actual_credit_note,
                cost_center: frm.doc.cost_center
            },
            callback: function (r) {
                if(r.message){
                    console.log(r.message)
                    // frm.set_value('termination_sales_invoice', r.message)
                    // submit()
                    // frm.save()
                }
            }
        })
    }
}

function make_sales_invoice(frm) {
    if(!frm.doc.cost_center){
        console.log("cost center")
        frappe.throw(__("Please Select Cost Center First"))
    }
    else{
    frappe.call({
        method: "russeell.russeell.doctype.termination_request_cd.termination_request_cd.make_sales_invoice",
        args: {
            termination_req: frm.doc.name,
            sales_order: frm.doc.so_reference,
            slot_date: frm.doc.date,
            si_item_qty: frm.doc.no_of_actual_visits_in_si,
            cost_center: frm.doc.cost_center
        },
        callback: function (r) {
            if(r.message){
                frm.set_value('termination_sales_invoice', r.message)
            }
        }
    })
    }
}
