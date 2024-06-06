frappe.ui.form.on("Sales Order", {
    refresh: function (frm) {
        console.log(frm.doc.contact_person)
        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold" && frm.doc.custom_no_of_visits !== 0) {
            frm.add_custom_button(__("Visit Plan"), () => {
                make_visit_pan(frm)
            }
                , __("Create")
            );
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
            no_of_visit: frm.doc.custom_no_of_visits
        },
        callback: function (r) {
            console.log(r.message)
        }
    })
}