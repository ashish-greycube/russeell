frappe.ui.form.on("Sales Order", {
    refresh: function (frm) {
        console.log("refreshhh")
        if (frm.doc.docstatus == 1 && frm.doc.status !== "Closed" && frm.doc.status !== "On Hold") {
                    frm.add_custom_button(__("Visit Plan"),() => {
                        make_visit_pan(frm)
                    }
                    ,__("Create")
                    );
                }
    }
})

function make_visit_pan(frm) {
	frappe.call({
		method: "russeell.api.make_visit_pan",
		args: {
            sale_order: frm.doc.name,
            date: frm.doc.transaction_date,
            contact_person: frm.doc.contact_person,
            address: frm.doc.customer_address || undefined,
            no_of_visit: frm.doc.custom_no_of_visits || undefined
        },
        callback: function (r) {
            console.log(r.message)
            // window.open('/app/visit-plan-cd/' + r.message)
        }
	})    
}