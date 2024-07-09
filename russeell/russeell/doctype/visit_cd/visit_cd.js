// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visit Consumption Item Table CT", {
	item_code: function(frm, cdt, cdn) {
        set_default_warehouse(frm, cdt, cdn)
	},
});

let set_default_warehouse = function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    frappe.call({
        method: "russeell.api.get_default_warehouse_for_consumed_item",
        args: {
            item_code: row.item_code,
            company: frappe.defaults.get_default("company"),
        },
        callback: function (r) {
           let default_warehouse = r.message
            frappe.model.set_value(cdt, cdn, 'warehouse', default_warehouse)
           
        }
    })
}