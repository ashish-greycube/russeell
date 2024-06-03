// Copyright (c) 2024, GreyCube Technologies and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Man Power CD", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Man Power Detail", {
    cost_per_month:function(frm, cdt, cdn){
        calculate_cost(frm,cdt,cdn)
       },
       man_power_detail_remove:function(frm, cdt, cdn){
        calculate_cost(frm,cdt,cdn)        
        }
});

let calculate_cost = function(frm,cdt,cdn){
    let total_cost_per_month = 0
    frm.doc.man_power_detail.forEach(function(cost){
        total_cost_per_month = total_cost_per_month + cost.cost_per_month
    })
    frm.set_value("total_cost_per_month", total_cost_per_month)

    frappe.db.get_single_value('Rsusseel Setting', 'admin_fees_percentage')
    .then( no_of_hours_in_a_month => {
        let total_cost_per_hour = total_cost_per_month /no_of_hours_in_a_month
        frm.set_value("total_cost_per_hour", total_cost_per_hour)
    })
}
